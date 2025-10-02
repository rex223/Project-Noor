"""History & personality integrated video recommender.

Combines:
- Stored watch history (user_video_history table) via Supabase
- Current personality profile (if available) else balanced defaults
- Category & behavior signals to weight recommendations
- Uses existing VideoIntelligenceAgent + YouTubeService for retrieval

Also computes a proposed personality adjustment (not auto-applied) derived
from dominant watch categories vs current trait levels.

Limitations:
- True YouTube watch history API not implemented; relies on internal stored events
- Personality update is heuristic; returns suggested adjustments only
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime, timedelta

from core.database.personality_service import get_personality_service
from core.database.models import PersonalityTrait
from core.database.supabase_client import get_supabase_client
from agents.video.video_agent import VideoIntelligenceAgent

logger = logging.getLogger("bondhu.history_recommender")

DEFAULT_PERSONALITY = {
    PersonalityTrait.OPENNESS: 0.5,
    PersonalityTrait.CONSCIENTIOUSNESS: 0.5,
    PersonalityTrait.EXTRAVERSION: 0.5,
    PersonalityTrait.AGREEABLENESS: 0.5,
    PersonalityTrait.NEUROTICISM: 0.5,
}

CATEGORY_TRAIT_INFLUENCE: Dict[str, Dict[PersonalityTrait, float]] = {
    # Education / learning categories → openness + conscientiousness
    'Education': {PersonalityTrait.OPENNESS: 0.4, PersonalityTrait.CONSCIENTIOUSNESS: 0.2},
    'Science & Technology': {PersonalityTrait.OPENNESS: 0.35, PersonalityTrait.CONSCIENTIOUSNESS: 0.15},
    'Documentary': {PersonalityTrait.OPENNESS: 0.45},
    'Howto & Style': {PersonalityTrait.CONSCIENTIOUSNESS: 0.35},
    'Productivity': {PersonalityTrait.CONSCIENTIOUSNESS: 0.4},
    # Social / expressive
    'Entertainment': {PersonalityTrait.EXTRAVERSION: 0.3},
    'Comedy': {PersonalityTrait.EXTRAVERSION: 0.4, PersonalityTrait.AGREEABLENESS: 0.2},
    'Music': {PersonalityTrait.EXTRAVERSION: 0.25, PersonalityTrait.OPENNESS: 0.2},
    'Sports': {PersonalityTrait.EXTRAVERSION: 0.35},
    'Gaming': {PersonalityTrait.EXTRAVERSION: 0.25, PersonalityTrait.OPENNESS: 0.2},
    # Empathy / prosocial
    'Pets & Animals': {PersonalityTrait.AGREEABLENESS: 0.3},
    'Nonprofits & Activism': {PersonalityTrait.AGREEABLENESS: 0.4, PersonalityTrait.CONSCIENTIOUSNESS: 0.2},
    'People & Blogs': {PersonalityTrait.AGREEABLENESS: 0.25},
    # Emotional / stability (neuroticism inverse cues not strong here, left blank)
}

@dataclass
class WatchHistorySummary:
    total_videos: int
    total_watch_time_seconds: float
    category_counts: Dict[str, int]
    category_watch_time: Dict[str, float]
    top_categories: List[Tuple[str, int]]


def _normalize_trait_value(value: float) -> float:
    return min(max(value, 0.0), 1.0)

async def _fetch_watch_history(user_id: str, limit: int = 300) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    try:
        result = supabase.supabase.table("user_video_history").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return result.data or []
    except Exception as exc:
        logger.error("Failed to fetch watch history for %s: %s", user_id, exc)
        return []

async def _build_personality_profile(user_id: str) -> Dict[PersonalityTrait, float]:
    service = get_personality_service()
    try:
        ctx = await service.get_user_personality_context(user_id)
        if not ctx.has_assessment or not ctx.personality_profile:
            return DEFAULT_PERSONALITY.copy()
        scores = ctx.personality_profile.scores  # dict[str, int]
        profile: Dict[PersonalityTrait, float] = {}
        for trait in PersonalityTrait:
            raw = scores.get(trait.value, 50) or 50
            profile[trait] = _normalize_trait_value(raw / 100.0)
        return profile
    except Exception as exc:
        logger.warning("Using default personality for %s due to error: %s", user_id, exc)
        return DEFAULT_PERSONALITY.copy()

def _summarize_watch_history(history: List[Dict[str, Any]]) -> WatchHistorySummary:
    counts: Dict[str, int] = {}
    watch_time: Dict[str, float] = {}
    total_time = 0.0
    for item in history:
        category = item.get('category_name') or item.get('category') or 'Unknown'
        counts[category] = counts.get(category, 0) + 1
        wt = 0.0
        for key in ('watch_time', 'watch_time_seconds', 'duration_seconds'):
            if key in item and isinstance(item[key], (int, float)):
                wt = float(item[key])
                break
        watch_time[category] = watch_time.get(category, 0.0) + wt
        total_time += wt
    top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:10]
    return WatchHistorySummary(
        total_videos=len(history),
        total_watch_time_seconds=total_time,
        category_counts=counts,
        category_watch_time=watch_time,
        top_categories=top,
    )

def _propose_personality_adjustments(summary: WatchHistorySummary, current: Dict[PersonalityTrait, float]) -> Dict[str, Any]:
    """Suggest potential slight nudges to personality based on viewing distribution."""
    adjustments: Dict[str, Dict[str, float]] = {}
    total_videos = max(summary.total_videos, 1)
    for category, count in summary.top_categories:
        if category in CATEGORY_TRAIT_INFLUENCE:
            influence_map = CATEGORY_TRAIT_INFLUENCE[category]
            weight = count / total_videos
            for trait, influence in influence_map.items():
                delta = influence * weight * 0.2  # scale down for subtlety
                trait_key = trait.value
                if trait_key not in adjustments:
                    adjustments[trait_key] = {"suggested_delta": 0.0, "sources": []}
                adjustments[trait_key]["suggested_delta"] += delta
                adjustments[trait_key]["sources"].append({
                    "category": category,
                    "weight": round(weight, 3),
                    "influence": influence,
                    "delta_contrib": round(delta, 4),
                })
    # Clamp proposed delta lifetime
    for trait_key, data in adjustments.items():
        data["suggested_delta"] = round(_normalize_trait_value(current.get(PersonalityTrait(trait_key), 0.5) + data["suggested_delta"]) - current.get(PersonalityTrait(trait_key), 0.5), 4)
    return adjustments

async def get_history_based_recommendations(user_id: str, max_results: int = 30, include_persona_adjustments: bool = True) -> Dict[str, Any]:
    """Generate recommendations using both personality profile & watch history signals."""
    history = await _fetch_watch_history(user_id)
    personality_profile = await _build_personality_profile(user_id)

    agent = VideoIntelligenceAgent(user_id)
    recommendations = await agent.get_personalized_recommendations(
        personality_profile=personality_profile,
        watch_history=history,
        max_results=max_results,
        force_refresh=True,
    )

    summary = _summarize_watch_history(history)
    adjustments: Dict[str, Any] = {}
    if include_persona_adjustments:
        adjustments = _propose_personality_adjustments(summary, personality_profile)

    return {
        "success": True,
        "data": {
            "recommendations": recommendations,
            "watch_history_summary": {
                "total_videos": summary.total_videos,
                "total_watch_time_seconds": summary.total_watch_time_seconds,
                "top_categories": summary.top_categories,
            },
            "category_counts": summary.category_counts,
            "category_watch_time": summary.category_watch_time,
            "personality_profile": {t.value: v for t, v in personality_profile.items()},
            "personality_adjustments": adjustments,
            "generated_at": datetime.utcnow().isoformat(),
        }
    }
