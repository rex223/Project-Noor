"""
Core Rate Limiter Service for Bondhu AI

Centralized rate limiting service that manages API quotas, caching, and request queueing
across all agents and services. Integrates with Redis for distributed state management.
"""

import asyncio
import logging
import yaml
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum
from pathlib import Path

from core.cache.redis_rate_limiter import redis_manager, UserTier, APIType

logger = logging.getLogger("bondhu.rate_limiter.service")


class RequestPriority(Enum):
    """Request priority levels for queue management"""
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"


class RateLimitResult(Enum):
    """Rate limiting decision results"""
    ALLOWED = "allowed"
    CACHED = "cached"
    QUEUED = "queued"
    DENIED = "denied"


class APIQuotaExceeded(Exception):
    """Raised when API quota is exceeded"""
    def __init__(self, api_type: str, user_id: str, current_usage: int, limit: int):
        self.api_type = api_type
        self.user_id = user_id
        self.current_usage = current_usage
        self.limit = limit
        super().__init__(f"API quota exceeded for {api_type}: {current_usage}/{limit}")


class RateLimiterService:
    """Central rate limiting service with caching and queue management"""
    
    def __init__(self, config_path: str = "config/rate_limits.yaml"):
        """Initialize rate limiter with configuration"""
        self.config = self._load_config(config_path)
        self.redis = redis_manager
        self._quota_cache = {}  # In-memory cache for frequently accessed quotas
        self._cache_expiry = {}
        
        logger.info("RateLimiterService initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load rate limiting configuration from YAML file"""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                logger.warning(f"Config file not found: {config_path}. Using defaults.")
                return self._get_default_config()
                
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                
            logger.info(f"Rate limiting config loaded from {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}. Using defaults.")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when config file is not available"""
        return {
            "user_tiers": {
                "free": {"youtube": 50, "spotify": 20, "openai": 100, "gaming": 50},
                "premium": {"youtube": 500, "spotify": 180, "openai": 1000, "gaming": 200},
                "enterprise": {"youtube": 2000, "spotify": 500, "openai": 5000, "gaming": 1000}
            },
            "api_costs": {
                "youtube": {"search": 100, "video_details": 1, "playlist_items": 1},
                "spotify": {"search_tracks": 1, "track_details": 1},
                "openai": {"gpt4": 1, "gpt35_turbo": 1},
                "gaming": {"steam_stats": 1}
            },
            "cache_ttl": {
                "youtube": {"search_results": 86400, "video_details": 604800},
                "spotify": {"track_details": 2592000},
                "openai": {"chat_context": 1800},
                "gaming": {"player_stats": 3600}
            }
        }
    
    # ===== MAIN API METHODS =====
    
    async def check_and_consume_quota(
        self, 
        user_id: str, 
        user_tier: str, 
        api_type: str, 
        operation: str,
        request_data: Dict[str, Any] = None,
        priority: RequestPriority = RequestPriority.MEDIUM
    ) -> Tuple[RateLimitResult, Dict[str, Any]]:
        """
        Main method to check quota, consume if available, or queue if exceeded.
        
        Returns:
            Tuple of (result, metadata) where:
            - result: RateLimitResult enum
            - metadata: Dict with quota info, cache status, queue position, etc.
        """
        
        # Validate inputs
        if not self._validate_inputs(user_id, user_tier, api_type, operation):
            return RateLimitResult.DENIED, {"error": "Invalid input parameters"}
        
        # Check cache first if request_data provided
        if request_data:
            cache_result = await self._check_cache(api_type, operation, request_data, user_id)
            if cache_result:
                return RateLimitResult.CACHED, {
                    "cached_data": cache_result,
                    "cache_hit": True,
                    "quota_consumed": 0
                }
        
        # Get quota limits and current usage
        quota_info = await self._get_quota_info(user_id, user_tier, api_type)
        operation_cost = self._get_operation_cost(api_type, operation)
        
        # Check if quota allows this request
        if quota_info["current_usage"] + operation_cost <= quota_info["limit"]:
            # Consume quota
            new_usage = self.redis.increment_quota(api_type, user_id, operation_cost)
            
            # Update local cache
            self._update_quota_cache(user_id, api_type, new_usage)
            
            return RateLimitResult.ALLOWED, {
                "quota_consumed": operation_cost,
                "quota_remaining": quota_info["limit"] - new_usage,
                "quota_usage": new_usage,
                "quota_limit": quota_info["limit"]
            }
        
        else:
            # Quota exceeded - queue the request
            queue_success = await self._queue_request(
                user_id, api_type, operation, request_data, priority
            )
            
            if queue_success:
                queue_position = self.redis.get_queue_depth(user_id)
                
                return RateLimitResult.QUEUED, {
                    "queue_position": queue_position,
                    "quota_exceeded": True,
                    "quota_usage": quota_info["current_usage"],
                    "quota_limit": quota_info["limit"],
                    "estimated_wait_time": self._estimate_queue_wait_time(queue_position)
                }
            else:
                return RateLimitResult.DENIED, {
                    "error": "Quota exceeded and queueing failed",
                    "quota_usage": quota_info["current_usage"], 
                    "quota_limit": quota_info["limit"]
                }
    
    async def process_cached_request(
        self,
        user_id: str,
        api_type: str,
        operation: str, 
        request_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check cache for existing response to avoid API call"""
        return await self._check_cache(api_type, operation, request_data, user_id)
    
    async def cache_response(
        self,
        user_id: str,
        api_type: str,
        operation: str,
        request_data: Dict[str, Any],
        response_data: Any,
        custom_ttl: Optional[int] = None
    ) -> bool:
        """Cache API response for future requests"""
        
        # Generate cache key
        cache_query = self._build_cache_query(operation, request_data)
        user_context = f"tier:{await self._get_user_tier(user_id)}"
        
        # Get TTL from config or use custom
        ttl = custom_ttl or self._get_cache_ttl(api_type, operation)
        
        # Cache the response
        success = self.redis.set_cache(api_type, cache_query, response_data, ttl, user_context)
        
        if success:
            logger.debug(f"Cached response for {api_type}:{operation} (TTL: {ttl}s)")
        
        return success
    
    async def get_user_quota_status(self, user_id: str, user_tier: str) -> Dict[str, Any]:
        """Get comprehensive quota status for all APIs"""
        
        quota_status = {
            "user_id": user_id,
            "user_tier": user_tier,
            "timestamp": datetime.utcnow().isoformat(),
            "quotas": {},
            "queue_depth": self.redis.get_queue_depth(user_id)
        }
        
        # Get quota info for each API type
        for api_type in APIType:
            api_name = api_type.value
            quota_info = await self._get_quota_info(user_id, user_tier, api_name)
            
            quota_status["quotas"][api_name] = {
                "current_usage": quota_info["current_usage"],
                "limit": quota_info["limit"],
                "remaining": quota_info["limit"] - quota_info["current_usage"],
                "percentage_used": (quota_info["current_usage"] / quota_info["limit"]) * 100 if quota_info["limit"] > 0 else 0,
                "reset_time": quota_info.get("reset_time")
            }
        
        return quota_status
    
    async def process_queue(self, user_id: str, max_items: int = 5) -> List[Dict[str, Any]]:
        """Process queued requests for user when quota becomes available"""
        
        processed_items = []
        queued_requests = self.redis.get_queued_requests(user_id, max_items)
        
        for request in queued_requests:
            try:
                api_type = request["api_type"]
                operation = request["request_data"].get("operation", "unknown")
                priority = RequestPriority(request.get("priority", "medium"))
                
                # Check if quota now available
                user_tier = await self._get_user_tier(user_id)
                result, metadata = await self.check_and_consume_quota(
                    user_id, user_tier, api_type, operation, 
                    request["request_data"], priority
                )
                
                if result == RateLimitResult.ALLOWED:
                    # Remove from queue and add to processed
                    self.redis.remove_queued_request(user_id, request)
                    processed_items.append({
                        "request": request,
                        "result": result.value,
                        "metadata": metadata
                    })
                    
                elif result == RateLimitResult.CACHED:
                    # Remove from queue (cache hit)
                    self.redis.remove_queued_request(user_id, request)
                    processed_items.append({
                        "request": request,
                        "result": result.value,
                        "metadata": metadata
                    })
                
                # If still queued or denied, leave in queue
                
            except Exception as e:
                logger.error(f"Error processing queued request: {e}")
                continue
        
        return processed_items
    
    # ===== HELPER METHODS =====
    
    def _validate_inputs(self, user_id: str, user_tier: str, api_type: str, operation: str) -> bool:
        """Validate input parameters"""
        if not user_id or not user_tier or not api_type or not operation:
            return False
            
        if user_tier not in self.config.get("user_tiers", {}):
            logger.warning(f"Unknown user tier: {user_tier}")
            return False
            
        if api_type not in [t.value for t in APIType]:
            logger.warning(f"Unknown API type: {api_type}")
            return False
            
        return True
    
    async def _get_quota_info(self, user_id: str, user_tier: str, api_type: str) -> Dict[str, Any]:
        """Get current quota usage and limits for user"""
        
        # Check local cache first
        cache_key = f"{user_id}:{api_type}"
        if cache_key in self._quota_cache and cache_key in self._cache_expiry:
            if datetime.utcnow() < self._cache_expiry[cache_key]:
                return self._quota_cache[cache_key]
        
        # Get from Redis
        current_usage = self.redis.get_quota_usage(api_type, user_id)
        limit = self.config["user_tiers"][user_tier].get(api_type, 0)
        
        # Check if needs daily reset
        reset_time = self._get_next_reset_time()
        
        quota_info = {
            "current_usage": current_usage,
            "limit": limit,
            "reset_time": reset_time.isoformat()
        }
        
        # Cache locally for 5 minutes
        self._quota_cache[cache_key] = quota_info
        self._cache_expiry[cache_key] = datetime.utcnow() + timedelta(minutes=5)
        
        return quota_info
    
    def _get_operation_cost(self, api_type: str, operation: str) -> int:
        """Get quota cost for specific API operation"""
        api_costs = self.config.get("api_costs", {}).get(api_type, {})
        return api_costs.get(operation, 1)  # Default cost is 1
    
    async def _check_cache(
        self, 
        api_type: str, 
        operation: str, 
        request_data: Dict[str, Any], 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Check Redis cache for existing response"""
        
        cache_query = self._build_cache_query(operation, request_data)
        user_tier = await self._get_user_tier(user_id)
        user_context = f"tier:{user_tier}"
        
        cached_data = self.redis.get_cache(api_type, cache_query, user_context)
        
        if cached_data:
            return cached_data.get("result")
        
        return None
    
    def _build_cache_query(self, operation: str, request_data: Dict[str, Any]) -> str:
        """Build cache query string from operation and request data"""
        # Extract key parameters for caching
        key_params = []
        
        if operation == "search":
            key_params.append(f"q:{request_data.get('query', '')}")
            key_params.append(f"max:{request_data.get('max_results', 10)}")
        elif operation == "video_details":
            key_params.append(f"ids:{','.join(request_data.get('video_ids', []))}")
        elif operation == "track_details":
            key_params.append(f"id:{request_data.get('track_id', '')}")
        
        return f"{operation}|{'|'.join(key_params)}"
    
    def _get_cache_ttl(self, api_type: str, operation: str) -> int:
        """Get cache TTL for specific API and operation"""
        cache_config = self.config.get("cache_ttl", {}).get(api_type, {})
        
        # Map operations to cache config keys
        operation_mapping = {
            "search": "search_results",
            "video_details": "video_details", 
            "track_details": "track_details",
            "chat_completion": "chat_context"
        }
        
        cache_key = operation_mapping.get(operation, operation)
        return cache_config.get(cache_key, 3600)  # Default 1 hour
    
    async def _queue_request(
        self,
        user_id: str,
        api_type: str, 
        operation: str,
        request_data: Dict[str, Any],
        priority: RequestPriority
    ) -> bool:
        """Queue request when quota exceeded"""
        
        queue_data = {
            "api_type": api_type,
            "operation": operation,
            "request_data": request_data or {},
            "user_id": user_id
        }
        
        return self.redis.queue_request(user_id, api_type, queue_data, priority.value)
    
    def _estimate_queue_wait_time(self, queue_position: int) -> int:
        """Estimate wait time based on queue position"""
        # Rough estimate: ~30 seconds per queued item
        return max(queue_position * 30, 60)  # Minimum 1 minute wait
    
    def _get_next_reset_time(self) -> datetime:
        """Get next quota reset time (midnight UTC)"""
        now = datetime.utcnow()
        next_reset = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return next_reset
    
    def _update_quota_cache(self, user_id: str, api_type: str, new_usage: int):
        """Update local quota cache"""
        cache_key = f"{user_id}:{api_type}"
        if cache_key in self._quota_cache:
            self._quota_cache[cache_key]["current_usage"] = new_usage
    
    async def _get_user_tier(self, user_id: str) -> str:
        """Get user tier (would integrate with user management system)"""
        # TODO: Integrate with actual user management system
        # For now, return default tier
        return "free"
    
    # ===== MONITORING AND ANALYTICS =====
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "redis_health": self.redis.health_check(),
            "api_metrics": {},
            "system_stats": {
                "total_users_active": len(self._quota_cache),
                "cache_entries": len(self._quota_cache),
                "config_loaded": bool(self.config)
            }
        }
        
        # Get metrics for each API
        today = datetime.utcnow().strftime("%Y-%m-%d")
        for api_type in APIType:
            api_metrics = self.redis.get_api_metrics(api_type.value, today)
            if api_metrics:
                metrics["api_metrics"][api_type.value] = api_metrics
        
        return metrics
    
    async def cleanup_expired_data(self) -> Dict[str, Any]:
        """Clean up expired cache and quota data"""
        
        # Clean Redis data
        redis_cleanup = self.redis.cleanup_expired_data()
        
        # Clean local cache
        now = datetime.utcnow()
        expired_keys = [
            key for key, expiry in self._cache_expiry.items() 
            if now > expiry
        ]
        
        for key in expired_keys:
            self._quota_cache.pop(key, None)
            self._cache_expiry.pop(key, None)
        
        return {
            "redis_cleanup": redis_cleanup,
            "local_cache_cleaned": len(expired_keys),
            "timestamp": now.isoformat()
        }


# Initialize singleton instance
rate_limiter_service = RateLimiterService()