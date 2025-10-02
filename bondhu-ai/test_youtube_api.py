#!/usr/bin/env python3
"""
Simple test script to debug video recommendations without full system imports
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test_youtube_api():
    """Test YouTube API directly."""
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("ERROR: YOUTUBE_API_KEY not found in environment")
        return
    
    print(f"Testing YouTube API with key: {api_key[:10]}...")
    
    # Test simple search
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q=music&maxResults=5&key={api_key}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(f"Response status: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                videos = data.get('items', [])
                print(f"Found {len(videos)} videos:")
                
                for i, video in enumerate(videos[:3]):
                    title = video.get('snippet', {}).get('title', 'Unknown')
                    print(f"  {i+1}. {title}")
                    
            else:
                error_text = await response.text()
                print(f"ERROR: {error_text}")

if __name__ == "__main__":
    asyncio.run(test_youtube_api())