"""
Entertainment API routes for video recommendations, music analysis, and gaming preferences.
Provides personality-based content recommendations and user feedback processing.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from core.database.supabase_client import get_supabase_client
from core.database.personality_service import PersonalityContextService, get_personality_service
from agents.video.video_agent import VideoIntelligenceAgent
from agents.music.music_agent import MusicIntelligenceAgent
from agents.gaming.gaming_agent import GamingIntelligenceAgent
from core.config.settings import get_config
from core.database.models import PersonalityTrait  # Enum, not Pydantic model

router = APIRouter(prefix="/api/v1", tags=["entertainment"])
logger = logging.getLogger("bondhu.entertainment")

# Video Entertainment Endpoints
@router.get("/video/recommendations/{user_id}")
async def get_video_recommendations(
    user_id: str,
    max_results: int = Query(20, ge=5, le=50),
    force_refresh: bool = Query(False),
    supabase=Depends(get_supabase_client)
):
    """
    Get personalized video recommendations based on user's personality profile.
    Returns real YouTube videos matched to user's Big Five personality traits.
    """
    try:
        config = get_config()
        
        # Initialize video agent
        video_agent = VideoIntelligenceAgent(
            user_id=user_id,
            youtube_api_key=config.youtube.api_key
        )
        
        # Get user's personality profile
        personality_service = get_personality_service()
        personality_context = await personality_service.get_user_personality_context(user_id)
        personality_scores = personality_context.personality_scores if personality_context else None
        
        if not personality_scores:
            # Use default balanced personality for new users
            personality_scores = {
                PersonalityTrait.OPENNESS: 50.0,
                PersonalityTrait.CONSCIENTIOUSNESS: 50.0,
                PersonalityTrait.EXTRAVERSION: 50.0,
                PersonalityTrait.AGREEABLENESS: 50.0,
                PersonalityTrait.NEUROTICISM: 50.0
            }
        
        # Get user's watch history (if available)
        watch_history = await get_user_watch_history(user_id, supabase)
        
        # Get personalized recommendations
        recommendations = await video_agent.get_personalized_recommendations(
            personality_profile=personality_scores,
            watch_history=watch_history,
            max_results=max_results,
            force_refresh=force_refresh
        )
        
        # Enrich recommendations with additional data
        enriched_recommendations = []
        for video in recommendations:
            enriched_video = {
                **video,
                "watch_url": f"https://www.youtube.com/watch?v={video['id']}",
                "embed_url": f"https://www.youtube.com/embed/{video['id']}",
                "personality_match": round(video.get('personality_score', 0.5) * 100, 1),
                "recommendation_reason": generate_recommendation_reason(video, personality_scores),
                "thumbnails": {
                    "default": video.get('thumbnail_url', ''),
                    "medium": video.get('thumbnail_url', '').replace('maxresdefault', 'mqdefault'),
                    "high": video.get('thumbnail_url', '').replace('maxresdefault', 'hqdefault')
                }
            }
            enriched_recommendations.append(enriched_video)
        
        # Group by categories for better UX
        videos_by_category = group_videos_by_category(enriched_recommendations)
        
        logger.info(f"Generated {len(enriched_recommendations)} video recommendations for user {user_id}")
        
        return {
            "recommendations": enriched_recommendations,
            "videos_per_genre": videos_by_category,
            "total_count": len(enriched_recommendations),
            "personality_based": True,
            "user_id": user_id,
            "generated_at": datetime.now().isoformat(),
            "has_thumbnails": True,
            "has_watch_links": True
        }
        
    except Exception as e:
        logger.error(f"Error getting video recommendations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.post("/video/feedback")
async def submit_video_feedback(
    feedback_data: Dict[str, Any],
    supabase=Depends(get_supabase_client)
):
    """
    Submit user feedback (like/dislike) for video recommendations.
    Used for reinforcement learning and improving future recommendations.
    """
    try:
        user_id = feedback_data.get("user_id")
        video_id = feedback_data.get("video_id")
        feedback_type = feedback_data.get("feedback_type")  # 'like', 'dislike', 'watch', 'skip'
        additional_data = feedback_data.get("additional_data", {})
        
        if not all([user_id, video_id, feedback_type]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Validate feedback type
        valid_feedback_types = ['like', 'dislike', 'watch', 'skip', 'share']
        if feedback_type not in valid_feedback_types:
            raise HTTPException(status_code=400, detail=f"Invalid feedback type. Must be one of: {valid_feedback_types}")
        
        # Store feedback in database
        feedback_record = {
            "user_id": user_id,
            "video_id": video_id,
            "feedback_type": feedback_type,
            "additional_data": additional_data,
            "timestamp": datetime.now().isoformat()
        }
        
        result = supabase.table("video_feedback").insert(feedback_record).execute()
        
        # Process feedback for ML improvement
        config = get_config()
        video_agent = VideoIntelligenceAgent(
            user_id=user_id,
            youtube_api_key=config.youtube.api_key
        )
        
        await video_agent.process_user_feedback(
            video_id=video_id,
            feedback_type=feedback_type,
            additional_data=additional_data
        )
        
        logger.info(f"Processed {feedback_type} feedback for video {video_id} from user {user_id}")
        
        return {
            "success": True,
            "message": "Feedback recorded successfully",
            "feedback_id": result.data[0]["id"] if result.data else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing video feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")

@router.get("/video/trending/{user_id}")
async def get_trending_videos_personalized(
    user_id: str,
    region_code: str = Query("US", description="Region code for trending videos"),
    max_results: int = Query(25, ge=10, le=50),
    supabase=Depends(get_supabase_client)
):
    """
    Get trending videos filtered and scored by user's personality compatibility.
    """
    try:
        config = get_config()
        
        # Initialize video agent
        video_agent = VideoIntelligenceAgent(
            user_id=user_id,
            youtube_api_key=config.youtube.api_key
        )
        
        # Get user's personality profile
        personality_service = get_personality_service()
        personality_context = await personality_service.get_user_personality_context(user_id)
        personality_scores = personality_context.personality_scores if personality_context else None
        
        if not personality_scores:
            personality_scores = {trait: 50.0 for trait in PersonalityTrait}
        
        # Get trending videos with personality scoring
        trending_videos = await video_agent.get_trending_videos_by_personality(
            personality_profile=personality_scores,
            region_code=region_code,
            max_results=max_results
        )
        
        # Enrich trending videos
        enriched_trending = []
        for video in trending_videos:
            enriched_video = {
                **video,
                "watch_url": f"https://www.youtube.com/watch?v={video['id']}",
                "personality_match": round(video.get('personality_score', 0.5) * 100, 1),
                "trending_rank": len(enriched_trending) + 1,
                "is_trending": True
            }
            enriched_trending.append(enriched_video)
        
        return {
            "trending_videos": enriched_trending,
            "region_code": region_code,
            "total_count": len(enriched_trending),
            "user_id": user_id,
            "personality_filtered": True
        }
        
    except Exception as e:
        logger.error(f"Error getting trending videos for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get trending videos: {str(e)}")

@router.get("/video/genres/{user_id}/analysis")
async def analyze_user_video_genres(
    user_id: str,
    force_refresh: bool = Query(False),
    supabase=Depends(get_supabase_client)
):
    """
    Analyze user's video genre preferences and extract personality insights.
    """
    try:
        config = get_config()
        
        # Initialize video agent
        video_agent = VideoIntelligenceAgent(
            user_id=user_id,
            youtube_api_key=config.youtube.api_key
        )
        
        # Get user's watch history
        watch_history = await get_user_watch_history(user_id, supabase)
        
        # Analyze genres
        genre_analysis = await video_agent.analyze_user_video_genres(
            watch_history=watch_history,
            force_refresh=force_refresh
        )
        
        return {
            "genre_analysis": genre_analysis,
            "user_id": user_id,
            "analysis_based_on": len(watch_history),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing video genres for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze genres: {str(e)}")

# Helper Functions
async def get_user_watch_history(user_id: str, supabase) -> List[Dict[str, Any]]:
    """Get user's video watch history from database."""
    try:
        result = supabase.table("user_video_history").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(100).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error fetching watch history for user {user_id}: {e}")
        return []

def generate_recommendation_reason(video: Dict[str, Any], personality_scores: Dict[PersonalityTrait, float]) -> str:
    """Generate a human-readable reason for why this video was recommended."""
    try:
        category = video.get('category_name', 'Entertainment')
        personality_score = video.get('personality_score', 0.5)
        
        # Find dominant personality traits
        sorted_traits = sorted(personality_scores.items(), key=lambda x: x[1], reverse=True)
        dominant_trait = sorted_traits[0][0].value.lower()
        
        # Generate reason based on category and dominant trait
        reasons = {
            'education': {
                'openness': "matches your curiosity and love for learning",
                'conscientiousness': "aligns with your structured approach to knowledge",
                'extraversion': "offers engaging educational content",
                'agreeableness': "provides helpful information for others",
                'neuroticism': "offers calming, structured learning"
            },
            'entertainment': {
                'openness': "offers creative and diverse entertainment",
                'conscientiousness': "provides quality entertainment content",
                'extraversion': "matches your social and energetic personality",
                'agreeableness': "offers feel-good entertainment",
                'neuroticism': "provides relaxing entertainment"
            },
            'music': {
                'openness': "explores diverse musical styles",
                'conscientiousness': "features well-crafted musical content",
                'extraversion': "matches your vibrant personality",
                'agreeableness': "offers emotionally connecting music",
                'neuroticism': "provides mood-lifting musical content"
            }
        }
        
        category_key = category.lower().replace(' & ', '_').replace(' ', '_')
        if category_key in reasons and dominant_trait in reasons[category_key]:
            return f"Recommended because it {reasons[category_key][dominant_trait]} ({int(personality_score * 100)}% match)"
        
        return f"Recommended based on your personality profile ({int(personality_score * 100)}% match)"
        
    except Exception as e:
        return f"Recommended for you ({int(video.get('personality_score', 0.5) * 100)}% match)"

def group_videos_by_category(videos: List[Dict[str, Any]]) -> Dict[str, int]:
    """Group videos by category for better organization."""
    category_counts = {}
    for video in videos:
        category = video.get('category_name', 'Other')
        category_counts[category] = category_counts.get(category, 0) + 1
    return category_counts

# Music Entertainment Endpoints (Future expansion)
@router.get("/music/recommendations/{user_id}")
async def get_music_recommendations(user_id: str):
    """Get music recommendations based on personality (placeholder for future implementation)."""
    return {"message": "Music recommendations coming soon", "user_id": user_id}

# Gaming Entertainment Endpoints (Future expansion)  
@router.get("/gaming/recommendations/{user_id}")
async def get_gaming_recommendations(user_id: str):
    """Get gaming recommendations based on personality (placeholder for future implementation)."""
    return {"message": "Gaming recommendations coming soon", "user_id": user_id}
