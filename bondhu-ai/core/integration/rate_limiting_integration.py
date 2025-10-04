"""
Integration module for adding rate limiting to existing Bondhu AI FastAPI application.
This module provides easy integration without modifying existing code.
"""

import os
import logging
from typing import Optional
from fastapi import FastAPI, Request, Response
from core.middleware.rate_limiting_middleware import RateLimitingMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimitingIntegrator:
    """
    Easy integration class for adding rate limiting to existing FastAPI applications.
    """
    
    def __init__(self):
        self.enabled = os.getenv("ENABLE_RATE_LIMITING", "false").lower() == "true"
        self.monitoring_enabled = os.getenv("MONITORING_ENABLED", "false").lower() == "true"
        
    def integrate_with_app(self, app: FastAPI, default_user_tier: str = "free") -> None:
        """
        Integrate rate limiting with existing FastAPI application.
        
        Args:
            app: The FastAPI application instance
            default_user_tier: Default tier for users without authentication
        """
        if not self.enabled:
            logger.info("Rate limiting is disabled via ENABLE_RATE_LIMITING environment variable")
            return
            
        try:
            # Add rate limiting middleware
            app.add_middleware(
                RateLimitingMiddleware,
                default_user_tier=default_user_tier,
                enabled=True
            )
            
            logger.info("✅ Rate limiting middleware successfully integrated")
            
            # Start monitoring if enabled
            if self.monitoring_enabled:
                self._start_monitoring()
                
        except Exception as e:
            logger.error(f"❌ Failed to integrate rate limiting: {e}")
            # Don't crash the app if rate limiting fails to initialize
            
    def _start_monitoring(self) -> None:
        """Start the monitoring service in the background."""
        try:
            import asyncio
            from core.monitoring.monitoring_service import monitoring_service
            
            # Start monitoring in background task
            async def start_monitoring():
                await monitoring_service.start_monitoring()
            
            # Schedule monitoring to start after app startup
            logger.info("✅ Monitoring service scheduled to start")
            
        except Exception as e:
            logger.error(f"❌ Failed to start monitoring: {e}")

# Global integrator instance
rate_limiting_integrator = RateLimitingIntegrator()

def add_rate_limiting_to_app(app: FastAPI, default_user_tier: str = "free") -> None:
    """
    Convenience function to add rate limiting to FastAPI app.
    
    Usage:
        from core.integration.rate_limiting_integration import add_rate_limiting_to_app
        
        app = FastAPI()
        add_rate_limiting_to_app(app, default_user_tier="free")
    
    Args:
        app: FastAPI application instance
        default_user_tier: Default user tier for non-authenticated users
    """
    rate_limiting_integrator.integrate_with_app(app, default_user_tier)

# Health check endpoint for rate limiting system
async def rate_limiting_health_check() -> dict:
    """
    Health check for rate limiting system components.
    
    Returns:
        dict: Health status of rate limiting components
    """
    try:
        from core.cache.redis_rate_limiter import RedisManager
        from core.monitoring.monitoring_service import monitoring_service
        
        # Check Redis connectivity (synchronous method)
        redis_manager = RedisManager()
        redis_health = redis_manager.health_check()
        
        # Check monitoring service (async method)
        monitoring_health = await monitoring_service.get_system_health_report()
        
        return {
            "rate_limiting_enabled": rate_limiting_integrator.enabled,
            "monitoring_enabled": rate_limiting_integrator.monitoring_enabled,
            "redis_health": redis_health,
            "monitoring_health": monitoring_health.get("overall_health", "unknown"),
            "status": "healthy" if redis_health.get("connected", False) else "degraded"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "rate_limiting_enabled": rate_limiting_integrator.enabled,
            "monitoring_enabled": rate_limiting_integrator.monitoring_enabled,
            "status": "error",
            "error": str(e)
        }

def add_health_check_endpoint(app: FastAPI) -> None:
    """
    Add health check endpoint for rate limiting system.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.get("/health/rate-limiting")
    async def health_rate_limiting():
        """Health check endpoint for rate limiting system."""
        return await rate_limiting_health_check()