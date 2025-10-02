#!/usr/bin/env python3
"""
Simple test script to debug video recommendations
"""

import asyncio
import logging
from core.services.youtube_service import YouTubeService
from core.database.models import PersonalityTrait

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_youtube_service():
    """Test the YouTube service directly."""
    youtube_service = YouTubeService()
    
    # Test simple search
    logger.info("Testing simple video search...")
    search_results = await youtube_service.search_videos("music", max_results=5)
    logger.info(f"Search results: {len(search_results)} videos found")
    
    if search_results:
        for video in search_results[:2]:
            logger.info(f"Video: {video.get('title', 'Unknown')}")
    else:
        logger.error("No videos found in search!")
    
    # Test personalized recommendations with a fake personality profile
    logger.info("Testing personalized recommendations...")
    fake_personality = {
        PersonalityTrait.OPENNESS: 0.7,
        PersonalityTrait.CONSCIENTIOUSNESS: 0.6,
        PersonalityTrait.EXTRAVERSION: 0.5,
        PersonalityTrait.AGREEABLENESS: 0.8,
        PersonalityTrait.NEUROTICISM: 0.3
    }
    
    personalized_results = await youtube_service.get_personalized_recommendations(
        personality_profile=fake_personality,
        user_history=[],
        max_results=10
    )
    
    logger.info(f"Personalized results: {len(personalized_results)} videos found")
    
    if personalized_results:
        for video in personalized_results[:3]:
            logger.info(f"Personalized video: {video.get('title', 'Unknown')} - Score: {video.get('personality_score', 0)}")
    else:
        logger.error("No personalized videos found!")

if __name__ == "__main__":
    asyncio.run(test_youtube_service())