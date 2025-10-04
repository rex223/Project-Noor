"""Simple video recommendation service wrapping SimpleYouTubeRecommender.

Provides an async-friendly interface and personality fallback handling so it can
be safely called inside FastAPI endpoints without depending on the complex agent stack.
"""
from __future__ import annotations

import os
import asyncio
from typing import Dict, Any, List, Optional
import logging

from simple_youtube_recommender import SimpleYouTubeRecommender
from core.database.personality_service import get_personality_service
from core.database.models import PersonalityTrait

logger = logging.getLogger("bondhu.simple_recommender")

# Cache recommender instances per user (for rate limiting)
_recommenders: Dict[str, SimpleYouTubeRecommender] = {}

def get_simple_recommender(user_id: str = "default_user") -> SimpleYouTubeRecommender:
    global _recommenders
    if user_id not in _recommenders:
        api_key = os.getenv("YOUTUBE_API_KEY")
        _recommenders[user_id] = SimpleYouTubeRecommender(api_key=api_key, user_id=user_id)
    return _recommenders[user_id]

async def build_personality_dict(user_id: str) -> Dict[str, float]:
    """Build a flat personality dict (0-1 floats) for simple recommender.

    Falls back to balanced traits if assessment missing or service errors.
    """
    try:
        personality_service = get_personality_service()
        user_context = await personality_service.get_user_personality_context(user_id)
        if not user_context.has_assessment or not user_context.personality_profile:
            return {
                'openness': 0.5,
                'conscientiousness': 0.5,
                'extraversion': 0.5,
                'agreeableness': 0.5,
                'neuroticism': 0.5,
            }
        scores = user_context.personality_profile.scores
        # scores is Dict[str, int] 0-100
        def norm(key: str) -> float:
            return min(max(scores.get(key, 50) / 100.0, 0.0), 1.0)
        return {
            'openness': norm('openness'),
            'conscientiousness': norm('conscientiousness'),
            'extraversion': norm('extraversion'),
            'agreeableness': norm('agreeableness'),
            'neuroticism': norm('neuroticism'),
        }
    except Exception as exc:
        logger.warning("Falling back to default personality for %s: %s", user_id, exc)
        return {
            'openness': 0.5,
            'conscientiousness': 0.5,
            'extraversion': 0.5,
            'agreeableness': 0.5,
            'neuroticism': 0.5,
        }

async def get_simple_recommendations(user_id: str, max_results: int = 20) -> Dict[str, Any]:
    """Return personalized simple recommendations payload.

    Structure mirrors existing advanced endpoint but simplified.
    """
    recommender = get_simple_recommender(user_id)
    personality = await build_personality_dict(user_id)

    try:
        videos = await recommender.get_personalized_recommendations(
            user_personality=personality,
            max_results=max_results,
        )
    except Exception as exc:
        logger.error("Simple recommender failure for %s: %s", user_id, exc)
        videos = []

    return {
        'success': True,
        'data': {
            'recommendations': videos,
            'personality_profile': personality,
            'total_count': len(videos),
        }
    }
