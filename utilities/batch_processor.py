#!/usr/bin/env python3
"""
Batch Processing System
Optimizes data operations by processing multiple items in batches.
"""

import time
import threading
import asyncio
from typing import List, Dict, Any, Optional, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from utilities.error_handler import error_handler, handle_exceptions

console = Console()

@dataclass
class BatchTask:
    """Represents a batch processing task."""
    id: str
    data: Any
    priority: int = 1
    created_at: float = None
    retry_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

class BatchProcessor:
    """High-performance batch processing system for trading data operations."""
    
    def __init__(self, max_workers: int = 4, batch_size: int = 10, max_retries: int = 3):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'retried_tasks': 0,
            'total_processing_time': 0,
            'average_processing_time': 0
        }
    
    @handle_exceptions
    def process_batch(self, items: List[Any], processor_func: Callable, 
                     batch_name: str = "Batch") -> List[Any]:
        """Process a list of items in batches using the provided function."""
        if not items:
            return []
        
        console.print(f"🔄 Processing {len(items)} items in {batch_name}...", style="blue")
        
        start_time = time.time()
        results = []
        
        # Split items into batches
        batches = [items[i:i + self.batch_size] for i in range(0, len(items), self.batch_size)]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"Processing {batch_name}...", total=len(batches))
            
            # Process batches in parallel
            futures = []
            for batch in batches:
                future = self.executor.submit(self._process_single_batch, batch, processor_func)
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    batch_result = future.result()
                    results.extend(batch_result)
                    progress.advance(task)
                except Exception as e:
                    console.print(f"❌ Batch processing error: {e}", style="red")
                    self.stats['failed_tasks'] += 1
        
        processing_time = time.time() - start_time
        self.stats['total_processing_time'] += processing_time
        self.stats['total_tasks'] += len(items)
        self.stats['completed_tasks'] += len(results)
        
        if self.stats['total_tasks'] > 0:
            self.stats['average_processing_time'] = (
                self.stats['total_processing_time'] / self.stats['total_tasks']
            )
        
        console.print(f"✅ {batch_name} completed: {len(results)}/{len(items)} items processed in {processing_time:.2f}s", style="green")
        return results
    
    @handle_exceptions
    def _process_single_batch(self, batch: List[Any], processor_func: Callable) -> List[Any]:
        """Process a single batch of items."""
        results = []
        
        for item in batch:
            try:
                result = processor_func(item)
                if result is not None:
                    results.append(result)
            except Exception as e:
                console.print(f"⚠️  Item processing error: {e}", style="yellow")
                continue
        
        return results
    
    @handle_exceptions
    def process_with_retry(self, items: List[Any], processor_func: Callable, 
                          batch_name: str = "Batch") -> List[Any]:
        """Process items with automatic retry for failed items."""
        all_results = []
        failed_items = items.copy()
        
        for attempt in range(self.max_retries + 1):
            if not failed_items:
                break
            
            console.print(f"🔄 Attempt {attempt + 1}/{self.max_retries + 1} for {batch_name}...", style="blue")
            
            results = self.process_batch(failed_items, processor_func, f"{batch_name} (Attempt {attempt + 1})")
            all_results.extend(results)
            
            # Identify failed items for retry
            successful_items = set()
            for result in results:
                if hasattr(result, 'get'):
                    successful_items.add(result.get('symbol', result.get('id', str(result))))
                else:
                    successful_items.add(str(result))
            
            failed_items = [item for item in failed_items if str(item) not in successful_items]
            
            if failed_items:
                console.print(f"⚠️  {len(failed_items)} items failed, retrying...", style="yellow")
                self.stats['retried_tasks'] += len(failed_items)
                time.sleep(1)  # Brief delay before retry
        
        if failed_items:
            console.print(f"❌ {len(failed_items)} items failed after {self.max_retries + 1} attempts", style="red")
        
        return all_results
    
    @handle_exceptions
    def get_stats(self) -> Dict[str, Any]:
        """Get batch processing statistics."""
        return {
            'total_tasks': self.stats['total_tasks'],
            'completed_tasks': self.stats['completed_tasks'],
            'failed_tasks': self.stats['failed_tasks'],
            'retried_tasks': self.stats['retried_tasks'],
            'success_rate': f"{(self.stats['completed_tasks'] / max(self.stats['total_tasks'], 1)) * 100:.1f}%",
            'average_processing_time': f"{self.stats['average_processing_time']:.3f}s",
            'total_processing_time': f"{self.stats['total_processing_time']:.2f}s",
            'max_workers': self.max_workers,
            'batch_size': self.batch_size
        }
    
    @handle_exceptions
    def display_stats(self) -> None:
        """Display batch processing statistics."""
        stats = self.get_stats()
        
        table = Table(title="Batch Processing Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in stats.items():
            table.add_row(key.replace('_', ' ').title(), str(value))
        
        console.print(table)
    
    def shutdown(self) -> None:
        """Shutdown the batch processor."""
        self.executor.shutdown(wait=True)
        console.print("🛑 Batch processor shutdown complete", style="yellow")

class DataBatchProcessor:
    """Specialized batch processor for trading data operations."""
    
    def __init__(self, data_manager, max_workers: int = 4, batch_size: int = 10):
        self.data_manager = data_manager
        self.batch_processor = BatchProcessor(max_workers, batch_size)
    
    @handle_exceptions
    def batch_fetch_stock_data(self, symbols: List[str]) -> Dict[str, Optional[Dict]]:
        """Fetch stock data for multiple symbols in batches."""
        def fetch_single_symbol(symbol):
            return {'symbol': symbol, 'data': self.data_manager.get_stock_data(symbol)}
        
        results = self.batch_processor.process_batch(symbols, fetch_single_symbol, "Stock Data Fetch")
        
        # Convert to dictionary format
        stock_data = {}
        for result in results:
            if result and result['data']:
                stock_data[result['symbol']] = result['data']
        
        return stock_data
    
    @handle_exceptions
    def batch_calculate_scores(self, stock_data: Dict[str, Dict]) -> Dict[str, float]:
        """Calculate scores for multiple stocks in batches."""
        def calculate_single_score(item):
            symbol, data = item
            if data:
                score = self.data_manager.calculate_stock_score(data)
                return {'symbol': symbol, 'score': score}
            return None
        
        items = list(stock_data.items())
        results = self.batch_processor.process_batch(items, calculate_single_score, "Score Calculation")
        
        # Convert to dictionary format
        scores = {}
        for result in results:
            if result:
                scores[result['symbol']] = result['score']
        
        return scores
    
    @handle_exceptions
    def batch_validate_data(self, data_list: List[Dict]) -> List[Dict]:
        """Validate multiple data items in batches."""
        from validation.data_validator import validate_stock_data_safe
        
        def validate_single_item(data):
            return validate_stock_data_safe(data)
        
        return self.batch_processor.process_batch(data_list, validate_single_item, "Data Validation")
    
    @handle_exceptions
    def batch_update_portfolio(self, portfolio_data: List[Dict]) -> List[Dict]:
        """Update portfolio data for multiple positions in batches."""
        def update_single_position(position):
            symbol = position['symbol']
            current_data = self.data_manager.get_stock_data_for_trading(symbol)
            
            if current_data:
                position['current_price'] = current_data['price']
                position['pnl'] = (current_data['price'] - position['buy_price']) * position['shares']
            
            return position
        
        return self.batch_processor.process_batch(portfolio_data, update_single_position, "Portfolio Update")
    
    @handle_exceptions
    def batch_filter_microcaps(self, stock_data: Dict[str, Dict]) -> Dict[str, Dict]:
        """Filter microcap stocks in batches."""
        def filter_single_stock(item):
            symbol, data = item
            if data and data.get('market_cap', 0) < 2.0:
                return {'symbol': symbol, 'data': data}
            return None
        
        items = list(stock_data.items())
        results = self.batch_processor.process_batch(items, filter_single_stock, "Microcap Filter")
        
        # Convert to dictionary format
        filtered_data = {}
        for result in results:
            if result:
                filtered_data[result['symbol']] = result['data']
        
        return filtered_data
    
    @handle_exceptions
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self.batch_processor.get_stats()
    
    @handle_exceptions
    def display_processing_stats(self) -> None:
        """Display processing statistics."""
        self.batch_processor.display_stats()
    
    def shutdown(self) -> None:
        """Shutdown the data batch processor."""
        self.batch_processor.shutdown()

class FileBatchProcessor:
    """Specialized batch processor for file operations."""
    
    def __init__(self, max_workers: int = 2):
        self.batch_processor = BatchProcessor(max_workers, batch_size=5)
    
    @handle_exceptions
    def batch_read_csv_files(self, file_paths: List[str]) -> List[Any]:
        """Read multiple CSV files in batches."""
        import pandas as pd
        
        def read_single_csv(file_path):
            try:
                return pd.read_csv(file_path)
            except Exception as e:
                console.print(f"⚠️  Error reading {file_path}: {e}", style="yellow")
                return None
        
        return self.batch_processor.process_batch(file_paths, read_single_csv, "CSV File Read")
    
    @handle_exceptions
    def batch_write_csv_files(self, data_tuples: List[Tuple[Any, str]]) -> List[bool]:
        """Write multiple CSV files in batches."""
        import pandas as pd
        
        def write_single_csv(data_tuple):
            df, file_path = data_tuple
            try:
                df.to_csv(file_path, index=False)
                return True
            except Exception as e:
                console.print(f"⚠️  Error writing {file_path}: {e}", style="yellow")
                return False
        
        return self.batch_processor.process_batch(data_tuples, write_single_csv, "CSV File Write")
    
    @handle_exceptions
    def batch_process_json_files(self, file_paths: List[str]) -> List[Dict]:
        """Process multiple JSON files in batches."""
        import json
        
        def process_single_json(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                console.print(f"⚠️  Error reading {file_path}: {e}", style="yellow")
                return None
        
        return self.batch_processor.process_batch(file_paths, process_single_json, "JSON File Process")
    
    def shutdown(self) -> None:
        """Shutdown the file batch processor."""
        self.batch_processor.shutdown() 