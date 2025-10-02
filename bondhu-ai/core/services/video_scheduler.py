"""
Background scheduler service for video recommendation refresh.
Handles automatic refresh 3 times daily and manages refresh scheduling.
"""

import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional
import schedule
from threading import Thread
import time as time_module

from agents.video.video_agent import VideoIntelligenceAgent
from core.rl.video_recommendation_rl import VideoRecommendationRL
from core.database.personality_service import get_personality_service
from core.database.models import PersonalityTrait  # Use Enum, not Pydantic model


class VideoRecommendationScheduler:
    """
    Background scheduler for automatic video recommendation refresh.
    Refreshes recommendations 3 times daily: morning, afternoon, evening.
    """
    
    def __init__(self):
        """Initialize the scheduler."""
        self.logger = logging.getLogger("bondhu.video_scheduler")
        self.active_users: Dict[str, VideoIntelligenceAgent] = {}
        self.rl_systems: Dict[str, VideoRecommendationRL] = {}
        self.is_running = False
        self.scheduler_thread: Optional[Thread] = None
        
        # Refresh times (24-hour format)
        self.refresh_times = [
            time(8, 0),   # 8:00 AM - Morning recommendations
            time(14, 0),  # 2:00 PM - Afternoon recommendations  
            time(20, 0)   # 8:00 PM - Evening recommendations
        ]
        
        self.setup_schedule()

    def setup_schedule(self):
        """Setup the automatic refresh schedule."""
        for refresh_time in self.refresh_times:
            schedule.every().day.at(refresh_time.strftime("%H:%M")).do(
                self._run_scheduled_refresh
            )
        
        self.logger.info(f"Scheduled video recommendations refresh at: {[t.strftime('%H:%M') for t in self.refresh_times]}")

    def start(self):
        """Start the background scheduler."""
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.scheduler_thread = Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Video recommendation scheduler started")

    def stop(self):
        """Stop the background scheduler."""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("Video recommendation scheduler stopped")

    def register_user(self, user_id: str) -> bool:
        """
        Register a user for automatic recommendation refresh.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if user was registered successfully
        """
        try:
            if user_id not in self.active_users:
                # Don't initialize agents until needed - just mark user as active
                self.active_users[user_id] = None  # Will be lazily initialized
                self.rl_systems[user_id] = None
                
                self.logger.info(f"Registered user {user_id} for automatic refresh")
                return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering user {user_id}: {e}")
            return False

    def unregister_user(self, user_id: str) -> bool:
        """
        Unregister a user from automatic recommendation refresh.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if user was unregistered successfully
        """
        try:
            if user_id in self.active_users:
                del self.active_users[user_id]
            
            if user_id in self.rl_systems:
                del self.rl_systems[user_id]
            
            self.logger.info(f"Unregistered user {user_id} from automatic refresh")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unregistering user {user_id}: {e}")
            return False

    async def refresh_user_recommendations(self, user_id: str, force: bool = False) -> bool:
        """
        Refresh recommendations for a specific user.
        
        Args:
            user_id: User identifier
            force: Whether to force refresh even if not scheduled
            
        Returns:
            True if refresh was successful
        """
        try:
            if user_id not in self.active_users:
                if not self.register_user(user_id):
                    return False
            
            # Lazily initialize agent if needed
            if self.active_users[user_id] is None:
                self.active_users[user_id] = VideoIntelligenceAgent(user_id)
            
            if self.rl_systems[user_id] is None:
                self.rl_systems[user_id] = VideoRecommendationRL(user_id)
            
            video_agent = self.active_users[user_id]
            
            # Check if refresh is needed
            if not force and not video_agent.should_refresh_recommendations():
                self.logger.debug(f"Skipping refresh for user {user_id} - not scheduled")
                return True
            
            # Get user's personality profile
            personality_service = get_personality_service()
            user_context = await personality_service.get_user_personality_context(user_id)
            
            if not user_context.has_assessment:
                self.logger.warning(f"User {user_id} has no personality assessment - using defaults")
                # Use default balanced personality
                personality_profile = {
                    PersonalityTrait.OPENNESS: 0.5,
                    PersonalityTrait.CONSCIENTIOUSNESS: 0.5,
                    PersonalityTrait.EXTRAVERSION: 0.5,
                    PersonalityTrait.AGREEABLENESS: 0.5,
                    PersonalityTrait.NEUROTICISM: 0.5
                }
            else:
                # Convert personality profile
                personality_profile = {}
                for trait in PersonalityTrait:
                    score = getattr(user_context.personality_profile.scores, trait.value, 50)
                    personality_profile[trait] = score / 100.0
            
            # Get user's watch history (would typically come from database)
            watch_history = []  # This would be populated from user's actual history
            
            # Refresh recommendations
            recommendations = await video_agent.get_personalized_recommendations(
                personality_profile=personality_profile,
                watch_history=watch_history,
                max_results=25,
                force_refresh=True
            )
            
            self.logger.info(f"Successfully refreshed {len(recommendations)} recommendations for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error refreshing recommendations for user {user_id}: {e}")
            return False

    async def refresh_all_users(self) -> Dict[str, bool]:
        """
        Refresh recommendations for all registered users.
        
        Returns:
            Dictionary mapping user_id to refresh success status
        """
        results = {}
        
        if not self.active_users:
            self.logger.info("No active users to refresh")
            return results
        
        self.logger.info(f"Starting scheduled refresh for {len(self.active_users)} users")
        
        # Process users in batches to avoid overwhelming the system
        batch_size = 10
        user_ids = list(self.active_users.keys())
        
        for i in range(0, len(user_ids), batch_size):
            batch = user_ids[i:i + batch_size]
            batch_tasks = []
            
            for user_id in batch:
                task = self.refresh_user_recommendations(user_id, force=True)
                batch_tasks.append((user_id, task))
            
            # Execute batch
            for user_id, task in batch_tasks:
                try:
                    result = await task
                    results[user_id] = result
                except Exception as e:
                    self.logger.error(f"Error in batch refresh for user {user_id}: {e}")
                    results[user_id] = False
            
            # Small delay between batches
            if i + batch_size < len(user_ids):
                await asyncio.sleep(1)
        
        successful_refreshes = sum(1 for success in results.values() if success)
        self.logger.info(f"Completed scheduled refresh: {successful_refreshes}/{len(results)} users successful")
        
        return results

    def get_next_refresh_time(self) -> Optional[datetime]:
        """
        Get the next scheduled refresh time.
        
        Returns:
            Next refresh datetime or None if no schedule
        """
        try:
            now = datetime.now()
            today = now.date()
            
            # Check if any refresh time today is still in the future
            for refresh_time in self.refresh_times:
                refresh_datetime = datetime.combine(today, refresh_time)
                if refresh_datetime > now:
                    return refresh_datetime
            
            # All today's refreshes are past, return first refresh time tomorrow
            tomorrow = today + timedelta(days=1)
            next_refresh = datetime.combine(tomorrow, self.refresh_times[0])
            return next_refresh
            
        except Exception as e:
            self.logger.error(f"Error calculating next refresh time: {e}")
            return None

    def get_scheduler_status(self) -> Dict[str, any]:
        """
        Get current status of the scheduler.
        
        Returns:
            Dictionary with scheduler status information
        """
        return {
            "is_running": self.is_running,
            "active_users": len(self.active_users),
            "refresh_times": [t.strftime("%H:%M") for t in self.refresh_times],
            "next_refresh": self.get_next_refresh_time().isoformat() if self.get_next_refresh_time() else None,
            "last_refresh": getattr(self, '_last_refresh_time', None),
            "refresh_count_today": getattr(self, '_refresh_count_today', 0)
        }

    def _scheduler_loop(self):
        """Main scheduler loop running in background thread."""
        self.logger.info("Scheduler loop started")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time_module.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time_module.sleep(60)
        
        self.logger.info("Scheduler loop stopped")

    def _run_scheduled_refresh(self):
        """Run the scheduled refresh (called by schedule library)."""
        try:
            self.logger.info("Starting scheduled video recommendation refresh")
            
            # Record refresh time
            self._last_refresh_time = datetime.now().isoformat()
            self._refresh_count_today = getattr(self, '_refresh_count_today', 0) + 1
            
            # Run async refresh in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                results = loop.run_until_complete(self.refresh_all_users())
                successful = sum(1 for success in results.values() if success)
                self.logger.info(f"Scheduled refresh completed: {successful}/{len(results)} successful")
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"Error in scheduled refresh: {e}")

    def manual_refresh_trigger(self, user_id: str) -> bool:
        """
        Trigger manual refresh for a user (called from API).
        
        Args:
            user_id: User identifier
            
        Returns:
            True if refresh was triggered successfully
        """
        try:
            # Ensure user is registered and agent is initialized
            if user_id not in self.active_users or self.active_users.get(user_id) is None:
                self.register_user(user_id)
                self.active_users[user_id] = VideoIntelligenceAgent(user_id)

            # Force immediate refresh by clearing cache
            video_agent = self.active_users[user_id]
            video_agent.recommendation_cache = {}
            video_agent.last_refresh_time = None
            
            self.logger.info(f"Manual refresh triggered for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error triggering manual refresh for user {user_id}: {e}")
            return False


# Global scheduler instance
_scheduler_instance: Optional[VideoRecommendationScheduler] = None

def get_video_scheduler() -> VideoRecommendationScheduler:
    """Get the global video recommendation scheduler instance."""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = VideoRecommendationScheduler()
    return _scheduler_instance

def start_video_scheduler():
    """Start the global video recommendation scheduler."""
    scheduler = get_video_scheduler()
    scheduler.start()

def stop_video_scheduler():
    """Stop the global video recommendation scheduler."""
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.stop()
        _scheduler_instance = None