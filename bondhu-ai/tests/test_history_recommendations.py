#!/usr/bin/env python3
"""
Test improved watch history-based video recommendations
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to sys.path to import from core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.services.youtube_service import YouTubeService
from core.database.models import PersonalityTrait

load_dotenv()

async def test_history_recommendations():
    """Test the improved history-based recommendation system."""
    print("Testing improved watch history-based recommendations...")
    
    # Mock personality profile (moderate scores)
    personality_profile = {
        PersonalityTrait.OPENNESS: 0.7,
        PersonalityTrait.CONSCIENTIOUSNESS: 0.6,
        PersonalityTrait.EXTRAVERSION: 0.5,
        PersonalityTrait.AGREEABLENESS: 0.8,
        PersonalityTrait.NEUROTICISM: 0.3
    }
    
    # Mock watch history indicating interest in education and technology
    mock_watch_history = [
        {
            'video_id': 'test1',
            'video_title': 'Python Programming Tutorial',
            'channel_title': 'Tech Academy',
            'category_name': 'Education',
            'watch_time': 600,
            'completion_rate': 0.9
        },
        {
            'video_id': 'test2',
            'video_title': 'Machine Learning Basics',
            'channel_title': 'AI Channel',
            'category_name': 'Science & Technology',
            'watch_time': 800,
            'completion_rate': 0.8
        },
        {
            'video_id': 'test3',
            'video_title': 'Web Development Course',
            'channel_title': 'Code School',
            'category_name': 'Education',
            'watch_time': 1200,
            'completion_rate': 1.0
        }
    ]
    
    api_key = os.getenv("YOUTUBE_API_KEY")
    youtube_service = YouTubeService(api_key)
    
    print("\n=== Test 1: No Watch History (Pure Personality) ===")
    try:
        no_history_recs = await youtube_service.get_personalized_recommendations(
            personality_profile=personality_profile,
            user_history=[],
            max_results=10
        )
        print(f"✅ No history recommendations: {len(no_history_recs)} videos")
        source_counts = {}
        for video in no_history_recs:
            source = video.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        print(f"   Sources: {source_counts}")
    except Exception as e:
        print(f"❌ No history test failed: {e}")
    
    print("\n=== Test 2: With Watch History (Hybrid) ===")
    try:
        history_recs = await youtube_service.get_personalized_recommendations(
            personality_profile=personality_profile,
            user_history=mock_watch_history,
            max_results=10
        )
        print(f"✅ History-based recommendations: {len(history_recs)} videos")
        
        # Analyze sources
        source_counts = {}
        for video in history_recs:
            source = video.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        print(f"   Sources: {source_counts}")
        
        # Show sample recommendations
        print("\n   Sample recommendations:")
        for i, video in enumerate(history_recs[:3]):
            source = video.get('source', 'unknown')
            title = video.get('title', 'Unknown Title')
            category = video.get('history_category') or video.get('personality_category') or video.get('category_name', 'Unknown')
            print(f"   {i+1}. [{source}] {title} (Category: {category})")
        
    except Exception as e:
        print(f"❌ History-based test failed: {e}")
    
    print("\n=== Test 3: History-Based Recommendations Only ===")
    try:
        history_only = await youtube_service._get_history_based_recommendations(
            mock_watch_history, 5
        )
        print(f"✅ Pure history recommendations: {len(history_only)} videos")
        
        for i, video in enumerate(history_only):
            title = video.get('title', 'Unknown Title')
            source = video.get('source', 'unknown')
            category = video.get('history_category', 'Unknown')
            print(f"   {i+1}. [{source}] {title} (Category: {category})")
        
    except Exception as e:
        print(f"❌ Pure history test failed: {e}")
    
    print("\n=== Test 4: Hybrid Recommendations Only ===")
    try:
        hybrid_only = await youtube_service._get_hybrid_recommendations(
            personality_profile, mock_watch_history, 3
        )
        print(f"✅ Hybrid recommendations: {len(hybrid_only)} videos")
        
        for i, video in enumerate(hybrid_only):
            title = video.get('title', 'Unknown Title')
            source = video.get('source', 'unknown')
            category = video.get('hybrid_category', 'Unknown')
            score = video.get('hybrid_score', 0)
            print(f"   {i+1}. [{source}] {title} (Category: {category}, Score: {score:.2f})")
        
    except Exception as e:
        print(f"❌ Hybrid test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_history_recommendations())