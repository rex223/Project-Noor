"""
FastAPI middleware for centralized API rate limiting.

Intercepts incoming requests and applies rate limiting before they reach
the endpoint handlers. Integrates with centralized rate limiting system.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from core.services.rate_limiter_service import (
    rate_limiter_service,
    RateLimitResult,
    RequestPriority,
    APIQuotaExceeded
)

logger = logging.getLogger("bondhu.middleware.rate_limiter")


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for request-level rate limiting"""
    
    def __init__(
        self,
        app: ASGIApp,
        enabled: bool = True,
        excluded_paths: Optional[list] = None,
        default_user_tier: str = "free"
    ):
        """
        Initialize rate limiting middleware
        
        Args:
            app: ASGI application
            enabled: Whether rate limiting is enabled
            excluded_paths: List of paths to exclude from rate limiting
            default_user_tier: Default user tier when not specified
        """
        super().__init__(app)
        self.enabled = enabled
        self.excluded_paths = excluded_paths or [
            "/health",
            "/metrics", 
            "/docs",
            "/openapi.json",
            "/favicon.ico"
        ]
        self.default_user_tier = default_user_tier
        self.rate_limiter = rate_limiter_service
        
        # Request tracking for global rate limiting
        self.request_counts = {}
        self.last_reset_time = time.time()
        
        logger.info(f"RateLimitingMiddleware initialized (enabled: {enabled})")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through rate limiting pipeline"""
        
        # Skip rate limiting if disabled or path excluded
        if not self.enabled or self._is_path_excluded(request.url.path):
            return await call_next(request)
        
        # Extract user information
        user_info = await self._extract_user_info(request)
        if not user_info:
            # Allow anonymous requests but with strict limits
            return await self._handle_anonymous_request(request, call_next)
        
        user_id = user_info["user_id"]
        user_tier = user_info.get("user_tier", self.default_user_tier)
        
        # Determine API type from request
        api_info = self._determine_api_info(request)
        if not api_info:
            # Not an API request that needs rate limiting
            return await call_next(request)
        
        api_type = api_info["api_type"]
        operation = api_info["operation"]
        priority = api_info.get("priority", RequestPriority.MEDIUM)
        
        # Apply rate limiting
        try:
            start_time = time.time()
            
            # Check global rate limits first
            if not await self._check_global_limits(request):
                return self._create_rate_limit_response(
                    "Global rate limit exceeded. Please try again later.",
                    429
                )
            
            # Extract request data for caching
            request_data = await self._extract_request_data(request, operation)
            
            # Check quota and rate limits
            result, metadata = await self.rate_limiter.check_and_consume_quota(
                user_id, user_tier, api_type, operation, request_data, priority
            )
            
            # Handle rate limiting results
            if result == RateLimitResult.CACHED:
                # Serve from cache
                logger.debug(f"Serving cached response for {user_id}:{api_type}:{operation}")
                return self._create_cached_response(metadata["cached_data"])
            
            elif result == RateLimitResult.ALLOWED:
                # Process request normally
                response = await call_next(request)
                
                # Track timing and success
                response_time = (time.time() - start_time) * 1000
                success = 200 <= response.status_code < 400
                
                # Cache successful responses
                if success and hasattr(response, 'body'):
                    await self._cache_response(
                        user_id, api_type, operation, request_data, response
                    )
                
                # Add rate limiting headers
                self._add_rate_limit_headers(response, metadata)
                
                return response
            
            elif result == RateLimitResult.QUEUED:
                # Request queued due to quota exceeded
                return self._create_queued_response(metadata)
            
            else:
                # Request denied
                return self._create_rate_limit_response(
                    metadata.get("error", "Rate limit exceeded"),
                    429
                )
        
        except APIQuotaExceeded as e:
            logger.warning(f"API quota exceeded: {e}")
            return self._create_quota_exceeded_response(e)
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Fall back to processing request without rate limiting
            return await call_next(request)
    
    def _is_path_excluded(self, path: str) -> bool:
        """Check if path should be excluded from rate limiting"""
        return any(excluded in path for excluded in self.excluded_paths)
    
    async def _extract_user_info(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extract user ID and tier from request"""
        
        # Try to get user info from different sources
        user_info = {}
        
        # 1. From path parameters (e.g., /api/v1/video/recommendations/{user_id})
        path_params = request.path_params
        if "user_id" in path_params:
            user_info["user_id"] = path_params["user_id"]
        
        # 2. From query parameters
        query_params = request.query_params
        if "user_id" in query_params:
            user_info["user_id"] = query_params["user_id"]
        
        # 3. From headers (for API keys, auth tokens)
        headers = request.headers
        if "x-user-id" in headers:
            user_info["user_id"] = headers["x-user-id"]
        if "x-user-tier" in headers:
            user_info["user_tier"] = headers["x-user-tier"]
        
        # 4. From JWT token (if implemented)
        # TODO: Add JWT token parsing for user_id and tier
        
        # 5. From request body (for POST requests)
        if request.method == "POST" and "user_id" not in user_info:
            try:
                body = await request.body()
                if body:
                    body_data = json.loads(body)
                    if "user_id" in body_data:
                        user_info["user_id"] = body_data["user_id"]
                    if "user_tier" in body_data:
                        user_info["user_tier"] = body_data["user_tier"]
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        
        return user_info if "user_id" in user_info else None
    
    def _determine_api_info(self, request: Request) -> Optional[Dict[str, Any]]:
        """Determine API type and operation from request"""
        
        path = request.url.path
        method = request.method
        
        # YouTube API endpoints
        if "/video/" in path:
            if "recommendations" in path:
                return {
                    "api_type": "youtube",
                    "operation": "search",  # Recommendations use search
                    "priority": RequestPriority.HIGH
                }
            elif "trending" in path:
                return {
                    "api_type": "youtube", 
                    "operation": "trending_videos",
                    "priority": RequestPriority.LOW
                }
            elif "feedback" in path:
                return {
                    "api_type": "youtube",
                    "operation": "video_details",
                    "priority": RequestPriority.MEDIUM
                }
        
        # Music/Spotify API endpoints
        elif "/music/" in path:
            return {
                "api_type": "spotify",
                "operation": "search_tracks",
                "priority": RequestPriority.MEDIUM
            }
        
        # Gaming API endpoints
        elif "/gaming/" in path:
            return {
                "api_type": "gaming", 
                "operation": "steam_stats",
                "priority": RequestPriority.MEDIUM
            }
        
        # Chat/OpenAI API endpoints
        elif "/chat/" in path:
            return {
                "api_type": "openai",
                "operation": "chat_completion",
                "priority": RequestPriority.HIGH
            }
        
        return None
    
    async def _extract_request_data(self, request: Request, operation: str) -> Dict[str, Any]:
        """Extract relevant data from request for caching"""
        
        request_data = {
            "operation": operation,
            "method": request.method,
            "path": request.url.path
        }
        
        # Add query parameters
        query_params = dict(request.query_params)
        if query_params:
            request_data.update(query_params)
        
        # Add body data for POST requests
        if request.method == "POST":
            try:
                body = await request.body()
                if body:
                    body_data = json.loads(body)
                    # Only include non-sensitive fields
                    safe_fields = [
                        "query", "max_results", "category_filter", 
                        "include_trending", "force_refresh"
                    ]
                    for field in safe_fields:
                        if field in body_data:
                            request_data[field] = body_data[field]
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        
        return request_data
    
    async def _check_global_limits(self, request: Request) -> bool:
        """Check global rate limits (requests per second, etc.)"""
        
        current_time = time.time()
        
        # Reset counters every minute
        if current_time - self.last_reset_time > 60:
            self.request_counts = {}
            self.last_reset_time = current_time
        
        # Count requests per IP
        client_ip = request.client.host if request.client else "unknown"
        self.request_counts[client_ip] = self.request_counts.get(client_ip, 0) + 1
        
        # Check global limits (could be configurable)
        global_limit_per_minute = 1000  # Global limit
        ip_limit_per_minute = 100       # Per-IP limit
        
        if self.request_counts[client_ip] > ip_limit_per_minute:
            logger.warning(f"IP rate limit exceeded: {client_ip}")
            return False
        
        total_requests = sum(self.request_counts.values())
        if total_requests > global_limit_per_minute:
            logger.warning(f"Global rate limit exceeded: {total_requests}")
            return False
        
        return True
    
    async def _handle_anonymous_request(self, request: Request, call_next: Callable) -> Response:
        """Handle requests without user identification"""
        
        # Apply strict rate limiting for anonymous requests
        client_ip = request.client.host if request.client else "anonymous"
        
        # Use IP-based rate limiting
        # TODO: Implement IP-based rate limiting with Redis
        
        # For now, allow through with warning
        logger.warning(f"Anonymous request from {client_ip}: {request.url.path}")
        return await call_next(request)
    
    async def _cache_response(
        self, 
        user_id: str, 
        api_type: str, 
        operation: str, 
        request_data: Dict[str, Any], 
        response: Response
    ):
        """Cache successful response for future requests"""
        
        try:
            # Only cache GET requests and successful responses
            if request_data.get("method") == "GET" and 200 <= response.status_code < 300:
                
                # Extract response body
                if hasattr(response, 'body'):
                    response_body = response.body
                    if isinstance(response_body, bytes):
                        response_data = json.loads(response_body.decode())
                        
                        # Cache the response
                        await self.rate_limiter.cache_response(
                            user_id, api_type, operation, request_data, response_data
                        )
                        
        except Exception as e:
            logger.error(f"Failed to cache response: {e}")
    
    def _create_cached_response(self, cached_data: Any) -> JSONResponse:
        """Create response from cached data"""
        return JSONResponse(
            content={
                "success": True,
                "data": cached_data,
                "cached": True,
                "timestamp": datetime.utcnow().isoformat()
            },
            headers={"X-Cache-Status": "HIT"}
        )
    
    def _create_queued_response(self, metadata: Dict[str, Any]) -> JSONResponse:
        """Create response for queued requests"""
        return JSONResponse(
            content={
                "success": False,
                "error": "Request queued due to quota limit",
                "queue_position": metadata.get("queue_position", 0),
                "estimated_wait_time": metadata.get("estimated_wait_time", 60),
                "quota_usage": metadata.get("quota_usage", 0),
                "quota_limit": metadata.get("quota_limit", 0),
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=429,
            headers={
                "Retry-After": str(metadata.get("estimated_wait_time", 60)),
                "X-Queue-Position": str(metadata.get("queue_position", 0))
            }
        )
    
    def _create_rate_limit_response(self, message: str, status_code: int = 429) -> JSONResponse:
        """Create rate limit exceeded response"""
        return JSONResponse(
            content={
                "success": False,
                "error": message,
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=status_code,
            headers={"Retry-After": "60"}
        )
    
    def _create_quota_exceeded_response(self, error: APIQuotaExceeded) -> JSONResponse:
        """Create quota exceeded response"""
        return JSONResponse(
            content={
                "success": False,
                "error": f"API quota exceeded for {error.api_type}",
                "current_usage": error.current_usage,
                "limit": error.limit,
                "user_id": error.user_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=429,
            headers={"Retry-After": "3600"}  # Retry after 1 hour
        )
    
    def _add_rate_limit_headers(self, response: Response, metadata: Dict[str, Any]):
        """Add rate limiting headers to response"""
        
        if "quota_remaining" in metadata:
            response.headers["X-Rate-Limit-Remaining"] = str(metadata["quota_remaining"])
        if "quota_limit" in metadata:
            response.headers["X-Rate-Limit-Limit"] = str(metadata["quota_limit"])
        if "quota_usage" in metadata:
            response.headers["X-Rate-Limit-Used"] = str(metadata["quota_usage"])
        
        response.headers["X-Rate-Limit-Reset"] = "86400"  # Daily reset


# Utility function to add middleware to FastAPI app
def add_rate_limiting_middleware(
    app,
    enabled: bool = True,
    excluded_paths: Optional[list] = None,
    default_user_tier: str = "free"
):
    """Add rate limiting middleware to FastAPI application"""
    
    middleware = RateLimitingMiddleware(
        app=app,
        enabled=enabled,
        excluded_paths=excluded_paths,
        default_user_tier=default_user_tier
    )
    
    app.add_middleware(BaseHTTPMiddleware, dispatch=middleware.dispatch)
    logger.info("Rate limiting middleware added to FastAPI application")