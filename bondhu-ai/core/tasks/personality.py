"""
Personality-related background tasks
Handles sentiment analysis, personality learning, and profile updates
"""

import logging
import json
from datetime import datetime, timedelta
from statistics import mean, stdev
from typing import Dict, List, Optional

from core.celery_app import celery_app
from core.database.supabase_client import get_supabase_client
from core.cache.redis_client import get_redis, cache_set, cache_delete

logger = logging.getLogger("bondhu.tasks.personality")


@celery_app.task(bind=True, max_retries=3)
def analyze_chat_sentiment_batch(self, user_id: str) -> Dict:
    """
    Analyze recent chat messages and update personality profile based on sentiment.
    
    This task:
    1. Fetches recent chat messages (last 24 hours)
    2. Analyzes sentiment patterns
    3. Updates personality insights
    4. Caches results in Redis
    5. Updates user profile in Supabase
    
    Args:
        user_id: User's unique ID
        
    Returns:
        dict: Analysis results with status and insights
    """
    try:
        logger.info(f"Starting sentiment analysis for user {user_id}")
        
        supabase = get_supabase_client()
        redis_client = get_redis()
        
        # Fetch recent messages (last 24 hours)
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        
        result = supabase.table('chat_messages') \
            .select('sentiment_score, mood_detected, created_at') \
            .eq('user_id', user_id) \
            .eq('sender_type', 'user') \
            .gte('created_at', cutoff) \
            .order('created_at', desc=False) \
            .execute()
        
        messages = result.data
        
        if len(messages) < 5:
            logger.info(f"Insufficient data for user {user_id}: {len(messages)} messages")
            return {'status': 'insufficient_data', 'message_count': len(messages)}
        
        # Calculate sentiment statistics
        scores = [float(msg['sentiment_score']) for msg in messages if msg['sentiment_score'] is not None]
        
        if not scores:
            return {'status': 'no_sentiment_data'}
        
        avg_sentiment = mean(scores)
        sentiment_volatility = stdev(scores) if len(scores) > 1 else 0.0
        
        # Detect dominant mood
        moods = [msg['mood_detected'] for msg in messages if msg['mood_detected']]
        mood_counts: Dict[str, int] = {}
        for mood in moods:
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        dominant_mood = max(mood_counts, key=mood_counts.get) if mood_counts else 'neutral'
        
        # Trend analysis (compare with previous period)
        prev_cutoff = (datetime.now() - timedelta(hours=48)).isoformat()
        prev_result = supabase.table('chat_messages') \
            .select('sentiment_score') \
            .eq('user_id', user_id) \
            .eq('sender_type', 'user') \
            .gte('created_at', prev_cutoff) \
            .lt('created_at', cutoff) \
            .execute()
        
        prev_scores = [float(msg['sentiment_score']) for msg in prev_result.data if msg['sentiment_score']]
        sentiment_trend = 'stable'
        if prev_scores:
            prev_avg = mean(prev_scores)
            diff = avg_sentiment - prev_avg
            if diff > 0.1:
                sentiment_trend = 'improving'
            elif diff < -0.1:
                sentiment_trend = 'declining'
        
        # Build insights
        insights = {
            'avg_sentiment_24h': round(avg_sentiment, 2),
            'sentiment_volatility': round(sentiment_volatility, 2),
            'sentiment_trend': sentiment_trend,
            'dominant_mood': dominant_mood,
            'mood_distribution': mood_counts,
            'message_count_24h': len(messages),
            'analyzed_at': datetime.now().isoformat()
        }
        
        # Determine communication style adjustments
        personality_updates = {}
        
        if avg_sentiment < 0.3:
            # User showing signs of negative mood
            personality_updates['needs_support'] = True
            personality_updates['communication_style'] = 'empathetic_supportive'
            personality_updates['tone'] = 'gentle_caring'
        elif avg_sentiment > 0.7:
            # User in positive mood
            personality_updates['communication_style'] = 'enthusiastic_energetic'
            personality_updates['tone'] = 'upbeat_motivating'
        else:
            personality_updates['communication_style'] = 'balanced_friendly'
            personality_updates['tone'] = 'warm_supportive'
        
        if sentiment_volatility > 0.3:
            # High emotional variability
            personality_updates['emotional_stability'] = 'variable'
            personality_updates['requires_consistency'] = True
        else:
            personality_updates['emotional_stability'] = 'stable'
        
        # Store insights in Redis (1 hour TTL)
        cache_key = f"personality:sentiment:{user_id}"
        cache_set(cache_key, json.dumps(insights), 3600)
        
        # Update personality profile in Supabase
        try:
            # Get current profile
            profile = supabase.table('profiles') \
                .select('personality_data') \
                .eq('id', user_id) \
                .single() \
                .execute()
            
            current_personality = profile.data.get('personality_data', {}) or {}
            
            # Merge with new insights
            current_personality['chat_insights'] = insights
            current_personality['adaptive_style'] = personality_updates
            current_personality['last_updated'] = datetime.now().isoformat()
            
            # Update profile
            supabase.table('profiles') \
                .update({'personality_data': current_personality}) \
                .eq('id', user_id) \
                .execute()
            
            logger.info(f"Personality profile updated for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to update personality profile: {e}")
            # Don't fail the task if profile update fails
        
        # Invalidate personality context cache
        cache_delete(f"personality:context:{user_id}")
        
        logger.info(f"Sentiment analysis complete for user {user_id}: {insights}")
        
        return {
            'status': 'success',
            'insights': insights,
            'updates_applied': personality_updates
        }
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed for user {user_id}: {e}", exc_info=True)
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery_app.task
def analyze_all_users_sentiment() -> Dict:
    """
    Periodic task to analyze sentiment for all active users.
    Runs every hour via Celery Beat.
    
    Returns:
        dict: Summary of analysis results
    """
    try:
        logger.info("Starting batch sentiment analysis for all users")
        
        supabase = get_supabase_client()
        
        # Get users with recent chat activity (last 24 hours)
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        
        result = supabase.table('chat_messages') \
            .select('user_id') \
            .gte('created_at', cutoff) \
            .execute()
        
        # Get unique user IDs
        user_ids = list(set(msg['user_id'] for msg in result.data))
        
        logger.info(f"Found {len(user_ids)} active users for sentiment analysis")
        
        # Queue individual analysis tasks
        for user_id in user_ids:
            analyze_chat_sentiment_batch.delay(user_id)
        
        return {
            'status': 'success',
            'users_queued': len(user_ids),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Batch sentiment analysis failed: {e}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@celery_app.task(bind=True, max_retries=3)
def update_personality_from_activity(
    self,
    user_id: str,
    activity_type: str,
    activity_data: Dict
) -> Dict:
    """
    Update personality profile based on user activity (games, music, video).
    
    Args:
        user_id: User's unique ID
        activity_type: Type of activity ('game', 'music', 'video')
        activity_data: Activity-specific data
        
    Returns:
        dict: Update results
    """
    try:
        logger.info(f"Updating personality for user {user_id} from {activity_type} activity")
        
        supabase = get_supabase_client()
        
        # Get current profile
        profile = supabase.table('profiles') \
            .select('personality_data') \
            .eq('id', user_id) \
            .single() \
            .execute()
        
        personality = profile.data.get('personality_data', {}) or {}
        
        # Update based on activity type
        if activity_type == 'music':
            # Extract personality traits from music preferences
            genres = activity_data.get('top_genres', [])
            audio_profile = activity_data.get('audio_profile', {})
            
            # High energy music -> extroverted
            if audio_profile.get('energy', 0) > 0.7:
                personality['music_traits'] = personality.get('music_traits', {})
                personality['music_traits']['energy_preference'] = 'high'
                personality['music_traits']['likely_extroverted'] = True
            
            # Positive valence -> optimistic
            if audio_profile.get('valence', 0) > 0.7:
                personality['music_traits']['mood_preference'] = 'positive'
                personality['music_traits']['likely_optimistic'] = True
        
        elif activity_type == 'video':
            # Extract personality traits from video preferences
            categories = activity_data.get('top_categories', [])
            
            if 'education' in categories or 'documentary' in categories:
                personality['video_traits'] = personality.get('video_traits', {})
                personality['video_traits']['learning_oriented'] = True
                personality['video_traits']['likely_curious'] = True
        
        elif activity_type == 'game':
            # Extract personality traits from game performance
            game_type = activity_data.get('game_type')
            performance = activity_data.get('performance', {})
            
            if game_type == 'puzzle' and performance.get('completion_time', 999) < 60:
                personality['game_traits'] = personality.get('game_traits', {})
                personality['game_traits']['problem_solving'] = 'strong'
                personality['game_traits']['likely_analytical'] = True
        
        # Update timestamp
        personality['last_activity_update'] = datetime.now().isoformat()
        
        # Save to database
        supabase.table('profiles') \
            .update({'personality_data': personality}) \
            .eq('id', user_id) \
            .execute()
        
        # Invalidate cache
        cache_delete(f"personality:context:{user_id}")
        
        logger.info(f"Personality updated for user {user_id} from {activity_type}")
        
        return {
            'status': 'success',
            'activity_type': activity_type,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Personality update failed: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
