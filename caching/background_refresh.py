#!/usr/bin/env python3
"""
Background Refresh System
Handles non-blocking data updates with priority queuing.
"""

import time
import threading
import queue
from typing import Dict, Any, Optional, Callable, Tuple
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .cache_config import (
    UseCase, PriorityLevel, PERFORMANCE_CONFIG, PRIORITY_QUEUE_CONFIG,
    get_priority_for_use_case, get_use_case_for_symbol
)
from utilities.error_handler import error_handler, APIError, NetworkError, handle_exceptions

console = Console()

class RefreshTask:
    """Represents a background refresh task."""
    
    def __init__(self, symbol: str, use_case: UseCase, priority: PriorityLevel, 
                 data_fetcher: Callable, retry_count: int = 0):
        self.symbol = symbol
        self.use_case = use_case
        self.priority = priority
        self.data_fetcher = data_fetcher
        self.retry_count = retry_count
        self.created_at = time.time()
        self.last_attempt = None
        self.error_count = 0
    
    def __lt__(self, other):
        """Priority comparison for queue ordering."""
        priority_weights = {
            PriorityLevel.HIGH: PRIORITY_QUEUE_CONFIG['high_priority_weight'],
            PriorityLevel.MEDIUM: PRIORITY_QUEUE_CONFIG['medium_priority_weight'],
            PriorityLevel.LOW: PRIORITY_QUEUE_CONFIG['low_priority_weight']
        }
        
        # Higher priority first
        if self.priority != other.priority:
            return priority_weights[self.priority] > priority_weights[other.priority]
        
        # Older tasks first within same priority
        return self.created_at < other.created_at

class BackgroundRefresh:
    """Background data refresh system with priority queuing."""
    
    def __init__(self, cache, data_fetcher: Callable):
        self.cache = cache
        self.data_fetcher = data_fetcher
        self.refresh_queue = queue.PriorityQueue(maxsize=PRIORITY_QUEUE_CONFIG['max_queue_size'])
        self.running = False
        self.worker_thread = None
        self.stats = {
            'tasks_processed': 0,
            'tasks_failed': 0,
            'tasks_retried': 0,
            'total_refresh_time': 0,
            'average_refresh_time': 0
        }
        self.subscribers: Dict[str, list] = {}
    
    @handle_exceptions
    def start(self) -> None:
        """Start the background refresh worker."""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            console.print("🔄 Background refresh system started", style="green")
    
    @handle_exceptions
    def stop(self) -> None:
        """Stop the background refresh worker."""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        console.print("⏹️  Background refresh system stopped", style="yellow")
    
    @handle_exceptions
    def queue_refresh(self, symbol: str, use_case: UseCase = UseCase.RESEARCH, 
                     priority: PriorityLevel = None) -> bool:
        """Queue a symbol for background refresh."""
        if priority is None:
            priority = get_priority_for_use_case(use_case)
        
        try:
            task = RefreshTask(
                symbol=symbol,
                use_case=use_case,
                priority=priority,
                data_fetcher=self.data_fetcher
            )
            
            self.refresh_queue.put(task)
            return True
            
        except queue.Full:
            console.print(f"⚠️  Refresh queue full, skipping {symbol}", style="yellow")
            return False
    
    @handle_exceptions
    def queue_batch_refresh(self, symbols: list, use_case: UseCase = UseCase.RESEARCH) -> int:
        """Queue multiple symbols for background refresh."""
        queued_count = 0
        for symbol in symbols:
            if self.queue_refresh(symbol, use_case):
                queued_count += 1
        
        console.print(f"📦 Queued {queued_count}/{len(symbols)} symbols for refresh", style="blue")
        return queued_count
    
    @handle_exceptions
    def subscribe_to_refresh(self, symbol: str, callback: Callable) -> None:
        """Subscribe to refresh updates for a specific symbol."""
        if symbol not in self.subscribers:
            self.subscribers[symbol] = []
        self.subscribers[symbol].append(callback)
    
    @handle_exceptions
    def unsubscribe_from_refresh(self, symbol: str, callback: Callable) -> None:
        """Unsubscribe from refresh updates."""
        if symbol in self.subscribers and callback in self.subscribers[symbol]:
            self.subscribers[symbol].remove(callback)
    
    def _worker_loop(self) -> None:
        """Main worker loop for processing refresh tasks."""
        while self.running:
            try:
                # Get task from queue with timeout
                task = self.refresh_queue.get(timeout=1)
                self._process_task(task)
                self.refresh_queue.task_done()
                
            except queue.Empty:
                # No tasks in queue, continue
                continue
            except Exception as e:
                console.print(f"❌ Worker loop error: {e}", style="red")
                time.sleep(1)
    
    @handle_exceptions
    def _process_task(self, task: RefreshTask) -> None:
        """Process a single refresh task."""
        start_time = time.time()
        task.last_attempt = start_time
        
        try:
            # Fetch fresh data
            new_data = task.data_fetcher(task.symbol)
            
            if new_data:
                # Check if cache should be invalidated
                should_invalidate, reason = self.cache.should_invalidate(task.symbol, new_data)
                
                if should_invalidate:
                    console.print(f"🔄 Invalidating cache for {task.symbol}: {reason}", style="yellow")
                
                # Update cache
                self.cache.set(task.symbol, new_data, task.use_case)
                
                # Notify subscribers
                self._notify_subscribers(task.symbol, new_data)
                
                # Update stats
                refresh_time = time.time() - start_time
                self.stats['tasks_processed'] += 1
                self.stats['total_refresh_time'] += refresh_time
                self.stats['average_refresh_time'] = (
                    self.stats['total_refresh_time'] / self.stats['tasks_processed']
                )
                
                console.print(f"✅ Refreshed {task.symbol} ({refresh_time:.2f}s)", style="green")
                
            else:
                raise DataError(f"No data returned for {task.symbol}")
                
        except Exception as e:
            self._handle_task_error(task, e)
    
    @handle_exceptions
    def _handle_task_error(self, task: RefreshTask, error: Exception) -> None:
        """Handle errors during task processing."""
        task.error_count += 1
        self.stats['tasks_failed'] += 1
        
        max_retries = PERFORMANCE_CONFIG['max_retries']
        retry_delay = PERFORMANCE_CONFIG['retry_delay']
        
        if task.retry_count < max_retries:
            # Retry the task
            task.retry_count += 1
            self.stats['tasks_retried'] += 1
            
            console.print(
                f"🔄 Retrying {task.symbol} ({task.retry_count}/{max_retries}): {error}",
                style="yellow"
            )
            
            # Re-queue with delay
            time.sleep(retry_delay)
            self.queue_refresh(task.symbol, task.use_case, task.priority)
            
        else:
            console.print(
                f"❌ Failed to refresh {task.symbol} after {max_retries} attempts: {error}",
                style="red"
            )
    
    @handle_exceptions
    def _notify_subscribers(self, symbol: str, data: Dict[str, Any]) -> None:
        """Notify subscribers of refresh updates."""
        if symbol in self.subscribers:
            for callback in self.subscribers[symbol]:
                try:
                    callback(symbol, data)
                except Exception as e:
                    console.print(f"⚠️  Subscriber notification failed: {e}", style="yellow")
    
    @handle_exceptions
    def get_stats(self) -> Dict[str, Any]:
        """Get background refresh statistics."""
        queue_size = self.refresh_queue.qsize()
        return {
            'queue_size': queue_size,
            'tasks_processed': self.stats['tasks_processed'],
            'tasks_failed': self.stats['tasks_failed'],
            'tasks_retried': self.stats['tasks_retried'],
            'average_refresh_time': f"{self.stats['average_refresh_time']:.2f}s",
            'worker_running': self.running,
            'max_queue_size': PRIORITY_QUEUE_CONFIG['max_queue_size']
        }
    
    def display_stats(self) -> None:
        """Display background refresh statistics."""
        stats = self.get_stats()
        
        panel = Panel(
            f"Queue Size: {stats['queue_size']}\n"
            f"Tasks Processed: {stats['tasks_processed']}\n"
            f"Tasks Failed: {stats['tasks_failed']}\n"
            f"Tasks Retried: {stats['tasks_retried']}\n"
            f"Average Refresh Time: {stats['average_refresh_time']}\n"
            f"Worker Running: {stats['worker_running']}",
            title="Background Refresh Statistics",
            border_style="blue"
        )
        
        console.print(panel)
    
    def is_running(self) -> bool:
        """Check if background refresh is running."""
        return self.running and self.worker_thread and self.worker_thread.is_alive() 