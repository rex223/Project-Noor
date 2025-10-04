#!/usr/bin/env python3
"""
Test YouTube API with improved rate limiting and retry logic
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to sys.path to import from core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.services.youtube_service import YouTubeService

load_dotenv()

async def test_youtube_with_rate_limiting():
    """Test YouTube service with rate limiting."""
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("ERROR: YOUTUBE_API_KEY not found in environment")
        return
    
    print(f"Testing YouTube service with rate limiting...")
    
    youtube_service = YouTubeService(api_key)
    
    # Test 1: Simple search with rate limiting
    print("\n1. Testing search with rate limiting:")
    try:
        results = await youtube_service.search_videos("music", max_results=5)
        if results:
            print(f"✅ Search successful: Found {len(results)} videos")
            for i, video in enumerate(results[:2]):
                print(f"   {i+1}. {video.get('title', 'Unknown Title')}")
        else:
            print("⚠️  Search returned empty results (likely using fallback)")
    except Exception as e:
        print(f"❌ Search failed: {e}")
    
    # Test 2: Get trending videos
    print("\n2. Testing trending videos:")
    try:
        trending = await youtube_service.get_trending_videos(max_results=5)
        if trending:
            print(f"✅ Trending successful: Found {len(trending)} videos")
            for i, video in enumerate(trending[:2]):
                print(f"   {i+1}. {video.get('title', 'Unknown Title')}")
        else:
            print("⚠️  Trending returned empty results (likely using fallback)")
    except Exception as e:
        print(f"❌ Trending failed: {e}")
    
    # Test 3: Multiple rapid requests to test rate limiting
    print("\n3. Testing multiple rapid requests:")
    try:
        tasks = []
        for i in range(3):
            task = youtube_service.search_videos(f"test query {i}", max_results=2)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"   Request {i+1}: ❌ {result}")
            else:
                success_count += 1
                print(f"   Request {i+1}: ✅ {len(result)} videos")
        
        print(f"Rate limiting test: {success_count}/{len(tasks)} requests successful")
        
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_youtube_with_rate_limiting())