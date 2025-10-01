"""
Background scheduler for periodic tasks like personality updates.
Uses APScheduler for reliable task scheduling.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from core.database.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: Optional[AsyncIOScheduler] = None


async def train_rl_model():
    """
    Background task to train the RL model on recent user interactions.
    Runs weekly to update recommendation parameters based on feedback.
    """
    try:
        logger.info("Starting RL model training...")
        
        from core.rl_orchestrator import get_rl_orchestrator
        
        orchestrator = get_rl_orchestrator()
        
        # Train on last 7 days of interactions
        training_results = await orchestrator.train_from_interactions(
            days_back=7,
            min_interactions_per_user=5
        )
        
        logger.info(f"RL training complete: {training_results}")
        
        # Also run evaluation
        evaluation_results = await orchestrator.evaluate_model(test_days=3)
        
        logger.info(f"Model evaluation: {evaluation_results}")
        
        # Log to database
        supabase = get_supabase_client()
        supabase.table("system_tasks").insert({
            "task_name": "rl_training",
            "executed_at": datetime.now().isoformat(),
            "status": "completed",
            "users_processed": training_results.get("users_trained", 0),
            "records_processed": training_results.get("total_updates", 0),
            "metadata": {
                "training": training_results,
                "evaluation": evaluation_results
            }
        }).execute()
        
    except Exception as e:
        logger.error(f"RL training task failed: {e}")
        
        # Log failure
        try:
            supabase = get_supabase_client()
            supabase.table("system_tasks").insert({
                "task_name": "rl_training",
                "executed_at": datetime.now().isoformat(),
                "status": "failed",
                "error_message": str(e)
            }).execute()
        except:
            pass


def get_scheduler() -> AsyncIOScheduler:
    """Get or create the global scheduler instance."""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
    return scheduler


async def update_all_user_personalities():
    """
    Background task to update personality profiles for all active users.
    This aggregates insights from chat and entertainment interactions.
    """
    try:
        logger.info("Starting scheduled personality update for all users...")
        
        supabase = get_supabase_client()
        
        # Get all users who have recent activity (last 7 days)
        from datetime import timedelta
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        # Get users with recent chat activity
        chat_users = supabase.table("chat_messages")\
            .select("user_id")\
            .gte("timestamp", seven_days_ago)\
            .execute()
        
        # Get users with recent entertainment activity
        entertainment_users = supabase.table("entertainment_interactions")\
            .select("user_id")\
            .gte("timestamp", seven_days_ago)\
            .execute()
        
        # Combine and deduplicate user IDs
        user_ids = set()
        if chat_users.data:
            user_ids.update([msg["user_id"] for msg in chat_users.data])
        if entertainment_users.data:
            user_ids.update([inter["user_id"] for inter in entertainment_users.data])
        
        logger.info(f"Found {len(user_ids)} active users to update")
        
        # Import here to avoid circular dependencies
        from api.routes.chat import update_personality_from_insights
        
        # Update each user's personality
        success_count = 0
        error_count = 0
        
        for user_id in user_ids:
            try:
                result = await update_personality_from_insights(user_id)
                if result.success and result.data.get("updated"):
                    success_count += 1
                    logger.info(f"Updated personality for user {user_id}: {result.data.get('insights_processed')} insights")
            except Exception as e:
                error_count += 1
                logger.error(f"Failed to update personality for user {user_id}: {e}")
        
        logger.info(f"Personality update complete: {success_count} successful, {error_count} errors")
        
        # Log the task completion
        supabase.table("system_tasks").insert({
            "task_name": "personality_update",
            "executed_at": datetime.now().isoformat(),
            "users_processed": len(user_ids),
            "successful_updates": success_count,
            "failed_updates": error_count,
            "status": "completed" if error_count == 0 else "completed_with_errors"
        }).execute()
        
    except Exception as e:
        logger.error(f"Personality update task failed: {e}")
        
        # Log the failure
        try:
            supabase = get_supabase_client()
            supabase.table("system_tasks").insert({
                "task_name": "personality_update",
                "executed_at": datetime.now().isoformat(),
                "status": "failed",
                "error_message": str(e)
            }).execute()
        except:
            pass


async def cleanup_old_insights():
    """
    Background task to clean up old personality insights (older than 90 days).
    Keeps database size manageable while retaining recent learning data.
    """
    try:
        logger.info("Starting cleanup of old personality insights...")
        
        supabase = get_supabase_client()
        ninety_days_ago = (datetime.now() - timedelta(days=90)).isoformat()
        
        # Delete old chat insights
        chat_result = supabase.table("chat_personality_insights")\
            .delete()\
            .lt("timestamp", ninety_days_ago)\
            .execute()
        
        # Delete old entertainment interactions (keep the records but clear personality_insights field)
        # This preserves interaction history while removing stale ML data
        entertainment_result = supabase.table("entertainment_interactions")\
            .update({"personality_insights": None})\
            .lt("timestamp", ninety_days_ago)\
            .is_("personality_insights", "not.null")\
            .execute()
        
        chat_deleted = len(chat_result.data) if chat_result.data else 0
        entertainment_cleaned = len(entertainment_result.data) if entertainment_result.data else 0
        
        logger.info(f"Cleanup complete: {chat_deleted} chat insights deleted, {entertainment_cleaned} entertainment insights cleared")
        
        # Log the task
        supabase.table("system_tasks").insert({
            "task_name": "insights_cleanup",
            "executed_at": datetime.now().isoformat(),
            "status": "completed",
            "records_processed": chat_deleted + entertainment_cleaned
        }).execute()
        
    except Exception as e:
        logger.error(f"Insights cleanup task failed: {e}")


def start_scheduler():
    """
    Start the background scheduler with all periodic tasks.
    Call this when the FastAPI application starts.
    """
    scheduler = get_scheduler()
    
    # Schedule personality updates - run daily at 2 AM
    scheduler.add_job(
        update_all_user_personalities,
        trigger=CronTrigger(hour=2, minute=0),
        id="personality_update",
        name="Update all user personalities",
        replace_existing=True
    )
    
    # Schedule insights cleanup - run weekly on Sunday at 3 AM
    scheduler.add_job(
        cleanup_old_insights,
        trigger=CronTrigger(day_of_week='sun', hour=3, minute=0),
        id="insights_cleanup",
        name="Clean up old personality insights",
        replace_existing=True
    )
    
    # Schedule RL training - run weekly on Monday at 1 AM
    scheduler.add_job(
        train_rl_model,
        trigger=CronTrigger(day_of_week='mon', hour=1, minute=0),
        id="rl_training",
        name="Train RL recommendation model",
        replace_existing=True
    )
    
    # For testing: also allow manual trigger via interval (commented out in production)
    # scheduler.add_job(
    #     update_all_user_personalities,
    #     trigger=IntervalTrigger(minutes=30),
    #     id="personality_update_frequent",
    #     name="Frequent personality updates (testing)",
    #     replace_existing=True
    # )
    
    scheduler.start()
    logger.info("Background scheduler started with personality update and RL training tasks")


def stop_scheduler():
    """
    Stop the background scheduler.
    Call this when the FastAPI application shuts down.
    """
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Background scheduler stopped")


def get_scheduled_jobs():
    """Get list of all scheduled jobs with their next run times."""
    scheduler = get_scheduler()
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })
    return jobs
