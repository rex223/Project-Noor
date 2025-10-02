"""
FastAPI middleware for rate limiting HTTP requests.
"""
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette import status

from utils.rate_limiter import RateLimitExceeded


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle rate limit errors globally.
    Converts RateLimitExceeded exceptions to HTTP 429 responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        
        except RateLimitExceeded as e:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit_exceeded",
                    "message": str(e),
                    "service": e.service,
                    "retry_after": e.retry_after
                },
                headers={
                    "Retry-After": str(e.retry_after),
                    "X-RateLimit-Service": e.service,
                }
            )


def get_rate_limit_headers(
    service: str,
    remaining: int,
    limit: int
) -> dict:
    """
    Generate standard rate limit headers for responses.
    
    Args:
        service: Service name
        remaining: Remaining requests
        limit: Total request limit
        
    Returns:
        Dictionary of headers to add to response
    """
    return {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Service": service,
    }
