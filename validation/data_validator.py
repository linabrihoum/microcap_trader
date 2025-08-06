#!/usr/bin/env python3
"""
Data Validation Manager
Integrates Pydantic validation with error handling for comprehensive data validation.
"""

import pandas as pd
import json
from typing import Dict, List, Any, Optional, Union
from decimal import Decimal
from datetime import datetime, date
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pydantic import ValidationError

from .data_models import (
    StockData, PortfolioPosition, TradeRecord, CandidateStock,
    TradingRecommendation, TradingPattern, SystemConfig, ErrorLog,
    MarketSector, TradeStatus, DataSource
)
from utilities.error_handler import error_handler, ValidationError as TradingValidationError

console = Console()

class DataValidator:
    """Comprehensive data validation manager with error handling integration."""
    
    def __init__(self):
        self.validation_errors = []
        self.validation_stats = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'error_types': {}
        }
    
    def validate_stock_data(self, data: Dict[str, Any]) -> Optional[StockData]:
        """Validate stock data with comprehensive error handling."""
        try:
            self.validation_stats['total_validations'] += 1
            
            # Pre-validation checks
            if not data:
                raise TradingValidationError("Stock data is empty")
            
            # Convert numeric fields to Decimal for precision
            numeric_fields = ['price', 'market_cap', 'pct_change_1d', 'pct_change_5d', 'score']
            for field in numeric_fields:
                if field in data and data[field] is not None:
                    try:
                        data[field] = Decimal(str(data[field]))
                    except (ValueError, TypeError):
                        raise TradingValidationError(f"Invalid numeric value for {field}: {data[field]}")
            
            # Validate and create model
            stock_data = StockData(**data)
            self.validation_stats['successful_validations'] += 1
            
            console.print(f"✅ Validated stock data for {stock_data.symbol}", style="green")
            return stock_data
            
        except ValidationError as e:
            self._handle_validation_error("StockData", data, e)
            return None
        except Exception as e:
            self._handle_validation_error("StockData", data, e)
            return None
    
    def validate_portfolio_position(self, data: Dict[str, Any]) -> Optional[PortfolioPosition]:
        """Validate portfolio position with comprehensive error handling."""
        try:
            self.validation_stats['total_validations'] += 1
            
            # Pre-validation checks
            if not data:
                raise TradingValidationError("Portfolio position data is empty")
            
            # Convert numeric fields
            numeric_fields = ['shares', 'buy_price', 'current_price', 'pnl', 'pnl_percentage']
            for field in numeric_fields:
                if field in data and data[field] is not None:
                    try:
                        data[field] = Decimal(str(data[field]))
                    except (ValueError, TypeError):
                        raise TradingValidationError(f"Invalid numeric value for {field}: {data[field]}")
            
            # Validate and create model
            position = PortfolioPosition(**data)
            self.validation_stats['successful_validations'] += 1
            
            console.print(f"✅ Validated portfolio position for {position.symbol}", style="green")
            return position
            
        except ValidationError as e:
            self._handle_validation_error("PortfolioPosition", data, e)
            return None
        except Exception as e:
            self._handle_validation_error("PortfolioPosition", data, e)
            return None
    
    def validate_trade_record(self, data: Dict[str, Any]) -> Optional[TradeRecord]:
        """Validate trade record with comprehensive error handling."""
        try:
            self.validation_stats['total_validations'] += 1
            
            # Pre-validation checks
            if not data:
                raise TradingValidationError("Trade record data is empty")
            
            # Convert numeric fields
            numeric_fields = ['shares', 'buy_price', 'sell_price', 'pnl', 'pnl_percentage', 'market_cap']
            for field in numeric_fields:
                if field in data and data[field] is not None:
                    try:
                        data[field] = Decimal(str(data[field]))
                    except (ValueError, TypeError):
                        raise TradingValidationError(f"Invalid numeric value for {field}: {data[field]}")
            
            # Convert date fields
            date_fields = ['buy_date', 'sell_date']
            for field in date_fields:
                if field in data and data[field] is not None:
                    if isinstance(data[field], str):
                        try:
                            data[field] = datetime.strptime(data[field], '%Y-%m-%d').date()
                        except ValueError:
                            raise TradingValidationError(f"Invalid date format for {field}: {data[field]}")
            
            # Validate and create model
            trade_record = TradeRecord(**data)
            self.validation_stats['successful_validations'] += 1
            
            console.print(f"✅ Validated trade record for {trade_record.symbol}", style="green")
            return trade_record
            
        except ValidationError as e:
            self._handle_validation_error("TradeRecord", data, e)
            return None
        except Exception as e:
            self._handle_validation_error("TradeRecord", data, e)
            return None
    
    def validate_candidate_stock(self, data: Dict[str, Any]) -> Optional[CandidateStock]:
        """Validate candidate stock with comprehensive error handling."""
        try:
            self.validation_stats['total_validations'] += 1
            
            # Pre-validation checks
            if not data:
                raise TradingValidationError("Candidate stock data is empty")
            
            # Convert numeric fields
            numeric_fields = ['market_cap', 'price', 'volume', 'avg_volume', 'pct_change_1d', 'pct_change_5d', 'score']
            for field in numeric_fields:
                if field in data and data[field] is not None:
                    try:
                        data[field] = Decimal(str(data[field]))
                    except (ValueError, TypeError):
                        raise TradingValidationError(f"Invalid numeric value for {field}: {data[field]}")
            
            # Validate and create model
            candidate = CandidateStock(**data)
            self.validation_stats['successful_validations'] += 1
            
            console.print(f"✅ Validated candidate stock {candidate.symbol}", style="green")
            return candidate
            
        except ValidationError as e:
            self._handle_validation_error("CandidateStock", data, e)
            return None
        except Exception as e:
            self._handle_validation_error("CandidateStock", data, e)
            return None
    
    def validate_trading_recommendation(self, data: Dict[str, Any]) -> Optional[TradingRecommendation]:
        """Validate trading recommendation with comprehensive error handling."""
        try:
            self.validation_stats['total_validations'] += 1
            
            # Pre-validation checks
            if not data:
                raise TradingValidationError("Trading recommendation data is empty")
            
            # Convert numeric fields
            numeric_fields = ['current_price', 'buy_shares', 'total_cost', 'stop_loss_price', 'score']
            for field in numeric_fields:
                if field in data and data[field] is not None:
                    try:
                        data[field] = Decimal(str(data[field]))
                    except (ValueError, TypeError):
                        raise TradingValidationError(f"Invalid numeric value for {field}: {data[field]}")
            
            # Validate and create model
            recommendation = TradingRecommendation(**data)
            self.validation_stats['successful_validations'] += 1
            
            console.print(f"✅ Validated trading recommendation for {recommendation.symbol}", style="green")
            return recommendation
            
        except ValidationError as e:
            self._handle_validation_error("TradingRecommendation", data, e)
            return None
        except Exception as e:
            self._handle_validation_error("TradingRecommendation", data, e)
            return None
    
    def validate_dataframe(self, df: pd.DataFrame, model_class: type) -> List[Any]:
        """Validate DataFrame rows and return list of validated models."""
        validated_models = []
        
        for index, row in df.iterrows():
            try:
                # Convert row to dict and handle NaN values
                data = row.to_dict()
                data = {k: v for k, v in data.items() if pd.notna(v)}
                
                # Validate based on model class
                if model_class == StockData:
                    model = self.validate_stock_data(data)
                elif model_class == PortfolioPosition:
                    model = self.validate_portfolio_position(data)
                elif model_class == TradeRecord:
                    model = self.validate_trade_record(data)
                elif model_class == CandidateStock:
                    model = self.validate_candidate_stock(data)
                elif model_class == TradingRecommendation:
                    model = self.validate_trading_recommendation(data)
                else:
                    raise TradingValidationError(f"Unknown model class: {model_class}")
                
                if model:
                    validated_models.append(model)
                    
            except Exception as e:
                console.print(f"⚠️ Validation error for row {index}: {str(e)}", style="yellow")
                continue
        
        return validated_models
    
    def validate_csv_file(self, file_path: str, model_class: type) -> List[Any]:
        """Load and validate CSV file to list of models."""
        try:
            df = pd.read_csv(file_path)
            console.print(f"📊 Loading {len(df)} rows from {file_path}", style="blue")
            return self.validate_dataframe(df, model_class)
        except Exception as e:
            error_handler.handle_file_error(e, file_path)
            return []
    
    def validate_json_file(self, file_path: str, model_class: type) -> List[Any]:
        """Load and validate JSON file to list of models."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                validated_models = []
                for item in data:
                    try:
                        if model_class == StockData:
                            model = self.validate_stock_data(item)
                        elif model_class == PortfolioPosition:
                            model = self.validate_portfolio_position(item)
                        elif model_class == TradeRecord:
                            model = self.validate_trade_record(item)
                        elif model_class == CandidateStock:
                            model = self.validate_candidate_stock(item)
                        elif model_class == TradingRecommendation:
                            model = self.validate_trading_recommendation(item)
                        else:
                            raise TradingValidationError(f"Unknown model class: {model_class}")
                        
                        if model:
                            validated_models.append(model)
                    except Exception as e:
                        console.print(f"⚠️ Validation error for item: {str(e)}", style="yellow")
                        continue
                
                return validated_models
            else:
                raise TradingValidationError("JSON file must contain a list of objects")
                
        except Exception as e:
            error_handler.handle_file_error(e, file_path)
            return []
    
    def _handle_validation_error(self, model_type: str, data: Dict[str, Any], error: Exception):
        """Handle validation errors with comprehensive logging."""
        self.validation_stats['failed_validations'] += 1
        error_type = type(error).__name__
        self.validation_stats['error_types'][error_type] = self.validation_stats['error_types'].get(error_type, 0) + 1
        
        # Log error with context
        error_context = {
            'model_type': model_type,
            'data_keys': list(data.keys()) if data else [],
            'error_type': error_type,
            'error_message': str(error)
        }
        
        error_handler.log_error_with_context(error, error_context)
        
        # Store validation error
        self.validation_errors.append({
            'model_type': model_type,
            'data': data,
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        })
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get comprehensive validation statistics."""
        success_rate = 0
        if self.validation_stats['total_validations'] > 0:
            success_rate = (self.validation_stats['successful_validations'] / 
                          self.validation_stats['total_validations']) * 100
        
        return {
            'total_validations': self.validation_stats['total_validations'],
            'successful_validations': self.validation_stats['successful_validations'],
            'failed_validations': self.validation_stats['failed_validations'],
            'success_rate': round(success_rate, 2),
            'error_types': self.validation_stats['error_types'],
            'validation_errors': self.validation_errors
        }
    
    def display_validation_summary(self):
        """Display validation summary in rich format."""
        summary = self.get_validation_summary()
        
        # Create summary table
        table = Table(title="📊 Data Validation Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Validations", str(summary['total_validations']))
        table.add_row("Successful", str(summary['successful_validations']))
        table.add_row("Failed", str(summary['failed_validations']))
        table.add_row("Success Rate", f"{summary['success_rate']}%")
        
        console.print(table)
        
        # Display error breakdown
        if summary['error_types']:
            error_table = Table(title="❌ Error Breakdown")
            error_table.add_column("Error Type", style="red")
            error_table.add_column("Count", style="yellow")
            
            for error_type, count in summary['error_types'].items():
                error_table.add_row(error_type, str(count))
            
            console.print(error_table)
    
    def reset_validation_stats(self):
        """Reset validation statistics."""
        self.validation_errors.clear()
        self.validation_stats = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'error_types': {}
        }
        console.print("✅ Validation statistics reset", style="green")

# Global data validator instance
data_validator = DataValidator()

# Convenience functions for easy integration
def validate_stock_data_safe(data: Dict[str, Any]) -> Optional[StockData]:
    """Safely validate stock data with error handling."""
    return data_validator.validate_stock_data(data)

def validate_portfolio_position_safe(data: Dict[str, Any]) -> Optional[PortfolioPosition]:
    """Safely validate portfolio position with error handling."""
    return data_validator.validate_portfolio_position(data)

def validate_trade_record_safe(data: Dict[str, Any]) -> Optional[TradeRecord]:
    """Safely validate trade record with error handling."""
    return data_validator.validate_trade_record(data)

def validate_candidate_stock_safe(data: Dict[str, Any]) -> Optional[CandidateStock]:
    """Safely validate candidate stock with error handling."""
    return data_validator.validate_candidate_stock(data)

def validate_trading_recommendation_safe(data: Dict[str, Any]) -> Optional[TradingRecommendation]:
    """Safely validate trading recommendation with error handling."""
    return data_validator.validate_trading_recommendation(data)

def validate_csv_safe(file_path: str, model_class: type) -> List[Any]:
    """Safely validate CSV file with error handling."""
    return data_validator.validate_csv_file(file_path, model_class)

def validate_json_safe(file_path: str, model_class: type) -> List[Any]:
    """Safely validate JSON file with error handling."""
    return data_validator.validate_json_file(file_path, model_class) 