import time
from typing import Any, Dict, Tuple, Optional

class RateLimitedCache:
    def __init__(self, cache_ttl: int = 300, min_delay: float = 2.0):
        """
        Initialize a rate-limited cache
        
        Args:
            cache_ttl (int): Time to live for cached items in seconds (default: 300s/5min)
            min_delay (float): Minimum delay between operations in seconds (default: 2.0s)
        """
        self.cache: Dict[str, Tuple[float, Any]] = {}
        self.cache_ttl = cache_ttl
        self.last_request = 0
        self.min_delay = min_delay

    def _throttle(self) -> None:
        """Enforce minimum delay between operations"""
        now = time.time()
        time_passed = now - self.last_request
        if time_passed < self.min_delay:
            time.sleep(self.min_delay - time_passed)
        self.last_request = time.time()

    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache if it exists and hasn't expired
        
        Args:
            key (str): Cache key to lookup
            
        Returns:
            Optional[Any]: Cached value if valid, None if expired or missing
        """
        now = time.time()
        if key in self.cache:
            cached_time, cached_data = self.cache[key]
            if now - cached_time < self.cache_ttl:
                return cached_data
        return None

    def set(self, key: str, value: Any) -> None:
        """
        Store item in cache with current timestamp
        
        Args:
            key (str): Cache key
            value (Any): Value to store
        """
        self._throttle()
        self.cache[key] = (time.time(), value)

    def clear(self) -> None:
        """Clear all cached items"""
        self.cache.clear()

    def remove_expired(self) -> None:
        """Remove all expired items from cache"""
        now = time.time()
        self.cache = {
            key: (ts, val) 
            for key, (ts, val) in self.cache.items() 
            if now - ts < self.cache_ttl
        } 