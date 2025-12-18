"""
In-Memory Cache System
Ultra-fast caching for frequently accessed data
"""

from functools import wraps
from typing import Any, Callable, Optional
import time
from collections import OrderedDict

# Global cache storage
_cache: dict = {}
_cache_timestamps: dict = {}
_cache_ttl: dict = {}


class LRUCache:
    """Least Recently Used cache with TTL support"""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: dict = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self.cache:
            return None
        
        # Check TTL
        if key in self.timestamps:
            ttl = self.timestamps.get(key, {}).get('ttl', self.default_ttl)
            age = time.time() - self.timestamps[key]['timestamp']
            if age > ttl:
                # Expired
                del self.cache[key]
                del self.timestamps[key]
                return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with optional TTL"""
        if ttl is None:
            ttl = self.default_ttl
        
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            if oldest_key in self.timestamps:
                del self.timestamps[oldest_key]
        
        self.cache[key] = value
        self.timestamps[key] = {
            'timestamp': time.time(),
            'ttl': ttl
        }
        self.cache.move_to_end(key)
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.timestamps.clear()
    
    def invalidate(self, key: str):
        """Remove specific key from cache"""
        if key in self.cache:
            del self.cache[key]
        if key in self.timestamps:
            del self.timestamps[key]


# Global LRU caches for different data types
_role_cache = LRUCache(max_size=50, default_ttl=600)  # 10 minutes
_user_cache = LRUCache(max_size=200, default_ttl=300)  # 5 minutes
_settings_cache = LRUCache(max_size=100, default_ttl=300)  # 5 minutes


def cached(ttl: int = 300, cache_instance: Optional[LRUCache] = None):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
        cache_instance: Optional LRUCache instance to use
    """
    def decorator(func: Callable) -> Callable:
        cache = cache_instance or LRUCache(default_ttl=ttl)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = "|".join(key_parts)
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result
        
        wrapper.cache = cache
        wrapper.clear_cache = lambda: cache.clear()
        return wrapper
    return decorator


def get_role_cache() -> LRUCache:
    """Get role cache instance"""
    return _role_cache


def get_user_cache() -> LRUCache:
    """Get user cache instance"""
    return _user_cache


def get_settings_cache() -> LRUCache:
    """Get settings cache instance"""
    return _settings_cache


def clear_all_caches():
    """Clear all caches"""
    _role_cache.clear()
    _user_cache.clear()
    _settings_cache.clear()
