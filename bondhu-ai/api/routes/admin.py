"""
Admin API endpoints for system management and manual task triggering.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel

from core.scheduler import (
    update_all_user_personalities,
    cleanup_old_insights,
    train_rl_model,
    get_scheduled_jobs
)
from core.database.supabase_client import get_supabase_client
from api.models.schemas import APIResponse

# Create router
admin_router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

logger = logging.getLogger(__name__)


class TaskTriggerResponse(BaseModel):
    """Response for manual task trigger."""
    task_name: str
    triggered_at: str
    status: str
    message: str


class SystemHealthResponse(BaseModel):
    """System health check response."""
    status: str
    scheduler_running: bool
    scheduled_jobs: list
    last_personality_update: Dict[str, Any] | None
    active_users_count: int


@admin_router.post("/tasks/personality-update/trigger")
async def trigger_personality_update(
    x_admin_key: str = Header(None, description="Admin API key for authentication")
) -> APIResponse[TaskTriggerResponse]:
    """
    Manually trigger personality update for all active users.
    
    Requires admin authentication via X-Admin-Key header.
    """
    # Simple API key authentication (in production, use proper auth)
    # TODO: Move admin key to environment variable
    if x_admin_key != "admin-dev-key-change-in-production":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key"
        )
    
    try:
        logger.info("Manual personality update triggered via admin API")
        
        # Run the update task
        await update_all_user_personalities()
        
        return APIResponse[TaskTriggerResponse](
            success=True,
            data=TaskTriggerResponse(
                task_name="personality_update",
                triggered_at=datetime.now().isoformat(),
                status="completed",
                message="Personality update task executed successfully"
            ),
            message="Task completed"
        )
        
    except Exception as e:
        logger.error(f"Manual personality update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task execution failed: {str(e)}"
        )


@admin_router.post("/tasks/insights-cleanup/trigger")
async def trigger_insights_cleanup(
    x_admin_key: str = Header(None, description="Admin API key for authentication")
) -> APIResponse[TaskTriggerResponse]:
    """
    Manually trigger cleanup of old personality insights.
    
    Requires admin authentication via X-Admin-Key header.
    """
    if x_admin_key != "admin-dev-key-change-in-production":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key"
        )
    
    try:
        logger.info("Manual insights cleanup triggered via admin API")
        
        # Run the cleanup task
        await cleanup_old_insights()
        
        return APIResponse[TaskTriggerResponse](
            success=True,
            data=TaskTriggerResponse(
                task_name="insights_cleanup",
                triggered_at=datetime.now().isoformat(),
                status="completed",
                message="Insights cleanup task executed successfully"
            ),
            message="Task completed"
        )
        
    except Exception as e:
        logger.error(f"Manual insights cleanup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task execution failed: {str(e)}"
        )


@admin_router.post("/tasks/rl-training/trigger")
async def trigger_rl_training(
    x_admin_key: str = Header(None, description="Admin API key for authentication"),
    days_back: int = 7,
    min_interactions: int = 5
) -> APIResponse[TaskTriggerResponse]:
    """
    Manually trigger RL model training.
    
    Args:
        days_back: Number of days of data to train on
        min_interactions: Minimum interactions required per user
    
    Requires admin authentication via X-Admin-Key header.
    """
    if x_admin_key != "admin-dev-key-change-in-production":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key"
        )
    
    try:
        logger.info(f"Manual RL training triggered via admin API (days_back={days_back})")
        
        # Run the training task
        await train_rl_model()
        
        return APIResponse[TaskTriggerResponse](
            success=True,
            data=TaskTriggerResponse(
                task_name="rl_training",
                triggered_at=datetime.now().isoformat(),
                status="completed",
                message=f"RL training completed with {days_back} days of data"
            ),
            message="Task completed"
        )
        
    except Exception as e:
        logger.error(f"Manual RL training failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task execution failed: {str(e)}"
        )


@admin_router.get("/system/health")
async def get_system_health(
    x_admin_key: str = Header(None, description="Admin API key for authentication")
) -> APIResponse[SystemHealthResponse]:
    """
    Get system health status including scheduler status and task history.
    
    Requires admin authentication via X-Admin-Key header.
    """
    if x_admin_key != "admin-dev-key-change-in-production":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key"
        )
    
    try:
        from core.scheduler import get_scheduler
        
        scheduler = get_scheduler()
        scheduled_jobs = get_scheduled_jobs()
        
        # Get last personality update task
        supabase = get_supabase_client()
        last_task = supabase.table("system_tasks")\
            .select("*")\
            .eq("task_name", "personality_update")\
            .order("executed_at", desc=True)\
            .limit(1)\
            .execute()
        
        # Count active users (last 7 days)
        from datetime import timedelta
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        active_users = supabase.table("chat_messages")\
            .select("user_id", count="exact")\
            .gte("timestamp", seven_days_ago)\
            .execute()
        
        return APIResponse[SystemHealthResponse](
            success=True,
            data=SystemHealthResponse(
                status="healthy",
                scheduler_running=scheduler.running if scheduler else False,
                scheduled_jobs=scheduled_jobs,
                last_personality_update=last_task.data[0] if last_task.data else None,
                active_users_count=active_users.count if active_users else 0
            ),
            message="System health retrieved"
        )
        
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system health: {str(e)}"
        )


@admin_router.get("/tasks/history")
async def get_task_history(
    x_admin_key: str = Header(None, description="Admin API key for authentication"),
    limit: int = 50
) -> APIResponse[list]:
    """
    Get history of scheduled task executions.
    
    Requires admin authentication via X-Admin-Key header.
    """
    if x_admin_key != "admin-dev-key-change-in-production":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key"
        )
    
    try:
        supabase = get_supabase_client()
        
        tasks = supabase.table("system_tasks")\
            .select("*")\
            .order("executed_at", desc=True)\
            .limit(limit)\
            .execute()
        
        return APIResponse[list](
            success=True,
            data=tasks.data or [],
            message=f"Retrieved {len(tasks.data) if tasks.data else 0} task records"
        )
        
    except Exception as e:
        logger.error(f"Failed to get task history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task history: {str(e)}"
        )
