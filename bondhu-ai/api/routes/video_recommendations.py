"""
Video recommendation API routes with personality integration and RL feedback.
Provides endpoints for personalized video recommendations, feedback processing, and genre analysis.
"""

import logging

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

"""Video recommendation API routes.

Note: We intentionally import PersonalityTrait enum from core.database.models (the Enum)
instead of the similarly named Pydantic model in api.models.schemas to allow iteration
(`for trait in PersonalityTrait:`). Using the Pydantic model caused the runtime error:
"'ModelMetaclass' object is not iterable".
"""

from core.database.models import PersonalityTrait
from agents.video.video_agent import VideoIntelligenceAgent
from core.rl.video_recommendation_rl import VideoRecommendationRL
from core.database.personality_service import get_personality_service
from core.services.video_scheduler import get_video_scheduler
from core.config import get_config
from core.database.supabase_client import get_supabase_client

router = APIRouter(prefix="/api/v1/video", tags=["video"])
logger = logging.getLogger("bondhu.video.api")

class VideoFeedbackRequest(BaseModel):
    """Request model for video feedback."""
    video_id: str = Field(..., description="YouTube video ID")
    feedback_type: str = Field(..., description="Type of feedback: like, dislike, watch, skip, share, comment")
    watch_time: Optional[int] = Field(None, description="Watch time in seconds")
    total_duration: Optional[int] = Field(None, description="Total video duration in seconds")
    interactions: Optional[List[str]] = Field(None, description="List of interactions: pause, rewind, etc.")
    time_to_click: Optional[float] = Field(None, description="Time to click on video in seconds")

class VideoRecommendationRequest(BaseModel):
    """Request model for video recommendations."""
    max_results: int = Field(20, description="Maximum number of recommendations")
    force_refresh: bool = Field(False, description="Force refresh recommendations")
    include_trending: bool = Field(True, description="Include trending videos")
    category_filter: Optional[str] = Field(None, description="Filter by specific category")

class GenreAnalysisRequest(BaseModel):
    """Request model for genre analysis."""
    watch_history: List[Dict[str, Any]] = Field(..., description="User's video watch history")
    force_refresh: bool = Field(False, description="Force refresh analysis")

# Global RL systems cache
rl_systems: Dict[str, VideoRecommendationRL] = {}

def get_or_create_rl_system(user_id: str) -> VideoRecommendationRL:
    """Get or create RL system for user."""
    if user_id not in rl_systems:
        rl_systems[user_id] = VideoRecommendationRL(user_id)
    return rl_systems[user_id]

# --- Simple recommender endpoint integration ---
try:
    from core.services.simple_video_recommender import get_simple_recommendations
except Exception as _simple_import_err:  # pragma: no cover
    get_simple_recommendations = None  # Fallback if module missing

@router.get("/simple-recommendations/{user_id}")
async def get_simple_video_recommendations(user_id: str, max_results: int = 20):
    """Lightweight recommendations using simple YouTube recommender.

    Returns quickly and does not rely on full agent / RL stack. Provides
    a subset of fields: recommendations[], personality_profile, total_count.
    """
    if get_simple_recommendations is None:
        raise HTTPException(status_code=500, detail="Simple recommender not available")
    try:
        payload = await get_simple_recommendations(user_id=user_id, max_results=max_results)
        return payload
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Error generating simple recommendations: {exc}")

# --- History-based recommender endpoint ---
try:
    from core.services.history_based_recommender import get_history_based_recommendations
except Exception as _hist_err:  # pragma: no cover
    get_history_based_recommendations = None

@router.get("/history-recommendations/{user_id}")
async def get_history_video_recommendations(user_id: str, max_results: int = 30, include_persona_adjustments: bool = True):
    """Recommendations combining personality profile and stored watch history.

    Returns enrichment including watch history summary and proposed personality adjustments.
    """
    if get_history_based_recommendations is None:
        raise HTTPException(status_code=500, detail="History-based recommender unavailable")
    try:
        return await get_history_based_recommendations(
            user_id=user_id,
            max_results=max_results,
            include_persona_adjustments=include_persona_adjustments,
        )
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Error generating history recommendations: {exc}")


async def _fetch_user_watch_history(user_id: str, supabase, limit: int = 150) -> List[Dict[str, Any]]:
    """Retrieve the user's recent video watch history from Supabase."""
    try:
        result = (
            supabase
            .table("user_video_history")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception as exc:
        logger.error(f"Failed to fetch watch history for user %s: %s", user_id, exc)
        return []

@router.get("/recommendations/{user_id}")
async def get_video_recommendations_get(
    user_id: str,
    max_results: int = 20,
    force_refresh: bool = False,
    include_trending: bool = True,
    supabase=Depends(get_supabase_client)
):
    """
    Get personalized video recommendations for a user (GET version).
    
    Args:
        user_id: User identifier
        max_results: Maximum number of recommendations to return
        force_refresh: Force refresh recommendations
        include_trending: Include trending videos
        
    Returns:
        List of recommended videos with personality scores
    """
    request = VideoRecommendationRequest(
        max_results=max_results,
        force_refresh=force_refresh,
        include_trending=include_trending
    )
    
    from fastapi import BackgroundTasks
    background_tasks = BackgroundTasks()
    
    return await get_video_recommendations_post(user_id, request, background_tasks, supabase)

@router.post("/recommendations/{user_id}")
async def get_video_recommendations_post(
    user_id: str,
    request: VideoRecommendationRequest,
    background_tasks: BackgroundTasks,
    supabase=Depends(get_supabase_client)
):
    """
    Get personalized video recommendations for a user (POST version).
    
    Args:
        user_id: User identifier
        request: Recommendation parameters
        background_tasks: Background task processor
        
    Returns:
        List of recommended videos with personality scores
    """
    try:
        # Get user's personality profile
        personality_service = get_personality_service()
        user_context = await personality_service.get_user_personality_context(user_id)
        
        if not user_context.has_assessment:
            raise HTTPException(
                status_code=400, 
                detail="User has not completed personality assessment"
            )
        
        # Convert personality profile to agent format
        personality_profile = {}
        for trait in PersonalityTrait:
            score = getattr(user_context.personality_profile.scores, trait.value, 50)
            personality_profile[trait] = score / 100.0  # Convert to 0-1 scale
        
        # Initialize video agent
        video_agent = VideoIntelligenceAgent(user_id)
        
        # Get user's watch history from database (if available)
        watch_history = await _fetch_user_watch_history(user_id, supabase)
        
        # Get base recommendations
        recommendations = await video_agent.get_personalized_recommendations(
            personality_profile=personality_profile,
            watch_history=watch_history,
            max_results=request.max_results,
            force_refresh=request.force_refresh
        )
        
        # Apply RL scoring
        rl_system = get_or_create_rl_system(user_id)
        rl_scored_recommendations = await rl_system.get_recommendation_scores(
            recommendations, personality_profile
        )
        
        # Include trending videos if requested
        trending_videos = []
        if request.include_trending:
            trending_videos = await video_agent.get_trending_videos_by_personality(
                personality_profile=personality_profile,
                max_results=10
            )
        
        # Genre-based clusters combining personality and history
        genre_clusters = await video_agent.get_genre_recommendation_clusters(
            personality_profile=personality_profile,
            watch_history=watch_history,
            max_genres=6,
            videos_per_genre=3
        )

        # Combine and format results
        final_recommendations = []
        
        # Add RL-scored recommendations
        for video, rl_score in rl_scored_recommendations:
            video_result = video.copy()
            video_result['recommendation_score'] = video.get('personality_score', 0.0)
            video_result['rl_score'] = rl_score
            video_result['combined_score'] = (video_result['recommendation_score'] + rl_score) / 2
            video_result['source'] = 'personalized'
            final_recommendations.append(video_result)
        
        # Add trending videos
        for video in trending_videos[:5]:  # Limit trending videos
            video_result = video.copy()
            video_result['recommendation_score'] = video.get('personality_score', 0.0)
            video_result['rl_score'] = 0.0  # No RL score for trending
            video_result['combined_score'] = video_result['recommendation_score']
            video_result['source'] = 'trending'
            final_recommendations.append(video_result)
        
        # Ensure genre cluster videos are included in final recommendations
        final_map = {video['id']: video for video in final_recommendations if video.get('id')}

        for cluster in genre_clusters:
            for video in cluster['videos']:
                video_id = video.get('id')
                if not video_id:
                    continue
                if video_id not in final_map:
                    final_map[video_id] = video
                else:
                    # Merge metadata to preserve RL/trending scores with genre info
                    final_map[video_id].setdefault('genre', video.get('genre'))
                    final_map[video_id].setdefault('genre_rank', video.get('genre_rank'))
                    final_map[video_id].setdefault('genre_combined_score', video.get('genre_combined_score'))

        final_recommendations = list(final_map.values())

        # Sort by combined score
        final_recommendations.sort(key=lambda x: x.get('combined_score', 0.0), reverse=True)

        # Limit to requested number while ensuring genre clusters remain intact
        minimum_cluster_count = sum(len(cluster['videos']) for cluster in genre_clusters)
        limit = max(request.max_results, minimum_cluster_count)
        final_recommendations = final_recommendations[:limit]
        
        return {
            "success": True,
            "data": {
                "recommendations": final_recommendations,
                "genre_clusters": genre_clusters,
                "total_count": len(final_recommendations),
                "personality_profile": {
                    trait.value: score for trait, score in personality_profile.items()
                },
                "refresh_time": datetime.now().isoformat(),
                "next_refresh": video_agent.should_refresh_recommendations()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@router.post("/feedback/{user_id}")
async def process_video_feedback(
    user_id: str,
    feedback: VideoFeedbackRequest,
    background_tasks: BackgroundTasks
):
    """
    Process user feedback for video recommendations.
    
    Args:
        user_id: User identifier
        feedback: Feedback data
        background_tasks: Background task processor
        
    Returns:
        Confirmation of feedback processing
    """
    try:
        # Get video agent
        video_agent = VideoIntelligenceAgent(user_id)
        
        # Process feedback through agent
        additional_data = {
            'watch_time': feedback.watch_time,
            'duration': feedback.total_duration,
            'interactions': feedback.interactions or [],
            'time_to_click': feedback.time_to_click
        }
        
        success = await video_agent.process_user_feedback(
            video_id=feedback.video_id,
            feedback_type=feedback.feedback_type,
            additional_data=additional_data
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to process feedback")
        
        # Process through RL system
        rl_system = get_or_create_rl_system(user_id)
        
        # Get video data (in real implementation, would fetch from YouTube API)
        video_data = {
            'id': feedback.video_id,
            'duration_seconds': feedback.total_duration or 300,
            'engagement_score': 0.5,  # Default values
            'category_name': 'Entertainment',
            'content_themes': ['entertainment']
        }
        
        # Get personality profile
        personality_service = get_personality_service()
        user_context = await personality_service.get_user_personality_context(user_id)
        
        personality_profile = {}
        if user_context.has_assessment:
            for trait in PersonalityTrait:
                score = getattr(user_context.personality_profile.scores, trait.value, 50)
                personality_profile[trait] = score / 100.0
        
        # Process RL feedback
        rl_score = await rl_system.process_feedback(
            video_data=video_data,
            personality_profile=personality_profile,
            feedback_type=feedback.feedback_type,
            additional_data=additional_data
        )
        
        # Background task to update personality insights
        background_tasks.add_task(
            update_personality_from_feedback,
            user_id, feedback.video_id, feedback.feedback_type, additional_data
        )
        
        return {
            "success": True,
            "data": {
                "feedback_processed": True,
                "rl_score": rl_score,
                "feedback_type": feedback.feedback_type,
                "video_id": feedback.video_id,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing feedback: {str(e)}")

@router.post("/genre-analysis/{user_id}")
async def analyze_video_genres(
    user_id: str,
    request: GenreAnalysisRequest
):
    """
    Analyze user's video genre preferences and extract personality insights.
    
    Args:
        user_id: User identifier
        request: Genre analysis parameters
        
    Returns:
        Genre analysis and personality insights
    """
    try:
        # Initialize video agent
        video_agent = VideoIntelligenceAgent(user_id)
        
        # Perform genre analysis
        analysis = await video_agent.analyze_user_video_genres(
            watch_history=request.watch_history,
            force_refresh=request.force_refresh
        )
        
        return {
            "success": True,
            "data": {
                "genre_analysis": analysis,
                "user_id": user_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "videos_analyzed": len(request.watch_history)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing genres: {str(e)}")

@router.get("/trending/{user_id}")
async def get_trending_videos(
    user_id: str,
    max_results: int = 25,
    region_code: str = "US"
):
    """
    Get trending videos filtered by user's personality.
    
    Args:
        user_id: User identifier
        max_results: Maximum number of videos to return
        region_code: Region code for trending videos
        
    Returns:
        List of personality-matched trending videos
    """
    try:
        # Get personality profile
        personality_service = get_personality_service()
        user_context = await personality_service.get_user_personality_context(user_id)
        
        if not user_context.has_assessment:
            raise HTTPException(
                status_code=400,
                detail="User has not completed personality assessment"
            )
        
        # Convert personality profile
        personality_profile = {}
        for trait in PersonalityTrait:
            score = getattr(user_context.personality_profile.scores, trait.value, 50)
            personality_profile[trait] = score / 100.0
        
        # Get trending videos
        video_agent = VideoIntelligenceAgent(user_id)
        trending_videos = await video_agent.get_trending_videos_by_personality(
            personality_profile=personality_profile,
            region_code=region_code,
            max_results=max_results
        )
        
        return {
            "success": True,
            "data": {
                "trending_videos": trending_videos,
                "total_count": len(trending_videos),
                "region_code": region_code,
                "personality_profile": {
                    trait.value: score for trait, score in personality_profile.items()
                },
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trending videos: {str(e)}")

@router.get("/rl-stats/{user_id}")
async def get_rl_statistics(user_id: str):
    """
    Get reinforcement learning statistics for user.
    
    Args:
        user_id: User identifier
        
    Returns:
        RL learning statistics and metrics
    """
    try:
        rl_system = get_or_create_rl_system(user_id)
        stats = rl_system.get_learning_statistics()
        
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "rl_statistics": stats,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting RL statistics: {str(e)}")

@router.post("/refresh-recommendations/{user_id}")
async def refresh_video_recommendations(user_id: str):
    """
    Manually refresh video recommendations for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Confirmation of refresh
    """
    try:
        # Use scheduler for manual refresh
        scheduler = get_video_scheduler()
        success = scheduler.manual_refresh_trigger(user_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to trigger refresh")
        
        # Also refresh through scheduler service
        refresh_success = await scheduler.refresh_user_recommendations(user_id, force=True)
        
        return {
            "success": True,
            "data": {
                "refresh_triggered": success,
                "refresh_completed": refresh_success,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "message": "Recommendations refreshed successfully" if refresh_success else "Refresh triggered, processing in background"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing recommendations: {str(e)}")

@router.get("/scheduler-status")
async def get_scheduler_status():
    """
    Get video recommendation scheduler status.
    
    Returns:
        Scheduler status and configuration
    """
    try:
        scheduler = get_video_scheduler()
        status = scheduler.get_scheduler_status()
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting scheduler status: {str(e)}")

@router.post("/scheduler/register/{user_id}")
async def register_user_for_auto_refresh(user_id: str):
    """
    Register a user for automatic video recommendation refresh.
    
    Args:
        user_id: User identifier
        
    Returns:
        Registration confirmation
    """
    try:
        scheduler = get_video_scheduler()
        success = scheduler.register_user(user_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to register user")
        
        return {
            "success": True,
            "data": {
                "user_registered": True,
                "user_id": user_id,
                "next_refresh": scheduler.get_next_refresh_time().isoformat() if scheduler.get_next_refresh_time() else None,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering user: {str(e)}")

@router.delete("/scheduler/unregister/{user_id}")
async def unregister_user_from_auto_refresh(user_id: str):
    """
    Unregister a user from automatic video recommendation refresh.
    
    Args:
        user_id: User identifier
        
    Returns:
        Unregistration confirmation
    """
    try:
        scheduler = get_video_scheduler()
        success = scheduler.unregister_user(user_id)
        
        return {
            "success": True,
            "data": {
                "user_unregistered": success,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unregistering user: {str(e)}")

async def update_personality_from_feedback(user_id: str, video_id: str, 
                                         feedback_type: str, additional_data: Dict[str, Any]):
    """
    Background task to update personality insights based on video feedback.
    
    Args:
        user_id: User identifier
        video_id: Video ID
        feedback_type: Type of feedback
        additional_data: Additional feedback context
    """
    try:
        # This would implement personality updating logic
        # For now, just log the feedback for future analysis
        
        feedback_entry = {
            'user_id': user_id,
            'video_id': video_id,
            'feedback_type': feedback_type,
            'additional_data': additional_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # In a full implementation, this would:
        # 1. Analyze video content and genre
        # 2. Update personality trait confidence scores
        # 3. Store feedback in database for batch learning
        # 4. Trigger personality model retraining if needed
        
        print(f"Background personality update: {feedback_entry}")
        
    except Exception as e:
        print(f"Error in background personality update: {e}")