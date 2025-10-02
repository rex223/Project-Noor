"""
Setup script for YouTube API integration and video entertainment system.
Ensures all dependencies are configured and API keys are set.
"""

import os
import sys
import asyncio
from core.config.settings import get_config
from core.services.youtube_service import YouTubeService
from agents.video.video_agent import VideoIntelligenceAgent
from core.database.models import PersonalityTrait

async def test_youtube_integration():
    """Test YouTube API integration and video recommendations."""
    print("🎬 Testing YouTube Integration and Video Recommendations")
    print("=" * 60)
    
    # Check configuration
    config = get_config()
    print(f"✓ Configuration loaded")
    print(f"  YouTube API Key: {'✓ Set' if config.youtube.api_key else '❌ Missing'}")
    print(f"  Google API Key: {'✓ Set' if config.google.api_key else '❌ Missing'}")
    print(f"  Supabase URL: {'✓ Set' if config.database.url else '❌ Missing'}")
    
    if not config.youtube.api_key:
        print("\n❌ YouTube API key is required for video recommendations")
        print("   Please set YOUTUBE_API_KEY in your .env file")
        return False
    
    # Test YouTube service
    print(f"\n🔍 Testing YouTube Service...")
    youtube_service = YouTubeService(config.youtube.api_key)
    
    try:
        # Test trending videos
        trending = await youtube_service.get_trending_videos(max_results=5)
        print(f"✓ Retrieved {len(trending)} trending videos")
        
        if trending:
            sample_video = trending[0]
            print(f"  Sample: '{sample_video['title'][:50]}...' by {sample_video['channel_title']}")
    
    except Exception as e:
        print(f"❌ YouTube API test failed: {e}")
        return False
    
    # Test video agent with sample personality
    print(f"\n🤖 Testing Video Intelligence Agent...")
    test_user_id = "test-user-123"
    video_agent = VideoIntelligenceAgent(test_user_id, config.youtube.api_key)
    
    # Sample personality profile (balanced personality)
    sample_personality = {
        PersonalityTrait.OPENNESS: 75.0,
        PersonalityTrait.CONSCIENTIOUSNESS: 60.0,
        PersonalityTrait.EXTRAVERSION: 45.0,
        PersonalityTrait.AGREEABLENESS: 80.0,
        PersonalityTrait.NEUROTICISM: 35.0
    }
    
    try:
        # Test personalized recommendations
        recommendations = await video_agent.get_personalized_recommendations(
            personality_profile=sample_personality,
            watch_history=[],
            max_results=10
        )
        
        print(f"✓ Generated {len(recommendations)} personalized recommendations")
        
        if recommendations:
            # Show top 3 recommendations
            for i, video in enumerate(recommendations[:3], 1):
                match_score = int(video.get('personality_score', 0) * 100)
                print(f"  {i}. '{video['title'][:40]}...' ({match_score}% match)")
                print(f"     Category: {video.get('category_name', 'Unknown')}")
                print(f"     Watch: {video.get('watch_url', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Video agent test failed: {e}")
        return False
    
    # Test personality-based search queries
    print(f"\n🧠 Testing Personality-Based Query Generation...")
    query_generator = youtube_service._generate_personality_queries(sample_personality)
    print(f"✓ Generated {len(query_generator)} personality-based queries:")
    for query in query_generator[:5]:
        print(f"  - '{query}'")
    
    print(f"\n🎯 Testing Category Preference Mapping...")
    preferred_categories = youtube_service._get_preferred_categories(sample_personality)
    print(f"✓ Top 5 preferred categories for this personality:")
    for category, score in preferred_categories[:5]:
        print(f"  - {category}: {score:.2f}")
    
    print(f"\n✅ All tests passed! YouTube integration is working correctly.")
    print(f"\n📊 Summary:")
    print(f"  - YouTube API: Working ✓")
    print(f"  - Video recommendations: Working ✓")
    print(f"  - Personality matching: Working ✓")
    print(f"  - Search query generation: Working ✓")
    print(f"  - Category preferences: Working ✓")
    
    return True

async def test_entertainment_api():
    """Test the entertainment API endpoints."""
    print(f"\n🌐 Testing Entertainment API Endpoints...")
    
    try:
        import aiohttp
        
        base_url = "http://localhost:8000/api/v1"
        test_user_id = "test-user-123"
        
        async with aiohttp.ClientSession() as session:
            # Test video recommendations endpoint
            url = f"{base_url}/video/recommendations/{test_user_id}?max_results=5"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ Video recommendations API working")
                    print(f"  Retrieved {data.get('total_count', 0)} recommendations")
                else:
                    print(f"❌ Video recommendations API failed: {response.status}")
                    return False
            
            # Test feedback endpoint
            feedback_data = {
                "user_id": test_user_id,
                "video_id": "test_video_123",
                "feedback_type": "like",
                "additional_data": {"test": True}
            }
            
            async with session.post(f"{base_url}/video/feedback", json=feedback_data) as response:
                if response.status == 200:
                    print(f"✓ Video feedback API working")
                else:
                    print(f"❌ Video feedback API failed: {response.status}")
                    return False
    
    except Exception as e:
        print(f"❌ Entertainment API test failed: {e}")
        print(f"   Make sure the FastAPI server is running on localhost:8000")
        return False
    
    return True

def check_database_schema():
    """Check if the required database tables exist."""
    print(f"\n🗄️ Database Schema Check...")
    print(f"Please ensure these tables exist in your Supabase database:")
    print(f"  - video_feedback")
    print(f"  - user_video_history") 
    print(f"  - video_recommendations_cache")
    print(f"  - entertainment_preferences")
    print(f"\nRun the SQL script: database/video_entertainment_schema.sql")

def main():
    """Main setup and test function."""
    print("🎬 Bondhu AI - YouTube Video Entertainment Setup")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check environment variables
    required_env_vars = ['YOUTUBE_API_KEY', 'GOOGLE_API_KEY', 'SUPABASE_URL']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print(f"\nPlease add these to your .env file")
        return False
    
    print(f"✓ All required environment variables are set")
    
    # Run async tests
    success = asyncio.run(test_youtube_integration())
    
    if success:
        print(f"\n🎉 Setup completed successfully!")
        print(f"\nNext steps:")
        print(f"1. Run the FastAPI server: python main.py")
        print(f"2. Set up the database schema (see database/video_entertainment_schema.sql)")
        print(f"3. Test the frontend video section")
        print(f"4. Start getting personalized video recommendations!")
    else:
        print(f"\n❌ Setup failed. Please check the errors above.")
    
    check_database_schema()
    return success

if __name__ == "__main__":
    main()