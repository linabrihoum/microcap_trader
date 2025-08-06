#!/usr/bin/env python3
"""
Cache Configuration for Real-Time Trading System
Defines TTL settings, priority levels, and invalidation rules.
"""

from enum import Enum
from typing import Dict, Any
from decimal import Decimal

class PriorityLevel(str, Enum):
    """Priority levels for cache operations."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class UseCase(str, Enum):
    """Use cases for different data requirements."""
    ACTIVE_POSITION = "active_position"
    WATCHLIST = "watchlist"
    HIGH_VOLUME = "high_volume"
    RESEARCH = "research"
    HISTORICAL = "historical"

# Cache TTL Configuration (in seconds)
CACHE_TTL_CONFIG = {
    UseCase.ACTIVE_POSITION: {
        'ttl': 30,  # 30 seconds
        'priority': PriorityLevel.HIGH,
        'real_time': True,
        'description': 'Active trading positions - real-time data'
    },
    UseCase.WATCHLIST: {
        'ttl': 120,  # 2 minutes
        'priority': PriorityLevel.MEDIUM,
        'real_time': True,
        'description': 'Watchlist stocks - near real-time data'
    },
    UseCase.HIGH_VOLUME: {
        'ttl': 60,  # 1 minute
        'priority': PriorityLevel.HIGH,
        'real_time': True,
        'description': 'High volume stocks - frequent updates'
    },
    UseCase.RESEARCH: {
        'ttl': 300,  # 5 minutes
        'priority': PriorityLevel.LOW,
        'real_time': False,
        'description': 'Research and analysis - cached data'
    },
    UseCase.HISTORICAL: {
        'ttl': 900,  # 15 minutes
        'priority': PriorityLevel.LOW,
        'real_time': False,
        'description': 'Historical analysis - long-term cached data'
    }
}

# Invalidation Rules
INVALIDATION_RULES = {
    'price_change_threshold': Decimal('0.02'),  # 2% price change
    'volume_change_threshold': Decimal('0.50'),  # 50% volume change
    'time_expiration': True,  # Enable time-based expiration
    'manual_invalidation': True,  # Enable manual invalidation
}

# Performance Settings
PERFORMANCE_CONFIG = {
    'max_cache_size': 1000,  # Maximum number of cached items
    'background_refresh_interval': 30,  # Background refresh interval (seconds)
    'max_retries': 3,  # Maximum retry attempts for failed refreshes
    'retry_delay': 5,  # Delay between retries (seconds)
    'subscriber_timeout': 10,  # Timeout for subscriber notifications (seconds)
}

# Priority Queue Settings
PRIORITY_QUEUE_CONFIG = {
    'max_queue_size': 500,  # Maximum items in priority queue
    'high_priority_weight': 3,  # Weight for high priority items
    'medium_priority_weight': 2,  # Weight for medium priority items
    'low_priority_weight': 1,  # Weight for low priority items
}

# Cache Statistics Configuration
STATS_CONFIG = {
    'track_hit_rate': True,
    'track_miss_rate': True,
    'track_invalidation_rate': True,
    'track_response_time': True,
    'stats_reset_interval': 3600,  # Reset stats every hour
}

def get_ttl_for_use_case(use_case: UseCase) -> int:
    """Get TTL for a specific use case."""
    return CACHE_TTL_CONFIG[use_case]['ttl']

def get_priority_for_use_case(use_case: UseCase) -> PriorityLevel:
    """Get priority level for a specific use case."""
    return CACHE_TTL_CONFIG[use_case]['priority']

def is_real_time_use_case(use_case: UseCase) -> bool:
    """Check if a use case requires real-time data."""
    return CACHE_TTL_CONFIG[use_case]['real_time']

def get_use_case_for_symbol(symbol: str, is_active_position: bool = False, 
                           is_high_volume: bool = False) -> UseCase:
    """Determine use case for a symbol based on context."""
    if is_active_position:
        return UseCase.ACTIVE_POSITION
    elif is_high_volume:
        return UseCase.HIGH_VOLUME
    else:
        return UseCase.RESEARCH

def get_cache_config() -> Dict[str, Any]:
    """Get complete cache configuration."""
    return {
        'ttl_config': CACHE_TTL_CONFIG,
        'invalidation_rules': INVALIDATION_RULES,
        'performance_config': PERFORMANCE_CONFIG,
        'priority_queue_config': PRIORITY_QUEUE_CONFIG,
        'stats_config': STATS_CONFIG,
    } 