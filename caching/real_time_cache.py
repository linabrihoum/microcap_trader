#!/usr/bin/env python3
"""
Real-Time Cache Engine
Core caching system with smart TTL management and dynamic invalidation.
"""

import time
import threading
from typing import Dict, Any, Optional, Tuple
from collections import OrderedDict
from decimal import Decimal
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .cache_config import (
    UseCase, PriorityLevel, CACHE_TTL_CONFIG, INVALIDATION_RULES,
    PERFORMANCE_CONFIG, get_ttl_for_use_case, get_priority_for_use_case
)
from utilities.error_handler import error_handler, DataError, handle_exceptions

console = Console()

class CacheEntry:
    """Represents a cached data entry with metadata."""
    
    def __init__(self, data: Dict[str, Any], use_case: UseCase, timestamp: float = None):
        self.data = data
        self.use_case = use_case
        self.timestamp = timestamp or time.time()
        self.access_count = 0
        self.last_accessed = self.timestamp
        self.invalidation_reason = None
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired based on TTL."""
        ttl = get_ttl_for_use_case(self.use_case)
        return time.time() - self.timestamp > ttl
    
    def access(self):
        """Mark entry as accessed."""
        self.access_count += 1
        self.last_accessed = time.time()
    
    def invalidate(self, reason: str = None):
        """Mark entry as invalidated."""
        self.invalidation_reason = reason or "manual"
    
    def get_age(self) -> float:
        """Get age of cache entry in seconds."""
        return time.time() - self.timestamp

class RealTimeCache:
    """Real-time cache with smart TTL management and dynamic invalidation."""
    
    def __init__(self, max_size: int = None):
        self.max_size = max_size or PERFORMANCE_CONFIG['max_cache_size']
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'invalidations': 0,
            'evictions': 0,
            'total_requests': 0
        }
        self.subscribers: Dict[str, list] = {}
    
    @handle_exceptions
    def get(self, key: str, use_case: UseCase = UseCase.RESEARCH) -> Optional[Dict[str, Any]]:
        """Get data from cache with smart validation."""
        with self.lock:
            self.stats['total_requests'] += 1
            
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            entry = self.cache[key]
            entry.access()
            
            # Check if entry is expired
            if entry.is_expired():
                self._invalidate_entry(key, "expired")
                self.stats['misses'] += 1
                return None
            
            # Move to end (LRU)
            self.cache.move_to_end(key)
            self.stats['hits'] += 1
            
            return entry.data.copy()
    
    @handle_exceptions
    def set(self, key: str, data: Dict[str, Any], use_case: UseCase = UseCase.RESEARCH) -> None:
        """Set data in cache with appropriate TTL."""
        with self.lock:
            # Create cache entry
            entry = CacheEntry(data, use_case)
            
            # Evict if cache is full
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            # Add to cache
            self.cache[key] = entry
            self.cache.move_to_end(key)
            
            # Notify subscribers
            self._notify_subscribers(key, data)
    
    @handle_exceptions
    def invalidate(self, key: str, reason: str = "manual") -> bool:
        """Manually invalidate a cache entry."""
        with self.lock:
            if key in self.cache:
                self._invalidate_entry(key, reason)
                return True
            return False
    
    @handle_exceptions
    def should_invalidate(self, key: str, new_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if cache should be invalidated based on data changes."""
        if key not in self.cache:
            return False, None
        
        entry = self.cache[key]
        old_data = entry.data
        
        # Check price change
        if 'price' in old_data and 'price' in new_data:
            old_price = Decimal(str(old_data['price']))
            new_price = Decimal(str(new_data['price']))
            price_change = abs(new_price - old_price) / old_price
            
            if price_change > INVALIDATION_RULES['price_change_threshold']:
                return True, f"price_change_{price_change:.2%}"
        
        # Check volume change
        if 'volume' in old_data and 'volume' in new_data:
            old_volume = old_data['volume']
            new_volume = new_data['volume']
            if old_volume > 0:
                volume_change = abs(new_volume - old_volume) / old_volume
                if volume_change > INVALIDATION_RULES['volume_change_threshold']:
                    return True, f"volume_change_{volume_change:.2%}"
        
        return False, None
    
    @handle_exceptions
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            hit_rate = (self.stats['hits'] / max(self.stats['total_requests'], 1)) * 100
            return {
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'invalidations': self.stats['invalidations'],
                'evictions': self.stats['evictions'],
                'total_requests': self.stats['total_requests'],
                'hit_rate': f"{hit_rate:.2f}%",
                'cache_size': len(self.cache),
                'max_size': self.max_size
            }
    
    @handle_exceptions
    def subscribe(self, key: str, callback) -> None:
        """Subscribe to cache updates for a specific key."""
        if key not in self.subscribers:
            self.subscribers[key] = []
        self.subscribers[key].append(callback)
    
    @handle_exceptions
    def unsubscribe(self, key: str, callback) -> None:
        """Unsubscribe from cache updates."""
        if key in self.subscribers and callback in self.subscribers[key]:
            self.subscribers[key].remove(callback)
    
    def _invalidate_entry(self, key: str, reason: str) -> None:
        """Internal method to invalidate a cache entry."""
        if key in self.cache:
            entry = self.cache[key]
            entry.invalidate(reason)
            del self.cache[key]
            self.stats['invalidations'] += 1
    
    def _evict_oldest(self) -> None:
        """Evict the oldest cache entry."""
        if self.cache:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.stats['evictions'] += 1
    
    def _notify_subscribers(self, key: str, data: Dict[str, Any]) -> None:
        """Notify subscribers of cache updates."""
        if key in self.subscribers:
            for callback in self.subscribers[key]:
                try:
                    callback(key, data)
                except Exception as e:
                    console.print(f"⚠️  Subscriber notification failed: {e}", style="yellow")
    
    def display_stats(self) -> None:
        """Display cache statistics in a rich table."""
        stats = self.get_stats()
        
        table = Table(title="Cache Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in stats.items():
            table.add_row(key.replace('_', ' ').title(), str(value))
        
        console.print(table)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.stats = {
                'hits': 0,
                'misses': 0,
                'invalidations': 0,
                'evictions': 0,
                'total_requests': 0
            } 