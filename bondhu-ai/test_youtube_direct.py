#!/usr/bin/env python3
"""
Minimal YouTube API test - no complex imports.
"""

import asyncio
import os
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_youtube_api_direct():
    """Test YouTube API directly without complex imports."""
    
    print("🔍 Testing YouTube Data API (Direct)...")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ YOUTUBE_API_KEY not found in .env file")
        return False
        
    print(f"✅ YouTube API Key found: {api_key[:15]}...")
    
    # Test trending videos endpoint
    try:
        url = f"https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'snippet,statistics',
            'chart': 'mostPopular',
            'regionCode': 'US',
            'maxResults': 5,
            'key': api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    videos = data.get('items', [])
                    
                    print(f"✅ Successfully fetched {len(videos)} trending videos:")
                    for i, video in enumerate(videos, 1):
                        title = video['snippet']['title'][:50]
                        category_id = video['snippet'].get('categoryId', 'Unknown')
                        view_count = video['statistics'].get('viewCount', 'N/A')
                        print(f"   {i}. {title}...")
                        print(f"      Category ID: {category_id}, Views: {view_count}")
                    
                    # Test genre analysis
                    print(f"\n📊 Genre Analysis:")
                    categories = {}
                    for video in videos:
                        cat_id = video['snippet'].get('categoryId', 'Unknown')
                        categories[cat_id] = categories.get(cat_id, 0) + 1
                    
                    for cat_id, count in categories.items():
                        print(f"   Category {cat_id}: {count} videos")
                    
                    print(f"\n✅ YouTube API integration is WORKING!")
                    print(f"✅ Video data includes: titles, categories, view counts")
                    print(f"✅ Ready for personality-based recommendations!")
                    
                    return True
                    
                else:
                    error_data = await response.json()
                    print(f"❌ API Error {response.status}: {error_data}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error testing YouTube API: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_youtube_api_direct())