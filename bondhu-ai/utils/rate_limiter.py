"""
Rate Limiter with Redis backend for API request throttling.
Implements sliding window rate limiting for Spotify, YouTube, Steam APIs.
"""
import time
from typing import Optional
from datetime import datetime, timedelta
from functools import wraps

from core.cache.redis_client import get_redis
from core.config.settings import config


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, service: str, retry_after: int):
        self.service = service
        self.retry_after = retry_after
        super().__init__(
            f"Rate limit exceeded for {service}. Retry after {retry_after} seconds."
        )


class RateLimiter:
    """
    Redis-based rate limiter using sliding window algorithm.
    
    Supports different rate limits per service (Spotify, YouTube, Steam, OpenAI).
    """
    
    # Rate limits from config (requests per minute)
    LIMITS = {
        'spotify': config.spotify_rpm,
        'youtube': config.youtube_rpm,
        'steam': config.steam_rpm,
        'openai': config.openai_rpm,
    }
    
    def __init__(self, service: str):
        """
        Initialize rate limiter for a specific service.
        
        Args:
            service: Service name ('spotify', 'youtube', 'steam', 'openai')
        """
        if service not in self.LIMITS:
            raise ValueError(f"Unknown service: {service}. Must be one of {list(self.LIMITS.keys())}")
        
        self.service = service
        self.limit = self.LIMITS[service]
        self.window = 60  # 1 minute window in seconds
        self.redis_client = get_redis()
    
    def _get_key(self, identifier: str) -> str:
        """Generate Redis key for rate limiting."""
        return f"ratelimit:{self.service}:{identifier}"
    
    def check_rate_limit(self, identifier: str) -> bool:
        """
        Check if request is within rate limit.
        
        Args:
            identifier: User ID or API key identifier
            
        Returns:
            True if request is allowed, False otherwise
            
        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        key = self._get_key(identifier)
        now = time.time()
        window_start = now - self.window
        
        # Remove old entries outside the window
        self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # Count requests in current window
        current_count = self.redis_client.zcard(key)
        
        if current_count >= self.limit:
            # Get oldest request timestamp to calculate retry_after
            oldest_requests = self.redis_client.zrange(key, 0, 0, withscores=True)
            if oldest_requests:
                oldest_timestamp = oldest_requests[0][1]
                retry_after = int(self.window - (now - oldest_timestamp)) + 1
            else:
                retry_after = self.window
            
            raise RateLimitExceeded(self.service, retry_after)
        
        # Add current request timestamp
        self.redis_client.zadd(key, {str(now): now})
        
        # Set expiry on the key (cleanup)
        self.redis_client.expire(key, self.window * 2)
        
        return True
    
    def get_remaining(self, identifier: str) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            identifier: User ID or API key identifier
            
        Returns:
            Number of remaining requests
        """
        key = self._get_key(identifier)
        now = time.time()
        window_start = now - self.window
        
        # Remove old entries
        self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current_count = self.redis_client.zcard(key)
        
        return max(0, self.limit - current_count)
    
    def reset(self, identifier: str):
        """
        Reset rate limit for identifier (admin/testing only).
        
        Args:
            identifier: User ID or API key identifier
        """
        key = self._get_key(identifier)
        self.redis_client.delete(key)


def rate_limit(service: str):
    """
    Decorator to apply rate limiting to functions.
    
    Usage:
        @rate_limit('spotify')
        def get_spotify_data(user_id: str):
            # API call here
            pass
    
    Args:
        service: Service name ('spotify', 'youtube', 'steam', 'openai')
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract user_id from function args/kwargs
            user_id = kwargs.get('user_id') or (args[0] if args else 'default')
            
            limiter = RateLimiter(service)
            limiter.check_rate_limit(str(user_id))
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Global rate limiter instances
spotify_limiter = RateLimiter('spotify')
youtube_limiter = RateLimiter('youtube')
steam_limiter = RateLimiter('steam')
openai_limiter = RateLimiter('openai')
