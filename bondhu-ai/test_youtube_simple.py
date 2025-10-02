#!/usr/bin/env python3
"""
Simple YouTube API test to verify integration works.
Tests API key, fetches trending videos, and analyzes genres.
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from core.services.youtube_service import YouTubeService
from core.database.models import PersonalityTrait  # Enum

async def test_youtube_integration():
    """Test YouTube Data API integration."""
    
    print("🔍 Testing YouTube Data API Integration...")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ YOUTUBE_API_KEY not found in environment variables")
        return False
        
    print(f"✅ YouTube API Key found: {api_key[:10]}...")
    
    # Initialize YouTube service
    try:
        youtube_service = YouTubeService(api_key)
        print("✅ YouTube service initialized")
    except Exception as e:
        print(f"❌ Failed to initialize YouTube service: {e}")
        return False
    
    # Test 1: Fetch trending videos
    print("\n📺 Testing trending videos fetch...")
    try:
        trending_videos = await youtube_service.get_trending_videos(max_results=5)
        if trending_videos:
            print(f"✅ Fetched {len(trending_videos)} trending videos")
            for i, video in enumerate(trending_videos[:3], 1):
                print(f"   {i}. {video.get('title', 'No title')[:50]}...")
                print(f"      Category: {video.get('category_name', 'Unknown')}")
        else:
            print("⚠️  No trending videos returned (might be quota/API issue)")
    except Exception as e:
        print(f"❌ Error fetching trending videos: {e}")
        return False
    
    # Test 2: Test search functionality
    print("\n🔍 Testing video search...")
    try:
        search_results = await youtube_service.search_videos("python tutorial", max_results=3)
        if search_results:
            print(f"✅ Search returned {len(search_results)} results")
            for i, video in enumerate(search_results, 1):
                print(f"   {i}. {video.get('title', 'No title')[:50]}...")
        else:
            print("⚠️  No search results returned")
    except Exception as e:
        print(f"❌ Error in video search: {e}")
    
    # Test 3: Test personality-based recommendations
    print("\n🧠 Testing personality-based recommendations...")
    try:
        # Sample personality profile - high openness (curious learner)
        personality_profile = {
            PersonalityTrait.OPENNESS: 0.8,
            PersonalityTrait.CONSCIENTIOUSNESS: 0.6,
            PersonalityTrait.EXTRAVERSION: 0.5,
            PersonalityTrait.AGREEABLENESS: 0.7,
            PersonalityTrait.NEUROTICISM: 0.3
        }
        
        recommendations = await youtube_service.get_personalized_recommendations(
            personality_profile=personality_profile,
            user_history=[],  # Empty history for test
            max_results=5
        )
        
        if recommendations:
            print(f"✅ Generated {len(recommendations)} personalized recommendations")
            for i, video in enumerate(recommendations[:3], 1):
                title = video.get('title', 'No title')[:40]
                score = video.get('personality_score', 0)
                category = video.get('category_name', 'Unknown')
                print(f"   {i}. {title}... (Score: {score:.2f}, Category: {category})")
        else:
            print("⚠️  No personalized recommendations generated")
            
    except Exception as e:
        print(f"❌ Error generating recommendations: {e}")
    
    print("\n" + "=" * 50)
    print("✅ YouTube integration test completed!")
    return True

if __name__ == "__main__":
    asyncio.run(test_youtube_integration())