#!/usr/bin/env python3
"""
Centralized Error Handling System
Provides consistent error handling, logging, and recovery mechanisms across the project.
"""

import logging
import traceback
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from functools import wraps
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class TradingSystemError(Exception):
    """Base exception for trading system errors."""
    pass

class APIError(TradingSystemError):
    """Exception for API-related errors."""
    def __init__(self, message: str, api_name: str = "Unknown", status_code: Optional[int] = None):
        self.api_name = api_name
        self.status_code = status_code
        super().__init__(f"{api_name} API Error: {message}")

class DataError(TradingSystemError):
    """Exception for data-related errors."""
    pass

class FileError(TradingSystemError):
    """Exception for file operation errors."""
    pass

class ValidationError(TradingSystemError):
    """Exception for data validation errors."""
    pass

class NetworkError(TradingSystemError):
    """Exception for network-related errors."""
    pass

class ErrorHandler:
    """Centralized error handling and recovery system."""
    
    def __init__(self):
        self.error_counts = {}
        self.recovery_strategies = {}
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
    def handle_api_error(self, error: Exception, api_name: str, symbol: str = None) -> bool:
        """Handle API errors with appropriate logging and recovery."""
        error_key = f"{api_name}_{type(error).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log the error
        logger.error(f"API Error in {api_name}: {str(error)}")
        if symbol:
            logger.error(f"Failed to fetch data for symbol: {symbol}")
        
        # Check if we should switch to fallback
        if self.error_counts[error_key] >= 3:
            console.print(f"⚠️  Multiple {api_name} errors detected, switching to fallback", style="yellow")
            return False
        
        return True
    
    def handle_file_error(self, error: Exception, file_path: str, operation: str = "read") -> bool:
        """Handle file operation errors."""
        logger.error(f"File {operation} error for {file_path}: {str(error)}")
        
        if isinstance(error, FileNotFoundError):
            console.print(f"❌ File not found: {file_path}", style="red")
            return False
        elif isinstance(error, PermissionError):
            console.print(f"❌ Permission denied: {file_path}", style="red")
            return False
        else:
            console.print(f"❌ File error: {str(error)}", style="red")
            return False
    
    def handle_data_error(self, error: Exception, data_type: str) -> bool:
        """Handle data processing errors."""
        logger.error(f"Data processing error for {data_type}: {str(error)}")
        console.print(f"❌ Data error in {data_type}: {str(error)}", style="red")
        return False
    
    def handle_network_error(self, error: Exception, operation: str) -> bool:
        """Handle network-related errors."""
        logger.error(f"Network error during {operation}: {str(error)}")
        console.print(f"🌐 Network error during {operation}: {str(error)}", style="red")
        return False
    
    def retry_on_failure(self, max_retries: int = None, delay: float = None):
        """Decorator to retry operations on failure."""
        if max_retries is None:
            max_retries = self.max_retries
        if delay is None:
            delay = self.retry_delay
            
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_retries:
                            logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
                            console.print(f"🔄 Retrying {func.__name__} (attempt {attempt + 2}/{max_retries + 1})", style="yellow")
                            import time
                            time.sleep(delay)
                        else:
                            logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}")
                            raise last_exception
                            
                return None
            return wrapper
        return decorator
    
    def validate_data(self, data: Any, data_type: str, required_fields: list = None) -> bool:
        """Validate data structure and content."""
        try:
            if data is None:
                raise ValidationError(f"{data_type} data is None")
            
            if isinstance(data, dict):
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        raise ValidationError(f"Missing required fields in {data_type}: {missing_fields}")
                
                # Check for NaN or None values in critical fields
                import pandas as pd
                for field in ['price', 'market_cap', 'avg_volume']:
                    if field in data and (pd.isna(data[field]) or data[field] is None):
                        raise ValidationError(f"Invalid {field} value in {data_type}")
            
            return True
            
        except Exception as e:
            logger.error(f"Data validation error for {data_type}: {str(e)}")
            return False
    
    def safe_file_operation(self, operation: Callable, file_path: str, *args, **kwargs):
        """Safely perform file operations with error handling."""
        try:
            return operation(file_path, *args, **kwargs)
        except FileNotFoundError:
            self.handle_file_error(FileNotFoundError(f"File not found: {file_path}"), file_path)
            return None
        except PermissionError:
            self.handle_file_error(PermissionError(f"Permission denied: {file_path}"), file_path)
            return None
        except Exception as e:
            self.handle_file_error(e, file_path)
            return None
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any] = None):
        """Log error with additional context information."""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        }
        
        logger.error(f"Error occurred: {error_info}")
        
        # Create rich error display
        error_text = Text()
        error_text.append(f"Error Type: {error_info['error_type']}\n", style="red")
        error_text.append(f"Message: {error_info['error_message']}\n", style="white")
        error_text.append(f"Time: {error_info['timestamp']}", style="dim")
        
        if context:
            error_text.append("\nContext:\n", style="bold")
            for key, value in context.items():
                error_text.append(f"  {key}: {value}\n", style="dim")
        
        console.print(Panel(error_text, title="❌ Error Details", border_style="red"))
    
    def create_error_summary(self) -> Dict[str, Any]:
        """Create a summary of all errors encountered."""
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_breakdown': self.error_counts.copy(),
            'timestamp': datetime.now().isoformat()
        }
    
    def reset_error_counts(self):
        """Reset error counts for recovery."""
        self.error_counts.clear()
        console.print("✅ Error counts reset", style="green")

# Global error handler instance
error_handler = ErrorHandler()

def handle_exceptions(func: Callable) -> Callable:
    """Decorator to handle exceptions in functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            error_handler.handle_api_error(e, e.api_name)
            raise
        except FileError as e:
            error_handler.handle_file_error(e, str(e))
            raise
        except DataError as e:
            error_handler.handle_data_error(e, str(e))
            raise
        except NetworkError as e:
            error_handler.handle_network_error(e, str(e))
            raise
        except Exception as e:
            error_handler.log_error_with_context(e, {
                'function': func.__name__,
                'args': str(args),
                'kwargs': str(kwargs)
            })
            raise
    return wrapper 