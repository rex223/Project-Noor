"""
Main FastAPI application for Bondhu AI backend.
Provides API endpoints for personality analysis and agent management.
"""

import logging
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core import get_config, PersonalityOrchestrator
from api.routes import personality_router, agents_router
from api.routes.personality_context import router as personality_context_router
from api.routes.chat import router as chat_router
from core.database.supabase_client import cleanup_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("bondhu.main")

# Global instances
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global orchestrator
    
    # Startup
    logger.info("Starting Bondhu AI application")
    
    try:
        # Initialize configuration
        config = get_config()
        logger.info("Configuration loaded successfully")
        
        # Initialize database services
        from core.database.personality_service import get_personality_service
        personality_service = get_personality_service()
        logger.info("Database services initialized")
        
        # Initialize orchestrator
        orchestrator = PersonalityOrchestrator()
        logger.info("Orchestrator initialized successfully")
        
        # Perform health checks
        health_check = await orchestrator.health_check()
        if health_check["status"] == "healthy":
            logger.info("System health check passed")
        else:
            logger.warning(f"System health check issues: {health_check}")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    # Shutdown
    logger.info("Shutting down Bondhu AI application")
    try:
        await cleanup_database()
        logger.info("Database cleanup completed")
    except Exception as e:
        logger.error(f"Database cleanup error: {e}")

# Create FastAPI application
app = FastAPI(
    title="Bondhu AI API",
    description="Multi-agent personality analysis system for mental health companion",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(personality_router)
app.include_router(agents_router)
app.include_router(personality_context_router)
app.include_router(chat_router)

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Bondhu AI API",
        "version": "1.0.0",
        "description": "Multi-agent personality analysis system",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """System health check endpoint."""
    try:
        config = get_config()
        
        # Basic system checks
        health_info = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",  # Will be replaced with actual timestamp
            "version": "1.0.0",
            "components": {
                "api": "healthy",
                "config": "healthy" if config else "unhealthy",
                "orchestrator": "unknown"
            }
        }
        
        # Check orchestrator if available
        global orchestrator
        if orchestrator:
            orch_health = await orchestrator.health_check()
            health_info["components"]["orchestrator"] = orch_health["status"]
            health_info["orchestrator_details"] = orch_health
        
        # Set overall status
        component_statuses = list(health_info["components"].values())
        if "unhealthy" in component_statuses:
            health_info["status"] = "unhealthy"
        elif "degraded" in component_statuses:
            health_info["status"] = "degraded"
        
        return health_info
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested endpoint {request.url.path} was not found",
            "available_endpoints": [
                "/",
                "/health",
                "/docs",
                "/api/v1/personality/analyze",
                "/api/v1/agents/status"
            ]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": None  # Could add request tracking
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration
    config = get_config()
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.api_debug,
        log_level="info"
    )
