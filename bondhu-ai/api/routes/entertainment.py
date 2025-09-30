"""
Entertainment API endpoints for Bondhu AI content recommendations.
Integrates personality analysis with entertainment recommendations.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse

from core import get_config
from core.database.personality_service import get_personality_service
from api.models.schemas import (
    EntertainmentRecommendationDB,
    EntertainmentInteraction,
    APIResponse
)

# Create router
entertainment_router = APIRouter(prefix="/api/v1/entertainment", tags=["entertainment"])

# Configure logging
logger = logging.getLogger(__name__)

@entertainment_router.get("/recommendations/{user_id}")
async def get_entertainment_recommendations(
    user_id: str,
    content_types: Optional[str] = Query(None, description="Comma-separated list: music,video,game"),
    limit: int = Query(20, ge=1, le=100),
    refresh: bool = Query(False, description="Force refresh recommendations")
) -> APIResponse[Dict[str, Any]]:
    """
    Get personalized entertainment recommendations for a user.
    
    Args:
        user_id: User ID to get recommendations for
        content_types: Filter by content types (music, video, game)
        limit: Maximum number of recommendations per type
        refresh: Whether to generate fresh recommendations
        
    Returns:
        Entertainment recommendations with metadata
    """
    try:
        config = get_config()
        personality_service = get_personality_service()
        
        # Parse content types
        requested_types = []
        if content_types:
            requested_types = [t.strip() for t in content_types.split(',')]
        else:
            requested_types = ['music', 'video', 'game']
        
        # Get user's personality context
        personality_context = await personality_service.get_personality_context(user_id)
        
        # Generate recommendations for each content type
        recommendations_data = {
            'user_id': user_id,
            'music_recommendations': [],
            'video_recommendations': [],
            'game_recommendations': [],
            'context': {
                'generated_at': datetime.now().isoformat(),
                'personality_based': bool(personality_context),
                'content_types': requested_types,
                'total_recommendations': 0
            }
        }
        
        total_recommendations = 0
        
        # Generate music recommendations
        if 'music' in requested_types:
            music_recs = await _generate_music_recommendations(
                user_id, personality_context, limit // len(requested_types)
            )
            recommendations_data['music_recommendations'] = music_recs
            total_recommendations += len(music_recs)
        
        # Generate video recommendations  
        if 'video' in requested_types:
            video_recs = await _generate_video_recommendations(
                user_id, personality_context, limit // len(requested_types)
            )
            recommendations_data['video_recommendations'] = video_recs
            total_recommendations += len(video_recs)
        
        # Generate game recommendations
        if 'game' in requested_types:
            game_recs = await _generate_game_recommendations(
                user_id, personality_context, limit // len(requested_types)
            )
            recommendations_data['game_recommendations'] = game_recs
            total_recommendations += len(game_recs)
        
        recommendations_data['context']['total_recommendations'] = total_recommendations
        
        return APIResponse[Dict[str, Any]](
            success=True,
            data=recommendations_data,
            message=f"Generated {total_recommendations} entertainment recommendations"
        )
        
    except Exception as e:
        logger.error(f"Error getting entertainment recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )


@entertainment_router.post("/interaction")
async def record_entertainment_interaction(
    interaction: EntertainmentInteraction
) -> APIResponse[Dict[str, str]]:
    """
    Record user interaction with entertainment content.
    
    Args:
        interaction: Entertainment interaction data
        
    Returns:
        Confirmation of recorded interaction
    """
    try:
        # TODO: Store interaction in database
        # For now, just log it
        logger.info(f"Entertainment interaction: {interaction.user_id} {interaction.interaction_type} {interaction.content_type}")
        
        return APIResponse[Dict[str, str]](
            success=True,
            data={"interaction_id": str(uuid.uuid4())},
            message="Interaction recorded successfully"
        )
        
    except Exception as e:
        logger.error(f"Error recording interaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record interaction: {str(e)}"
        )


async def _generate_music_recommendations(
    user_id: str, 
    personality_context: Any, 
    limit: int
) -> List[Dict[str, Any]]:
    """Generate music recommendations based on personality."""
    
    # Sample music recommendations based on personality traits
    base_recommendations = [
        {
            "id": f"music-{uuid.uuid4()}",
            "title": "Chill Vibes Playlist",
            "type": "music",
            "description": "Perfect for relaxation and focus",
            "url": "https://open.spotify.com/playlist/example1",
            "thumbnail_url": "https://via.placeholder.com/300x300?text=Chill+Vibes",
            "score": 0.85,
            "reasoning": "Based on your personality, you might enjoy calming music for stress relief",
            "metadata": {
                "genre": "ambient",
                "mood": "relaxing",
                "energy_level": "low"
            }
        },
        {
            "id": f"music-{uuid.uuid4()}",
            "title": "Upbeat Motivation Mix",
            "type": "music", 
            "description": "Energetic tracks to boost your mood",
            "url": "https://open.spotify.com/playlist/example2",
            "thumbnail_url": "https://via.placeholder.com/300x300?text=Upbeat+Mix",
            "score": 0.78,
            "reasoning": "High-energy music to match your extraverted tendencies",
            "metadata": {
                "genre": "pop",
                "mood": "energetic",
                "energy_level": "high"
            }
        },
        {
            "id": f"music-{uuid.uuid4()}",
            "title": "Classical Focus",
            "type": "music",
            "description": "Classical pieces for concentration",
            "url": "https://open.spotify.com/playlist/example3",
            "thumbnail_url": "https://via.placeholder.com/300x300?text=Classical",
            "score": 0.72,
            "reasoning": "Your openness to experience suggests you'd appreciate classical complexity",
            "metadata": {
                "genre": "classical",
                "mood": "contemplative", 
                "energy_level": "medium"
            }
        }
    ]
    
    return base_recommendations[:limit]


async def _generate_video_recommendations(
    user_id: str,
    personality_context: Any,
    limit: int
) -> List[Dict[str, Any]]:
    """Generate video recommendations based on personality."""
    
    base_recommendations = [
        {
            "id": f"video-{uuid.uuid4()}",
            "title": "Mindfulness and Mental Health",
            "type": "video",
            "description": "Learn techniques for better mental wellness",
            "url": "https://youtube.com/watch?v=example1",
            "thumbnail_url": "https://via.placeholder.com/480x360?text=Mindfulness",
            "score": 0.88,
            "reasoning": "Aligns with your interest in personal growth and mental wellness",
            "metadata": {
                "category": "wellness",
                "duration": "15:30",
                "channel": "Mental Health Academy"
            }
        },
        {
            "id": f"video-{uuid.uuid4()}",
            "title": "Creative Problem Solving",
            "type": "video",
            "description": "Innovative approaches to challenges",
            "url": "https://youtube.com/watch?v=example2", 
            "thumbnail_url": "https://via.placeholder.com/480x360?text=Problem+Solving",
            "score": 0.82,
            "reasoning": "Your openness suggests you'd enjoy creative thinking content",
            "metadata": {
                "category": "education",
                "duration": "22:15",
                "channel": "Innovation Hub"
            }
        },
        {
            "id": f"video-{uuid.uuid4()}",
            "title": "Nature Documentary",
            "type": "video",
            "description": "Relaxing nature scenes and wildlife",
            "url": "https://youtube.com/watch?v=example3",
            "thumbnail_url": "https://via.placeholder.com/480x360?text=Nature",
            "score": 0.75,
            "reasoning": "Calming content that matches your need for stress relief",
            "metadata": {
                "category": "documentary",
                "duration": "45:00",
                "channel": "Nature World"
            }
        }
    ]
    
    return base_recommendations[:limit]


async def _generate_game_recommendations(
    user_id: str,
    personality_context: Any, 
    limit: int
) -> List[Dict[str, Any]]:
    """Generate game recommendations based on personality."""
    
    base_recommendations = [
        {
            "id": f"game-{uuid.uuid4()}",
            "title": "Stardew Valley",
            "type": "game",
            "description": "Relaxing farming simulation game",
            "url": "https://store.steampowered.com/app/413150/Stardew_Valley/",
            "thumbnail_url": "https://via.placeholder.com/300x400?text=Stardew+Valley",
            "score": 0.90,
            "reasoning": "Perfect for relaxation and stress relief with gentle gameplay",
            "metadata": {
                "genre": "simulation",
                "platform": "PC, Console, Mobile",
                "rating": "E10+"
            }
        },
        {
            "id": f"game-{uuid.uuid4()}",
            "title": "Journey",
            "type": "game",
            "description": "Beautiful exploration and discovery game",
            "url": "https://store.steampowered.com/app/638230/Journey/",
            "thumbnail_url": "https://via.placeholder.com/300x400?text=Journey",
            "score": 0.85,
            "reasoning": "Artistic and emotionally engaging, perfect for your openness trait",
            "metadata": {
                "genre": "adventure",
                "platform": "PC, Console",
                "rating": "E"
            }
        },
        {
            "id": f"game-{uuid.uuid4()}",
            "title": "Chess.com",
            "type": "game",
            "description": "Strategic chess gameplay online",
            "url": "https://chess.com",
            "thumbnail_url": "https://via.placeholder.com/300x400?text=Chess",
            "score": 0.78,
            "reasoning": "Strategic thinking aligns with your conscientiousness",
            "metadata": {
                "genre": "strategy",
                "platform": "Web, Mobile",
                "rating": "E"
            }
        }
    ]
    
    return base_recommendations[:limit]