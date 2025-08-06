#!/usr/bin/env python3
"""
Cache Manager
High-level interface for real-time cache management with use-case specific methods.
"""

import time
from typing import Dict, Any, List, Optional, Callable
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .real_time_cache import RealTimeCache
from .background_refresh import BackgroundRefresh
from .cache_config import (
    UseCase, PriorityLevel, get_use_case_for_symbol, get_ttl_for_use_case,
    is_real_time_use_case
)
from utilities.error_handler import error_handler, DataError, handle_exceptions

console = Console()

class RealTimeCacheManager:
    """High-level cache management interface for the trading system."""
    
    def __init__(self, data_fetcher: Callable):
        """
        Initialize cache manager.
        
        Args:
            data_fetcher: Function that fetches stock data (symbol -> data_dict)
        """
        self.cache = RealTimeCache()
        self.background_refresh = BackgroundRefresh(self.cache, data_fetcher)
        self.active_positions = set()
        self.watchlist = set()
        self.high_volume_stocks = set()
        
        # Start background refresh
        self.background_refresh.start()
    
    @handle_exceptions
    def get_stock_data_for_trading(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time data for active trading decisions."""
        use_case = UseCase.ACTIVE_POSITION
        data = self.cache.get(symbol, use_case)
        
        if data:
            # Queue background refresh for next update
            self.background_refresh.queue_refresh(symbol, use_case, PriorityLevel.HIGH)
            return data
        
        # Fetch real-time data if not in cache
        fresh_data = self._fetch_and_cache(symbol, use_case, PriorityLevel.HIGH)
        return fresh_data
    
    @handle_exceptions
    def get_stock_data_for_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached data for analysis and research."""
        use_case = UseCase.RESEARCH
        data = self.cache.get(symbol, use_case)
        
        if data:
            # Queue background refresh for next update
            self.background_refresh.queue_refresh(symbol, use_case, PriorityLevel.LOW)
            return data
        
        # Fetch data if not in cache
        fresh_data = self._fetch_and_cache(symbol, use_case, PriorityLevel.LOW)
        return fresh_data
    
    @handle_exceptions
    def get_portfolio_data(self, symbols: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """Get portfolio data with appropriate caching strategy."""
        portfolio_data = {}
        
        for symbol in symbols:
            if self._is_active_position(symbol):
                # Real-time data for active positions
                portfolio_data[symbol] = self.get_stock_data_for_trading(symbol)
            elif self._is_high_volume(symbol):
                # High priority for high volume stocks
                portfolio_data[symbol] = self._get_high_volume_data(symbol)
            else:
                # Cached data for others
                portfolio_data[symbol] = self.get_stock_data_for_analysis(symbol)
        
        return portfolio_data
    
    @handle_exceptions
    def get_watchlist_data(self, symbols: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """Get watchlist data with medium priority."""
        watchlist_data = {}
        
        for symbol in symbols:
            use_case = UseCase.WATCHLIST
            data = self.cache.get(symbol, use_case)
            
            if data:
                # Queue background refresh
                self.background_refresh.queue_refresh(symbol, use_case, PriorityLevel.MEDIUM)
                watchlist_data[symbol] = data
            else:
                # Fetch fresh data
                fresh_data = self._fetch_and_cache(symbol, use_case, PriorityLevel.MEDIUM)
                watchlist_data[symbol] = fresh_data
        
        return watchlist_data
    
    @handle_exceptions
    def get_historical_data(self, symbols: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """Get historical data with long-term caching."""
        historical_data = {}
        
        for symbol in symbols:
            use_case = UseCase.HISTORICAL
            data = self.cache.get(symbol, use_case)
            
            if data:
                # Queue background refresh
                self.background_refresh.queue_refresh(symbol, use_case, PriorityLevel.LOW)
                historical_data[symbol] = data
            else:
                # Fetch fresh data
                fresh_data = self._fetch_and_cache(symbol, use_case, PriorityLevel.LOW)
                historical_data[symbol] = fresh_data
        
        return historical_data
    
    @handle_exceptions
    def set_active_position(self, symbol: str, is_active: bool = True) -> None:
        """Mark a symbol as an active position for real-time updates."""
        if is_active:
            self.active_positions.add(symbol)
            # Queue immediate refresh for active position
            self.background_refresh.queue_refresh(symbol, UseCase.ACTIVE_POSITION, PriorityLevel.HIGH)
        else:
            self.active_positions.discard(symbol)
    
    @handle_exceptions
    def set_watchlist(self, symbols: List[str]) -> None:
        """Set watchlist symbols for medium priority updates."""
        self.watchlist = set(symbols)
        # Queue refresh for all watchlist symbols
        self.background_refresh.queue_batch_refresh(symbols, UseCase.WATCHLIST)
    
    @handle_exceptions
    def set_high_volume_stocks(self, symbols: List[str]) -> None:
        """Set high volume stocks for frequent updates."""
        self.high_volume_stocks = set(symbols)
        # Queue refresh for all high volume symbols
        self.background_refresh.queue_batch_refresh(symbols, UseCase.HIGH_VOLUME)
    
    @handle_exceptions
    def invalidate_cache(self, symbol: str, reason: str = "manual") -> bool:
        """Manually invalidate cache for a symbol."""
        return self.cache.invalidate(symbol, reason)
    
    @handle_exceptions
    def subscribe_to_updates(self, symbol: str, callback: Callable) -> None:
        """Subscribe to cache updates for a symbol."""
        self.cache.subscribe(symbol, callback)
        self.background_refresh.subscribe_to_refresh(symbol, callback)
    
    @handle_exceptions
    def unsubscribe_from_updates(self, symbol: str, callback: Callable) -> None:
        """Unsubscribe from cache updates for a symbol."""
        self.cache.unsubscribe(symbol, callback)
        self.background_refresh.unsubscribe_from_refresh(symbol, callback)
    
    @handle_exceptions
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        cache_stats = self.cache.get_stats()
        refresh_stats = self.background_refresh.get_stats()
        
        return {
            'cache': cache_stats,
            'background_refresh': refresh_stats,
            'active_positions': len(self.active_positions),
            'watchlist': len(self.watchlist),
            'high_volume_stocks': len(self.high_volume_stocks)
        }
    
    @handle_exceptions
    def display_comprehensive_stats(self) -> None:
        """Display comprehensive cache and refresh statistics."""
        stats = self.get_cache_stats()
        
        # Cache stats table
        cache_table = Table(title="Cache Statistics")
        cache_table.add_column("Metric", style="cyan")
        cache_table.add_column("Value", style="green")
        
        for key, value in stats['cache'].items():
            cache_table.add_row(key.replace('_', ' ').title(), str(value))
        
        # Background refresh stats table
        refresh_table = Table(title="Background Refresh Statistics")
        refresh_table.add_column("Metric", style="cyan")
        refresh_table.add_column("Value", style="blue")
        
        for key, value in stats['background_refresh'].items():
            refresh_table.add_row(key.replace('_', ' ').title(), str(value))
        
        # Summary panel
        summary_panel = Panel(
            f"Active Positions: {stats['active_positions']}\n"
            f"Watchlist: {stats['watchlist']}\n"
            f"High Volume Stocks: {stats['high_volume_stocks']}\n"
            f"Cache Hit Rate: {stats['cache']['hit_rate']}\n"
            f"Background Worker: {'Running' if stats['background_refresh']['worker_running'] else 'Stopped'}",
            title="Cache Manager Summary",
            border_style="green"
        )
        
        console.print(summary_panel)
        console.print(cache_table)
        console.print(refresh_table)
    
    @handle_exceptions
    def _fetch_and_cache(self, symbol: str, use_case: UseCase, 
                        priority: PriorityLevel) -> Optional[Dict[str, Any]]:
        """Fetch data and cache it with appropriate settings."""
        try:
            # Fetch fresh data
            fresh_data = self.background_refresh.data_fetcher(symbol)
            
            if fresh_data:
                # Cache the data
                self.cache.set(symbol, fresh_data, use_case)
                return fresh_data
            else:
                console.print(f"⚠️  No data returned for {symbol}", style="yellow")
                return None
                
        except Exception as e:
            console.print(f"❌ Failed to fetch data for {symbol}: {e}", style="red")
            return None
    
    def _is_active_position(self, symbol: str) -> bool:
        """Check if symbol is an active position."""
        return symbol in self.active_positions
    
    def _is_high_volume(self, symbol: str) -> bool:
        """Check if symbol is a high volume stock."""
        return symbol in self.high_volume_stocks
    
    @handle_exceptions
    def _get_high_volume_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get data for high volume stocks with frequent updates."""
        use_case = UseCase.HIGH_VOLUME
        data = self.cache.get(symbol, use_case)
        
        if data:
            # Queue background refresh
            self.background_refresh.queue_refresh(symbol, use_case, PriorityLevel.HIGH)
            return data
        
        # Fetch fresh data
        fresh_data = self._fetch_and_cache(symbol, use_case, PriorityLevel.HIGH)
        return fresh_data
    
    def shutdown(self) -> None:
        """Shutdown the cache manager and background refresh."""
        self.background_refresh.stop()
        console.print("🛑 Cache manager shutdown complete", style="yellow") 