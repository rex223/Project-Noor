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

import asyncio
import json
import logging
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field

# Note: Import PersonalityTrait Enum (not Pydantic model) so we can iterate
from core.database.models import PersonalityTrait
from agents.video.video_agent import VideoIntelligenceAgent
from core.rl.video_recommendation_rl import VideoRecommendationRL
from core.database.personality_service import get_personality_service
from core.services.video_scheduler import get_video_scheduler
from core.database.supabase_client import get_supabase_client
from core.cache.redis_client import get_redis

router = APIRouter(prefix="/api/v1/video", tags=["video"])
logger = logging.getLogger("bondhu.video.api")

# Redis client (optional)
_REDIS_CLIENT = None
try:
    _REDIS_CLIENT = get_redis()
except Exception as e:  # pragma: no cover
    logger.warning("Unable to initialize Redis client for video cache: %s", e)

RECOMMENDATION_CACHE_TTL = 15 * 60  # 15 minutes
PREFETCH_LOCK_TTL = 2 * 60  # 2 minutes lock to avoid duplicate warmups


class VideoFeedbackRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")
    feedback_type: str = Field(..., description="Type of feedback: like, dislike, watch, skip, share, comment")
    watch_time: Optional[int] = Field(None, description="Watch time in seconds")
    total_duration: Optional[int] = Field(None, description="Total video duration in seconds")
    interactions: Optional[List[str]] = Field(None, description="List of interactions: pause, rewind, etc.")
    time_to_click: Optional[float] = Field(None, description="Time to click on video in seconds")
    video_title: Optional[str] = Field(None, description="Video title")
    channel_title: Optional[str] = Field(None, description="Channel title")
    category_name: Optional[str] = Field(None, description="Video category")


class VideoRecommendationRequest(BaseModel):
    max_results: int = Field(15, description="Maximum number of recommendations")
    force_refresh: bool = Field(False, description="Force refresh recommendations")
    include_trending: bool = Field(True, description="Include trending videos")
    category_filter: Optional[str] = Field(None, description="Filter by specific category")


def _build_recommendation_cache_key(user_id: str, request: VideoRecommendationRequest) -> str:
    category = request.category_filter or "all"
    return f"video:recommendations:{user_id}:{request.max_results}:{int(request.include_trending)}:{category}"


async def _load_cached_recommendations(cache_key: str) -> Optional[Dict[str, Any]]:
    if _REDIS_CLIENT is None:
        return None

    loop = asyncio.get_running_loop()
    try:
        raw = await loop.run_in_executor(None, _REDIS_CLIENT.get, cache_key)
        if raw:
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            return json.loads(raw)
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to read recommendation cache key %s: %s", cache_key, exc)
    return None


async def _store_cached_recommendations(cache_key: str, payload: Dict[str, Any]) -> None:
    if _REDIS_CLIENT is None:
        return

    loop = asyncio.get_running_loop()
    data = json.dumps(payload)
    try:
        await loop.run_in_executor(None, _REDIS_CLIENT.setex, cache_key, RECOMMENDATION_CACHE_TTL, data)
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to store recommendation cache key %s: %s", cache_key, exc)


async def _acquire_prefetch_lock(lock_key: str) -> bool:
    if _REDIS_CLIENT is None:
        return True

    loop = asyncio.get_running_loop()

    def _setnx() -> bool:
        return bool(_REDIS_CLIENT.set(lock_key, "1", nx=True, ex=PREFETCH_LOCK_TTL))

    try:
        return await loop.run_in_executor(None, _setnx)
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to acquire prefetch lock %s: %s", lock_key, exc)
        return False


async def _release_prefetch_lock(lock_key: str) -> None:
    if _REDIS_CLIENT is None:
        return

    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, _REDIS_CLIENT.delete, lock_key)
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to release prefetch lock %s: %s", lock_key, exc)


class GenreAnalysisRequest(BaseModel):
    watch_history: List[Dict[str, Any]] = Field(..., description="User's video watch history")
    force_refresh: bool = Field(False, description="Force refresh analysis")


# Global RL systems cache
rl_systems: Dict[str, VideoRecommendationRL] = {}


def get_or_create_rl_system(user_id: str) -> VideoRecommendationRL:
    if user_id not in rl_systems:
        rl_systems[user_id] = VideoRecommendationRL(user_id)
    return rl_systems[user_id]


async def _fetch_user_watch_history(user_id: str, supabase, limit: int = 150) -> List[Dict[str, Any]]:
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
        logger.error("Failed to fetch watch history for user %s: %s", user_id, exc)
        return []


async def _generate_recommendation_payload(
    user_id: str,
    video_agent: VideoIntelligenceAgent,
    personality_profile: Dict[PersonalityTrait, float],
    watch_history: List[Dict[str, Any]],
    request: VideoRecommendationRequest
) -> Dict[str, Any]:

    recommendations = await video_agent.get_personalized_recommendations(
        personality_profile=personality_profile,
        watch_history=watch_history,
        max_results=request.max_results,
        force_refresh=request.force_refresh
    )

    rl_system = get_or_create_rl_system(user_id)
    rl_scored_recommendations = await rl_system.get_recommendation_scores(
        recommendations, personality_profile
    )

    trending_videos: List[Dict[str, Any]] = []
    if request.include_trending:
        trending_videos = await video_agent.get_trending_videos_by_personality(
            personality_profile=personality_profile,
            max_results=10
        )

    genre_clusters = await video_agent.get_genre_recommendation_clusters(
        personality_profile=personality_profile,
        watch_history=watch_history,
        max_genres=6,
        videos_per_genre=3
    )

    final_recommendations: List[Dict[str, Any]] = []

    for video, rl_score in rl_scored_recommendations:
        video_result = video.copy()
        video_result['recommendation_score'] = video.get('personality_score', 0.0)
        video_result['rl_score'] = rl_score
        video_result['combined_score'] = (video_result['recommendation_score'] + rl_score) / 2
        video_result['source'] = 'personalized'
        final_recommendations.append(video_result)

    for video in trending_videos[:5]:
        video_result = video.copy()
        video_result['recommendation_score'] = video.get('personality_score', 0.0)
        video_result['rl_score'] = 0.0
        video_result['combined_score'] = video_result['recommendation_score']
        video_result['source'] = 'trending'
        final_recommendations.append(video_result)

    final_map = {video['id']: video for video in final_recommendations if video.get('id')}

    for cluster in genre_clusters:
        for video in cluster['videos']:
            video_id = video.get('id')
            if not video_id:
                continue
            if request.category_filter and video.get('category_name') and request.category_filter.lower() not in video.get('category_name', '').lower():
                continue
            if video_id not in final_map:
                final_map[video_id] = video
            else:
                final_map[video_id].setdefault('genre', video.get('genre'))
                final_map[video_id].setdefault('genre_rank', video.get('genre_rank'))
                final_map[video_id].setdefault('genre_combined_score', video.get('genre_combined_score'))

    final_recommendations = list(final_map.values())
    final_recommendations.sort(key=lambda x: x.get('combined_score', 0.0), reverse=True)

    minimum_cluster_count = sum(len(cluster['videos']) for cluster in genre_clusters)
    limit = max(request.max_results, minimum_cluster_count)
    final_recommendations = final_recommendations[:limit]

    payload = {
        "recommendations": final_recommendations,
        "genre_clusters": genre_clusters,
        "total_count": len(final_recommendations),
        "personality_profile": {trait.value: score for trait, score in personality_profile.items()},
        "refresh_time": datetime.now().isoformat(),
        "next_refresh": video_agent.should_refresh_recommendations()
    }

    return payload


async def _prepare_user_context(user_id: str, supabase) -> Tuple[Dict[PersonalityTrait, float], List[Dict[str, Any]]]:
    personality_service = get_personality_service()
    user_context = await personality_service.get_user_personality_context(user_id)

    if not user_context.has_assessment:
        raise HTTPException(status_code=400, detail="User has not completed personality assessment")

    personality_profile: Dict[PersonalityTrait, float] = {}
    for trait in PersonalityTrait:
        score = getattr(user_context.personality_profile.scores, trait.value, 50)
        personality_profile[trait] = score / 100.0

    watch_history = await _fetch_user_watch_history(user_id, supabase)
    return personality_profile, watch_history


@router.get("/recommendations/{user_id}")
async def get_video_recommendations_get(
    user_id: str,
    background_tasks: BackgroundTasks,
    max_results: int = 20,
    force_refresh: bool = False,
    include_trending: bool = True,
    category_filter: Optional[str] = None,
    supabase=Depends(get_supabase_client)
):
    request = VideoRecommendationRequest(
        max_results=max_results,
        force_refresh=force_refresh,
        include_trending=include_trending,
        category_filter=category_filter
    )

    return await get_video_recommendations_post(user_id, request, background_tasks, supabase)


@router.post("/recommendations/{user_id}")
async def get_video_recommendations_post(
    user_id: str,
    request: VideoRecommendationRequest,
    background_tasks: BackgroundTasks,
    supabase=Depends(get_supabase_client)
):
    try:
        cache_key = _build_recommendation_cache_key(user_id, request)

        if not request.force_refresh:
            cached_entry = await _load_cached_recommendations(cache_key)
            if cached_entry:
                payload = cached_entry.get("payload") if isinstance(cached_entry, dict) else cached_entry
                response: Dict[str, Any] = {"success": True, "data": payload, "cache_hit": True}
                if isinstance(cached_entry, dict):
                    if cached_entry.get("cached_at"):
                        response["cache_timestamp"] = cached_entry["cached_at"]
                    if cached_entry.get("ttl_seconds"):
                        response["cache_ttl"] = cached_entry["ttl_seconds"]
                return response

        personality_profile, watch_history = await _prepare_user_context(user_id, supabase)
        video_agent = VideoIntelligenceAgent(user_id)

        payload = await _generate_recommendation_payload(
            user_id=user_id,
            video_agent=video_agent,
            personality_profile=personality_profile,
            watch_history=watch_history,
            request=request
        )

        cache_record = {"payload": payload, "cached_at": datetime.now().isoformat(), "ttl_seconds": RECOMMENDATION_CACHE_TTL}
        await _store_cached_recommendations(cache_key, cache_record)

        return {"success": True, "data": payload, "cache_hit": False, "cache_timestamp": cache_record["cached_at"]}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.post("/feedback/{user_id}")
async def process_video_feedback(
    user_id: str,
    feedback: VideoFeedbackRequest,
    background_tasks: BackgroundTasks
):
    try:
        video_agent = VideoIntelligenceAgent(user_id)
        additional_data = {
            'watch_time': feedback.watch_time,
            'duration': feedback.total_duration,
            'interactions': feedback.interactions or [],
            'time_to_click': feedback.time_to_click,
            'video_title': feedback.video_title,
            'channel_title': feedback.channel_title,
            'category_name': feedback.category_name
        }
        success = await video_agent.process_user_feedback(
            video_id=feedback.video_id,
            feedback_type=feedback.feedback_type,
            additional_data=additional_data
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to process feedback")

        rl_system = get_or_create_rl_system(user_id)
        video_data = {
            'id': feedback.video_id,
            'duration_seconds': feedback.total_duration or 300,
            'engagement_score': 0.5,
            'category_name': 'Entertainment',
            'content_themes': ['entertainment']
        }
        personality_service = get_personality_service()
        user_context = await personality_service.get_user_personality_context(user_id)
        personality_profile = {}
        if user_context.has_assessment:
            for trait in PersonalityTrait:
                score = getattr(user_context.personality_profile.scores, trait.value, 50)
                personality_profile[trait] = score / 100.0
        rl_score = await rl_system.process_feedback(
            video_data=video_data,
            personality_profile=personality_profile,
            feedback_type=feedback.feedback_type,
            additional_data=additional_data
        )
        background_tasks.add_task(update_personality_from_feedback, user_id, feedback.video_id, feedback.feedback_type, additional_data)
        return {"success": True, "data": {"feedback_processed": True, "rl_score": rl_score, "feedback_type": feedback.feedback_type, "video_id": feedback.video_id, "timestamp": datetime.now().isoformat()}}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing feedback: {str(e)}")


@router.post("/genre-analysis/{user_id}")
async def analyze_video_genres(
    user_id: str,
    request: GenreAnalysisRequest
):
    try:
        video_agent = VideoIntelligenceAgent(user_id)
        analysis = await video_agent.analyze_user_video_genres(watch_history=request.watch_history, force_refresh=request.force_refresh)
        return {"success": True, "data": {"genre_analysis": analysis, "user_id": user_id, "analysis_timestamp": datetime.now().isoformat(), "videos_analyzed": len(request.watch_history)}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing genres: {str(e)}")


@router.get("/trending/{user_id}")
async def get_trending_videos(
    user_id: str,
    max_results: int = 25,
    region_code: str = "US"
):
    try:
        personality_service = get_personality_service()
        user_context = await personality_service.get_user_personality_context(user_id)
        if not user_context.has_assessment:
            raise HTTPException(status_code=400, detail="User has not completed personality assessment")
        personality_profile = {}
        for trait in PersonalityTrait:
            score = getattr(user_context.personality_profile.scores, trait.value, 50)
            personality_profile[trait] = score / 100.0
        video_agent = VideoIntelligenceAgent(user_id)
        trending_videos = await video_agent.get_trending_videos_by_personality(personality_profile=personality_profile, region_code=region_code, max_results=max_results)
        return {"success": True, "data": {"trending_videos": trending_videos, "total_count": len(trending_videos), "region_code": region_code, "personality_profile": {trait.value: score for trait, score in personality_profile.items()}, "timestamp": datetime.now().isoformat()}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trending videos: {str(e)}")


@router.get("/rl-stats/{user_id}")
async def get_rl_statistics(user_id: str):
    try:
        rl_system = get_or_create_rl_system(user_id)
        stats = rl_system.get_learning_statistics()
        return {"success": True, "data": {"user_id": user_id, "rl_statistics": stats, "timestamp": datetime.now().isoformat()}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting RL statistics: {str(e)}")


@router.post("/refresh-recommendations/{user_id}")
async def refresh_video_recommendations(user_id: str):
    try:
        scheduler = get_video_scheduler()
        success = scheduler.manual_refresh_trigger(user_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to trigger refresh")
        refresh_success = await scheduler.refresh_user_recommendations(user_id, force=True)
        return {"success": True, "data": {"refresh_triggered": success, "refresh_completed": refresh_success, "user_id": user_id, "timestamp": datetime.now().isoformat(), "message": "Recommendations refreshed successfully" if refresh_success else "Refresh triggered, processing in background"}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing recommendations: {str(e)}")


@router.get("/scheduler-status")
async def get_scheduler_status():
    try:
        scheduler = get_video_scheduler()
        status = scheduler.get_scheduler_status()
        return {"success": True, "data": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting scheduler status: {str(e)}")


@router.post("/scheduler/register/{user_id}")
async def register_user_for_auto_refresh(user_id: str):
    try:
        scheduler = get_video_scheduler()
        success = scheduler.register_user(user_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to register user")
        return {"success": True, "data": {"user_registered": True, "user_id": user_id, "next_refresh": scheduler.get_next_refresh_time().isoformat() if scheduler.get_next_refresh_time() else None, "timestamp": datetime.now().isoformat()}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering user: {str(e)}")


@router.delete("/scheduler/unregister/{user_id}")
async def unregister_user_from_auto_refresh(user_id: str):
    try:
        scheduler = get_video_scheduler()
        success = scheduler.unregister_user(user_id)
        return {"success": True, "data": {"user_unregistered": success, "user_id": user_id, "timestamp": datetime.now().isoformat()}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unregistering user: {str(e)}")


async def update_personality_from_feedback(user_id: str, video_id: str, 
                                         feedback_type: str, additional_data: Dict[str, Any]):
    try:
        feedback_entry = {'user_id': user_id, 'video_id': video_id, 'feedback_type': feedback_type, 'additional_data': additional_data, 'timestamp': datetime.now().isoformat()}
        print(f"Background personality update: {feedback_entry}")
    except Exception as e:
        print(f"Error in background personality update: {e}")


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


async def _generate_recommendation_payload(
    user_id: str,
    video_agent: VideoIntelligenceAgent,
    personality_profile: Dict[PersonalityTrait, float],
    watch_history: List[Dict[str, Any]],
    request: VideoRecommendationRequest
) -> Dict[str, Any]:
    """Generate recommendation payload shared by API and prefetch warmup."""

    recommendations = await video_agent.get_personalized_recommendations(
        personality_profile=personality_profile,
        watch_history=watch_history,
        max_results=request.max_results,
        force_refresh=request.force_refresh
    )

    rl_system = get_or_create_rl_system(user_id)
    rl_scored_recommendations = await rl_system.get_recommendation_scores(
        recommendations, personality_profile
    )

    trending_videos: List[Dict[str, Any]] = []
    if request.include_trending:
        trending_videos = await video_agent.get_trending_videos_by_personality(
            personality_profile=personality_profile,
            max_results=10
        )

    genre_clusters = await video_agent.get_genre_recommendation_clusters(
        personality_profile=personality_profile,
        watch_history=watch_history,
        max_genres=6,
        videos_per_genre=3
    )

    final_recommendations: List[Dict[str, Any]] = []

    for video, rl_score in rl_scored_recommendations:
        video_result = video.copy()
        video_result['recommendation_score'] = video.get('personality_score', 0.0)
        video_result['rl_score'] = rl_score
        video_result['combined_score'] = (video_result['recommendation_score'] + rl_score) / 2
        video_result['source'] = 'personalized'
        final_recommendations.append(video_result)

    for video in trending_videos[:5]:
        video_result = video.copy()
        video_result['recommendation_score'] = video.get('personality_score', 0.0)
        video_result['rl_score'] = 0.0
        video_result['combined_score'] = video_result['recommendation_score']
        video_result['source'] = 'trending'
        final_recommendations.append(video_result)

    final_map = {video['id']: video for video in final_recommendations if video.get('id')}

    for cluster in genre_clusters:
        for video in cluster['videos']:
            video_id = video.get('id')
            if not video_id:
                continue
            if request.category_filter and video.get('category_name') and request.category_filter.lower() not in video.get('category_name', '').lower():
                continue
            if video_id not in final_map:
                final_map[video_id] = video
            else:
                final_map[video_id].setdefault('genre', video.get('genre'))
                final_map[video_id].setdefault('genre_rank', video.get('genre_rank'))
                final_map[video_id].setdefault('genre_combined_score', video.get('genre_combined_score'))

    final_recommendations = list(final_map.values())
    final_recommendations.sort(key=lambda x: x.get('combined_score', 0.0), reverse=True)

    minimum_cluster_count = sum(len(cluster['videos']) for cluster in genre_clusters)
    limit = max(request.max_results, minimum_cluster_count)
    final_recommendations = final_recommendations[:limit]

    payload = {
        "recommendations": final_recommendations,
        "genre_clusters": genre_clusters,
        "total_count": len(final_recommendations),
        "personality_profile": {
            trait.value: score for trait, score in personality_profile.items()
        },
        "refresh_time": datetime.now().isoformat(),
        "next_refresh": video_agent.should_refresh_recommendations()
    }

    return payload


async def _prepare_user_context(user_id: str, supabase) -> Tuple[Dict[PersonalityTrait, float], List[Dict[str, Any]]]:
    """Fetch personality profile and watch history required for recommendations."""

    personality_service = get_personality_service()
    user_context = await personality_service.get_user_personality_context(user_id)

    if not user_context.has_assessment:
        raise HTTPException(
            status_code=400,
            detail="User has not completed personality assessment"
        )

    personality_profile: Dict[PersonalityTrait, float] = {}
    for trait in PersonalityTrait:
        score = getattr(user_context.personality_profile.scores, trait.value, 50)
        personality_profile[trait] = score / 100.0

    watch_history = await _fetch_user_watch_history(user_id, supabase)
    return personality_profile, watch_history


@router.get("/recommendations/{user_id}")
async def get_video_recommendations_get(
    user_id: str,
    background_tasks: BackgroundTasks,
    max_results: int = 20,
    force_refresh: bool = False,
    include_trending: bool = True,
    category_filter: Optional[str] = None,
    supabase=Depends(get_supabase_client)
):
    """GET version of video recommendations endpoint."""
    request = VideoRecommendationRequest(
        max_results=max_results,
        force_refresh=force_refresh,
        include_trending=include_trending,
        category_filter=category_filter
    )
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
        cache_key = _build_recommendation_cache_key(user_id, request)

        if not request.force_refresh:
            cached_entry = await _load_cached_recommendations(cache_key)
            if cached_entry:
                payload = cached_entry.get("payload") if isinstance(cached_entry, dict) else cached_entry
                response: Dict[str, Any] = {
                    "success": True,
                    "data": payload,
                    "cache_hit": True
                }
                if isinstance(cached_entry, dict):
                    if cached_entry.get("cached_at"):
                        response["cache_timestamp"] = cached_entry["cached_at"]
                    if cached_entry.get("ttl_seconds"):
                        response["cache_ttl"] = cached_entry["ttl_seconds"]
                return response

        personality_profile, watch_history = await _prepare_user_context(user_id, supabase)
        video_agent = VideoIntelligenceAgent(user_id)

        payload = await _generate_recommendation_payload(
            user_id=user_id,
            video_agent=video_agent,
            personality_profile=personality_profile,
            watch_history=watch_history,
            request=request
        )

        cache_record = {
            "payload": payload,
            "cached_at": datetime.now().isoformat(),
            "ttl_seconds": RECOMMENDATION_CACHE_TTL
        }
        await _store_cached_recommendations(cache_key, cache_record)

        return {
            "success": True,
            "data": payload,
            "cache_hit": False,
            "cache_timestamp": cache_record["cached_at"],
        }

    except HTTPException:
        raise
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
            'time_to_click': feedback.time_to_click,
            # Include video metadata for database storage
            'video_title': feedback.video_title,
            'channel_title': feedback.channel_title,
            'category_name': feedback.category_name
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