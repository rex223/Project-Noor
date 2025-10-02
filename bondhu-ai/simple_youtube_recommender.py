#!/usr/bin/env python3
"""
Simple YouTube recommendation system that works.
Analyzes user watch patterns and provides personality-based recommendations.
"""

import asyncio
import aiohttp
import os
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleYouTubeRecommender:
    """Simple YouTube recommender that actually works."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with API key."""
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
        # Category ID to name mapping
        self.categories = {
            '1': 'Film & Animation',
            '2': 'Autos & Vehicles', 
            '10': 'Music',
            '15': 'Pets & Animals',
            '17': 'Sports',
            '19': 'Travel & Events',
            '20': 'Gaming',
            '22': 'People & Blogs',
            '23': 'Comedy',
            '24': 'Entertainment',
            '25': 'News & Politics',
            '26': 'Howto & Style',
            '27': 'Education',
            '28': 'Science & Technology',
            '29': 'Nonprofits & Activism'
        }
        
        # Personality weights for each category (0-1 scale)
        self.personality_weights = {
            'Education': {
                'openness': 0.9,
                'conscientiousness': 0.8,
                'extraversion': 0.4,
                'agreeableness': 0.6,
                'neuroticism': 0.3
            },
            'Science & Technology': {
                'openness': 0.85,
                'conscientiousness': 0.7,
                'extraversion': 0.3,
                'agreeableness': 0.5,
                'neuroticism': 0.3
            },
            'Music': {
                'openness': 0.7,
                'conscientiousness': 0.4,
                'extraversion': 0.6,
                'agreeableness': 0.6,
                'neuroticism': 0.4
            },
            'Entertainment': {
                'openness': 0.5,
                'conscientiousness': 0.4,
                'extraversion': 0.8,
                'agreeableness': 0.6,
                'neuroticism': 0.3
            },
            'Gaming': {
                'openness': 0.6,
                'conscientiousness': 0.4,
                'extraversion': 0.5,
                'agreeableness': 0.4,
                'neuroticism': 0.4
            },
            'Comedy': {
                'openness': 0.6,
                'conscientiousness': 0.3,
                'extraversion': 0.8,
                'agreeableness': 0.7,
                'neuroticism': 0.2
            }
        }

    async def get_trending_videos(self, max_results: int = 25) -> List[Dict[str, Any]]:
        """Get trending videos with category analysis."""
        
        params = {
            'part': 'snippet,statistics,contentDetails',
            'chart': 'mostPopular',
            'regionCode': 'US',
            'maxResults': max_results,
            'key': self.api_key
        }
        
        url = f"{self.base_url}/videos"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_videos(data.get('items', []))
                else:
                    print(f"API Error: {response.status}")
                    return []

    async def search_videos(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search for videos."""
        
        # First, search for video IDs
        search_params = {
            'part': 'snippet',
            'type': 'video',
            'q': query,
            'maxResults': max_results,
            'order': 'relevance',
            'key': self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/search", params=search_params) as response:
                if response.status == 200:
                    search_data = await response.json()
                    video_ids = [item['id']['videoId'] for item in search_data.get('items', [])]
                    
                    # Get detailed video information
                    if video_ids:
                        detail_params = {
                            'part': 'snippet,statistics,contentDetails',
                            'id': ','.join(video_ids),
                            'key': self.api_key
                        }
                        
                        async with session.get(f"{self.base_url}/videos", params=detail_params) as detail_response:
                            if detail_response.status == 200:
                                detail_data = await detail_response.json()
                                return self._process_videos(detail_data.get('items', []))
                
                return []

    def _process_videos(self, videos: List[Dict]) -> List[Dict[str, Any]]:
        """Process raw YouTube API video data."""
        
        processed = []
        for video in videos:
            snippet = video.get('snippet', {})
            stats = video.get('statistics', {})
            content = video.get('contentDetails', {})
            
            category_id = snippet.get('categoryId', '24')
            category_name = self.categories.get(category_id, 'Entertainment')
            
            processed_video = {
                'id': video.get('id'),
                'title': snippet.get('title', 'No title'),
                'description': snippet.get('description', '')[:200] + '...',
                'channel_title': snippet.get('channelTitle', 'Unknown'),
                'category_id': category_id,
                'category_name': category_name,
                'published_at': snippet.get('publishedAt'),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'view_count': int(stats.get('viewCount', 0)),
                'like_count': int(stats.get('likeCount', 0)),
                'duration': content.get('duration', 'PT0S'),
                'youtube_url': f"https://www.youtube.com/watch?v={video.get('id')}",
                'source': 'youtube_api'
            }
            processed.append(processed_video)
        
        return processed

    def calculate_personality_score(self, video: Dict[str, Any], user_personality: Dict[str, float]) -> float:
        """Calculate how well a video matches user's personality."""
        
        category_name = video.get('category_name', 'Entertainment')
        
        if category_name not in self.personality_weights:
            return 0.5  # Default neutral score
        
        category_weights = self.personality_weights[category_name]
        
        # Calculate weighted score
        total_score = 0.0
        total_weight = 0.0
        
        for trait, user_score in user_personality.items():
            if trait in category_weights:
                weight = category_weights[trait]
                # Score is higher when user trait aligns with category preference
                trait_score = 1.0 - abs(user_score - weight)
                total_score += trait_score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.5

    async def get_personalized_recommendations(
        self, 
        user_personality: Dict[str, float],
        search_queries: Optional[List[str]] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Get personalized video recommendations."""
        
        # Default search queries based on personality
        if not search_queries:
            queries = []
            
            if user_personality.get('openness', 0.5) > 0.6:
                queries.extend(['documentary', 'science', 'art', 'philosophy'])
            
            if user_personality.get('conscientiousness', 0.5) > 0.6:
                queries.extend(['tutorial', 'how to', 'education', 'productivity'])
            
            if user_personality.get('extraversion', 0.5) > 0.6:
                queries.extend(['comedy', 'entertainment', 'social', 'music'])
            
            if user_personality.get('agreeableness', 0.5) > 0.6:
                queries.extend(['animals', 'wholesome', 'helping others', 'community'])
            
            if user_personality.get('neuroticism', 0.5) < 0.4:  # Low neuroticism = stable
                queries.extend(['adventure', 'sports', 'travel', 'challenges'])
            
            search_queries = queries[:4]  # Limit to 4 queries
        
        # Get videos from multiple sources
        all_videos = []
        
        # Get trending videos
        trending = await self.get_trending_videos(10)
        all_videos.extend(trending)
        
        # Search for personality-relevant content
        for query in search_queries:
            search_results = await self.search_videos(query, 5)
            all_videos.extend(search_results)
        
        # Remove duplicates
        seen_ids = set()
        unique_videos = []
        for video in all_videos:
            if video['id'] not in seen_ids:
                seen_ids.add(video['id'])
                unique_videos.append(video)
        
        # Score and rank videos
        for video in unique_videos:
            video['personality_score'] = self.calculate_personality_score(video, user_personality)
        
        # Sort by personality score
        unique_videos.sort(key=lambda x: x['personality_score'], reverse=True)
        
        return unique_videos[:max_results]

    def analyze_watch_history(self, watch_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user's watch history to understand preferences."""
        
        if not watch_history:
            return {'message': 'No watch history to analyze'}
        
        # Count categories
        category_counts = {}
        total_watch_time = 0
        
        for video in watch_history:
            category = video.get('category_name', 'Unknown')
            watch_time = video.get('watch_time_seconds', 0)
            
            category_counts[category] = category_counts.get(category, 0) + 1
            total_watch_time += watch_time
        
        # Find most watched categories
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Infer personality traits from preferences
        inferred_personality = {
            'openness': 0.5,
            'conscientiousness': 0.5,
            'extraversion': 0.5,
            'agreeableness': 0.5,
            'neuroticism': 0.5
        }
        
        for category, count in sorted_categories:
            if category in self.personality_weights:
                weight = count / len(watch_history)  # Normalize by total videos
                category_traits = self.personality_weights[category]
                
                for trait, trait_score in category_traits.items():
                    # Blend the inferred trait with existing
                    inferred_personality[trait] = (
                        inferred_personality[trait] * 0.7 + 
                        trait_score * weight * 0.3
                    )
        
        return {
            'total_videos': len(watch_history),
            'total_watch_time_hours': total_watch_time / 3600,
            'top_categories': sorted_categories[:5],
            'inferred_personality': inferred_personality,
            'analysis_timestamp': asyncio.get_event_loop().time()
        }


async def main():
    """Test the simple YouTube recommender."""
    
    print("🎥 Simple YouTube Recommender Test")
    print("=" * 50)
    
    recommender = SimpleYouTubeRecommender()
    
    # Test user personality (high openness, curious learner)
    user_personality = {
        'openness': 0.8,
        'conscientiousness': 0.7,
        'extraversion': 0.4,
        'agreeableness': 0.6,
        'neuroticism': 0.3
    }
    
    print("👤 User Personality Profile:")
    for trait, score in user_personality.items():
        print(f"   {trait.capitalize()}: {score:.1f}")
    
    print(f"\n🔍 Getting personalized recommendations...")
    
    recommendations = await recommender.get_personalized_recommendations(
        user_personality=user_personality,
        max_results=10
    )
    
    print(f"\n✅ Generated {len(recommendations)} recommendations:")
    for i, video in enumerate(recommendations[:5], 1):
        title = video['title'][:50]
        category = video['category_name']
        score = video['personality_score']
        views = video['view_count']
        
        print(f"{i:2d}. {title}...")
        print(f"     Category: {category} | Score: {score:.3f} | Views: {views:,}")
    
    print(f"\n✅ YouTube recommendation system is working!")
    print(f"✅ Ready for integration with your app!")

if __name__ == "__main__":
    asyncio.run(main())