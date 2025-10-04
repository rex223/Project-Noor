"""
Enhanced YouTube Data V3 API service for fetching video data and analyzing user preferences.
Integrates with personality system to provide personalized video recommendations.
"""

import asyncio
import aiohttp
import logging
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode
import random
import time
import json
import hashlib

from core.config import get_config
from core.database.models import PersonalityTrait  # Enum for iteration
from core.cache.redis_client import get_redis
from core.services.youtube_rate_limiter import YouTubeRateLimiter, RateLimitConfig as YouTubeRateLimitConfig


class YouTubeService:
    """
    Enhanced YouTube Data V3 API service for personality-aware video recommendations.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize YouTube service with API key."""
        self.config = get_config()
        self.api_key = api_key or self.config.youtube.api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.logger = logging.getLogger("bondhu.youtube")
        
        # Redis cache client
        self.redis_client = get_redis()
        
        # Cache TTL settings (in seconds)
        self.cache_ttl = {
            'search_results': 3600,  # 1 hour for search results
            'trending_videos': 1800,  # 30 minutes for trending videos
            'video_details': 7200,   # 2 hours for video details
            'recommendations': 1800,  # 30 minutes for full recommendation sets
            'fallback_content': 7200  # 2 hours for fallback content
        }
        
        # Rate limiting properties
        self.last_request_time = 0.0
        self.max_retries = 3
        self.base_retry_delay = 1.0  # Base delay for exponential backoff

        per_minute_limit = getattr(self.config.rate_limits, "youtube_requests_per_minute", 100)
        per_second_env = os.getenv("YOUTUBE_RPS")
        if per_second_env:
            per_second_limit = max(1, int(per_second_env))
        else:
            per_second_limit = max(1, per_minute_limit // 30)  # default to ~1/30th of per-minute limit

        limiter_config = YouTubeRateLimitConfig(
            api_key=self.api_key,
            per_second=per_second_limit,
            per_minute=per_minute_limit,
        )
        self.rate_limiter = YouTubeRateLimiter(config=limiter_config, redis_client=self.redis_client)
        # Local smoothing between requests within this process
        self.min_request_interval = max(0.05, 1.0 / (self.rate_limiter.config.per_second * 1.5))

        # YouTube category mappings (id -> name and reverse)
        self.category_map = {
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
        self.category_name_to_id = {name: id_ for id_, name in self.category_map.items()}
        
        # Genre to personality mappings based on research
        self.genre_personality_map = {
            # Educational content - High Openness, Conscientiousness
            "Education": {
                PersonalityTrait.OPENNESS: 0.85,
                PersonalityTrait.CONSCIENTIOUSNESS: 0.75,
                PersonalityTrait.EXTRAVERSION: 0.45
            },
            "Science & Technology": {
                PersonalityTrait.OPENNESS: 0.80,
                PersonalityTrait.CONSCIENTIOUSNESS: 0.70,
                PersonalityTrait.EXTRAVERSION: 0.35
            },
            "Howto & Style": {
                PersonalityTrait.CONSCIENTIOUSNESS: 0.75,
                PersonalityTrait.OPENNESS: 0.60,
                PersonalityTrait.AGREEABLENESS: 0.55
            },
            
            # Entertainment - High Extraversion
            "Entertainment": {
                PersonalityTrait.EXTRAVERSION: 0.70,
                PersonalityTrait.AGREEABLENESS: 0.50,
                PersonalityTrait.NEUROTICISM: -0.20
            },
            "Comedy": {
                PersonalityTrait.EXTRAVERSION: 0.75,
                PersonalityTrait.OPENNESS: 0.60,
                PersonalityTrait.AGREEABLENESS: 0.55
            },
            "Film & Animation": {
                PersonalityTrait.OPENNESS: 0.70,
                PersonalityTrait.EXTRAVERSION: 0.45,
                PersonalityTrait.AGREEABLENESS: 0.50
            },
            
            # Music & Arts - High Openness
            "Music": {
                PersonalityTrait.OPENNESS: 0.75,
                PersonalityTrait.EXTRAVERSION: 0.55,
                PersonalityTrait.AGREEABLENESS: 0.50
            },
            "Arts": {
                PersonalityTrait.OPENNESS: 0.85,
                PersonalityTrait.CONSCIENTIOUSNESS: 0.40,
                PersonalityTrait.AGREEABLENESS: 0.60
            },
            
            # Sports & Gaming - Mixed profiles
            "Sports": {
                PersonalityTrait.EXTRAVERSION: 0.65,
                PersonalityTrait.CONSCIENTIOUSNESS: 0.60,
                PersonalityTrait.AGREEABLENESS: 0.45
            },
            "Gaming": {
                PersonalityTrait.OPENNESS: 0.55,
                PersonalityTrait.EXTRAVERSION: 0.50,
                PersonalityTrait.CONSCIENTIOUSNESS: 0.45
            },
            
            # News & Politics - High Conscientiousness, variable Openness
            "News & Politics": {
                PersonalityTrait.CONSCIENTIOUSNESS: 0.70,
                PersonalityTrait.OPENNESS: 0.65,
                PersonalityTrait.NEUROTICISM: 0.45
            },
            
            # Lifestyle & Vlogs - High Agreeableness
            "People & Blogs": {
                PersonalityTrait.AGREEABLENESS: 0.70,
                PersonalityTrait.EXTRAVERSION: 0.60,
                PersonalityTrait.OPENNESS: 0.50
            },
            "Travel & Events": {
                PersonalityTrait.OPENNESS: 0.80,
                PersonalityTrait.EXTRAVERSION: 0.70,
                PersonalityTrait.AGREEABLENESS: 0.55
            },
            "Pets & Animals": {
                PersonalityTrait.AGREEABLENESS: 0.80,
                PersonalityTrait.OPENNESS: 0.50,
                PersonalityTrait.NEUROTICISM: -0.30
            },
            
            # Nonprofits & Activism - High Agreeableness, Conscientiousness
            "Nonprofits & Activism": {
                PersonalityTrait.AGREEABLENESS: 0.85,
                PersonalityTrait.CONSCIENTIOUSNESS: 0.75,
                PersonalityTrait.OPENNESS: 0.65
            }
        }
        
        # Content themes for deeper personality analysis
        self.content_themes = {
            "mindfulness": {
                PersonalityTrait.AGREEABLENESS: 0.70,
                PersonalityTrait.NEUROTICISM: -0.60,
                PersonalityTrait.CONSCIENTIOUSNESS: 0.55
            },
            "productivity": {
                PersonalityTrait.CONSCIENTIOUSNESS: 0.85,
                PersonalityTrait.NEUROTICISM: -0.40,
                PersonalityTrait.OPENNESS: 0.50
            },
            "creativity": {
                PersonalityTrait.OPENNESS: 0.90,
                PersonalityTrait.EXTRAVERSION: 0.45,
                PersonalityTrait.AGREEABLENESS: 0.40
            },
            "social_interaction": {
                PersonalityTrait.EXTRAVERSION: 0.80,
                PersonalityTrait.AGREEABLENESS: 0.70,
                PersonalityTrait.NEUROTICISM: -0.20
            },
            "self_improvement": {
                PersonalityTrait.CONSCIENTIOUSNESS: 0.75,
                PersonalityTrait.OPENNESS: 0.65,
                PersonalityTrait.NEUROTICISM: -0.30
            }
        }

    async def _rate_limited_request(self, session: aiohttp.ClientSession, url: str, params: Dict[str, Any] = None) -> aiohttp.ClientResponse:
        """Make a rate-limited request to YouTube API with exponential backoff retry."""
        await self.rate_limiter.acquire()

        # Local smoothing to avoid burst from this process even with shared limiter
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)

        self.last_request_time = time.time()

        for attempt in range(self.max_retries):
            try:
                response = await session.get(url, params=params)
                
                # If successful or non-retryable error, return
                if response.status == 200:
                    return response
                elif response.status == 403:
                    error_data = await response.json()
                    error_reason = error_data.get('error', {}).get('errors', [{}])[0].get('reason', '')
                    
                    if error_reason in ['quotaExceeded', 'rateLimitExceeded', 'userRateLimitExceeded']:
                        if attempt < self.max_retries - 1:
                            # Calculate exponential backoff delay
                            delay = self.base_retry_delay * (2 ** attempt) + random.uniform(0, 1)
                            self.logger.warning(f"Rate limit hit (reason: {error_reason}), retrying in {delay:.2f}s (attempt {attempt + 1}/{self.max_retries})")
                            await asyncio.sleep(delay)
                            continue
                    
                    # Non-retryable 403 error or max retries reached
                    return response
                else:
                    # Other HTTP errors
                    return response
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.base_retry_delay * (2 ** attempt)
                    self.logger.warning(f"Request failed with {e}, retrying in {delay:.2f}s (attempt {attempt + 1}/{self.max_retries})")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise
        
        # This shouldn't be reached, but just in case
        return response

    def _generate_cache_key(self, prefix: str, *args) -> str:
        """Generate a consistent cache key from prefix and arguments."""
        # Create a hash of all arguments for consistent key generation
        key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get data from Redis cache."""
        try:
            if self.redis_client:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data.decode('utf-8') if isinstance(cached_data, bytes) else cached_data)
        except Exception as e:
            self.logger.warning(f"Cache get error for key {cache_key}: {e}")
        return None

    def _set_cached_data(self, cache_key: str, data: Dict[str, Any], ttl: int) -> None:
        """Set data in Redis cache with TTL."""
        try:
            if self.redis_client:
                self.redis_client.setex(cache_key, ttl, json.dumps(data))
        except Exception as e:
            self.logger.warning(f"Cache set error for key {cache_key}: {e}")

    def _get_cached_videos_with_shuffle(self, cache_key: str, requested_count: int) -> Optional[List[Dict[str, Any]]]:
        """Get cached videos and return a shuffled subset."""
        cached_data = self._get_cached_data(cache_key)
        if cached_data and 'videos' in cached_data:
            videos = cached_data['videos']
            if len(videos) >= requested_count:
                # Return a random sample to provide variety on each refresh
                return random.sample(videos, min(requested_count, len(videos)))
        return None

    async def get_trending_videos(self, region_code: str = "US", max_results: int = 50) -> List[Dict[str, Any]]:
        """Fetch trending videos from YouTube with intelligent caching."""
        cache_key = self._generate_cache_key("trending", region_code)
        
        # Try to get from cache first
        cached_videos = self._get_cached_videos_with_shuffle(cache_key, max_results)
        if cached_videos:
            self.logger.info(f"Returning {len(cached_videos)} trending videos from cache")
            return cached_videos
        
        try:
            params = {
                'part': 'snippet,statistics,contentDetails',
                'chart': 'mostPopular',
                'regionCode': region_code,
                'maxResults': min(50, max_results * 2),  # Get more videos to cache for variety
                'key': self.api_key
            }
            
            url = f"{self.base_url}/videos"
            
            async with aiohttp.ClientSession() as session:
                response = await self._rate_limited_request(session, url, params)
                
                if response.status == 200:
                    data = await response.json()
                    videos = await self._process_video_data(data.get('items', []))
                    
                    # Cache the full set of videos
                    self._set_cached_data(cache_key, {'videos': videos}, self.cache_ttl['trending_videos'])
                    
                    # Return a random subset
                    return random.sample(videos, min(max_results, len(videos)))
                elif response.status == 403:
                    error_data = await response.json()
                    error_reason = error_data.get('error', {}).get('errors', [{}])[0].get('reason', '')
                    
                    if error_reason in ['quotaExceeded', 'rateLimitExceeded', 'userRateLimitExceeded']:
                        self.logger.warning(f"YouTube API limit exceeded ({error_reason}) - using fallback content")
                        return await self._get_fallback_trending_videos()
                    else:
                        self.logger.error(f"YouTube API 403 error: {error_data}")
                        return await self._get_fallback_trending_videos()
                else:
                    self.logger.error(f"YouTube API error: {response.status}")
                    return await self._get_fallback_trending_videos()
                        
        except Exception as e:
            self.logger.error(f"Error fetching trending videos: {e}")
            return await self._get_fallback_trending_videos()

    async def search_videos(self, query: str, max_results: int = 25, category_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for videos based on query and optional category with intelligent caching."""
        cache_key = self._generate_cache_key("search", query, category_id or "none")
        
        # Try to get from cache first
        cached_videos = self._get_cached_videos_with_shuffle(cache_key, max_results)
        if cached_videos:
            self.logger.info(f"Returning {len(cached_videos)} search results from cache for query: {query}")
            return cached_videos
        
        try:
            params = {
                'part': 'snippet',
                'type': 'video',
                'q': query,
                'maxResults': min(50, max_results * 2),  # Get more videos to cache for variety
                'order': 'relevance',
                'key': self.api_key
            }
            
            if category_id:
                params['videoCategoryId'] = category_id
            
            url = f"{self.base_url}/search"
            
            async with aiohttp.ClientSession() as session:
                response = await self._rate_limited_request(session, url, params)
                
                if response.status == 200:
                    data = await response.json()
                    video_ids = [item['id']['videoId'] for item in data.get('items', [])]
                    
                    # Get detailed video information
                    videos = await self.get_video_details(video_ids)
                    
                    # Cache the full set of videos
                    self._set_cached_data(cache_key, {'videos': videos}, self.cache_ttl['search_results'])
                    
                    # Return a random subset
                    return random.sample(videos, min(max_results, len(videos)))
                elif response.status == 403:
                    error_data = await response.json()
                    error_reason = error_data.get('error', {}).get('errors', [{}])[0].get('reason', '')
                    
                    if error_reason in ['quotaExceeded', 'rateLimitExceeded', 'userRateLimitExceeded']:
                        self.logger.warning(f"YouTube API limit exceeded ({error_reason}) for search query: {query}")
                        return await self._get_fallback_search_results(query, max_results)
                    else:
                        self.logger.error(f"YouTube search API 403 error: {error_data}")
                        return await self._get_fallback_search_results(query, max_results)
                else:
                    self.logger.error(f"YouTube search API error: {response.status}")
                    return await self._get_fallback_search_results(query, max_results)
                        
        except Exception as e:
            self.logger.error(f"Error searching videos: {e}")
            return await self._get_fallback_search_results(query, max_results)

    async def get_video_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """Get detailed information for specific videos."""
        try:
            if not video_ids:
                return []
                
            params = {
                'part': 'snippet,statistics,contentDetails',
                'id': ','.join(video_ids),
                'key': self.api_key
            }
            
            url = f"{self.base_url}/videos"
            
            async with aiohttp.ClientSession() as session:
                response = await self._rate_limited_request(session, url, params)
                
                if response.status == 200:
                    data = await response.json()
                    return await self._process_video_data(data.get('items', []))
                elif response.status == 403:
                    error_data = await response.json()
                    error_reason = error_data.get('error', {}).get('errors', [{}])[0].get('reason', '')
                    
                    if error_reason in ['quotaExceeded', 'rateLimitExceeded', 'userRateLimitExceeded']:
                        self.logger.warning(f"YouTube API limit exceeded ({error_reason}) for video details")
                        return await self._get_fallback_video_details(video_ids)
                    else:
                        self.logger.error(f"YouTube video details API 403 error: {error_data}")
                        return await self._get_fallback_video_details(video_ids)
                else:
                    self.logger.error(f"YouTube video details API error: {response.status}")
                    return await self._get_fallback_video_details(video_ids)
                        
        except Exception as e:
            self.logger.error(f"Error fetching video details: {e}")
            return await self._get_fallback_video_details(video_ids) if video_ids else []

    async def get_video_categories(self, region_code: str = "US") -> Dict[str, str]:
        """Get available video categories."""
        try:
            params = {
                'part': 'snippet',
                'regionCode': region_code,
                'key': self.api_key
            }
            
            url = f"{self.base_url}/videoCategories?" + urlencode(params)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        categories = {}
                        for item in data.get('items', []):
                            categories[item['id']] = item['snippet']['title']
                        return categories
                    else:
                        self.logger.error(f"YouTube categories API error: {response.status}")
                        return {}
                        
        except Exception as e:
            self.logger.error(f"Error fetching video categories: {e}")
            return {}

    async def get_personalized_recommendations(self, personality_profile: Dict[PersonalityTrait, float], 
                                              user_history: List[Dict[str, Any]], 
                                              max_results: int = 20) -> List[Dict[str, Any]]:
        """Get personalized video recommendations based on personality and history."""
        try:
            # Analyze user's personality preferences
            preferred_categories = self._get_preferred_categories(personality_profile)
            
            # Generate search queries based on personality
            search_queries = self._generate_personality_queries(personality_profile)
            
            recommendations = []
            
            # Search for videos in preferred categories
            for category, score in preferred_categories:
                if score > 0.3:  # Only include categories with decent match
                    query_results = await self.search_videos(
                        query=category.lower().replace('&', '').replace(' ', '+'),
                        max_results=max(5, int(max_results * score / 2))
                    )
                    recommendations.extend(query_results)
            
            # Search for personality-based content
            for query in search_queries[:3]:  # Limit to top 3 queries
                query_results = await self.search_videos(query, max_results=5)
                recommendations.extend(query_results)
            
            # Remove duplicates and score videos
            unique_videos = {video['id']: video for video in recommendations}
            scored_videos = []
            
            for video in unique_videos.values():
                score = self._calculate_video_score(video, personality_profile, user_history)
                video['personality_score'] = score
                scored_videos.append(video)
            
            # Sort by personality score and return top results
            scored_videos.sort(key=lambda x: x['personality_score'], reverse=True)
            return scored_videos[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error generating personalized recommendations: {e}")
            return []

    async def get_genre_recommendations(self,
                                        genre_name: str,
                                        personality_profile: Dict[PersonalityTrait, float],
                                        user_history: List[Dict[str, Any]],
                                        max_results: int = 6) -> List[Dict[str, Any]]:
        """Fetch and score videos for a specific genre."""
        try:
            category_id = self.category_name_to_id.get(genre_name)
            search_query = genre_name.lower().replace(" & ", " ")

            # Fetch more results to filter down after scoring
            raw_results = await self.search_videos(
                query=search_query,
                max_results=max_results * 2,
                category_id=category_id
            )

            if not raw_results:
                return []

            unique_videos = {video['id']: video for video in raw_results}
            scored_videos: List[Dict[str, Any]] = []

            for video in unique_videos.values():
                score = self._calculate_video_score(video, personality_profile, user_history)
                video['personality_score'] = score
                scored_videos.append(video)

            scored_videos.sort(key=lambda x: x.get('personality_score', 0.0), reverse=True)

            # Add randomization to genre recommendations for variety
            if len(scored_videos) > max_results:
                # Take top 70% by score, then add some random variety
                top_70_percent = int(len(scored_videos) * 0.7)
                top_videos = scored_videos[:top_70_percent]
                remaining_videos = scored_videos[top_70_percent:]
                
                random.shuffle(top_videos)
                random.shuffle(remaining_videos)
                
                final_selection = (top_videos + remaining_videos)[:max_results]
            else:
                random.shuffle(scored_videos)
                final_selection = scored_videos[:max_results]

            return final_selection

        except Exception as e:
            self.logger.error(f"Error fetching genre recommendations for {genre_name}: {e}")
            return []

    async def analyze_user_genres(self, watch_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user's video genre preferences from watch history."""
        try:
            genre_counts = {}
            genre_watch_time = {}
            personality_indicators = {trait: [] for trait in PersonalityTrait}
            
            for video in watch_history:
                category = video.get('category', 'Unknown')
                watch_time = video.get('watch_time', 0)
                
                # Count genre preferences
                genre_counts[category] = genre_counts.get(category, 0) + 1
                genre_watch_time[category] = genre_watch_time.get(category, 0) + watch_time
                
                # Extract personality indicators
                if category in self.genre_personality_map:
                    for trait, score in self.genre_personality_map[category].items():
                        personality_indicators[trait].append(score)
            
            # Calculate genre preferences
            total_videos = len(watch_history)
            genre_preferences = {}
            for genre, count in genre_counts.items():
                preference_score = count / total_videos
                avg_watch_time = genre_watch_time[genre] / count
                genre_preferences[genre] = {
                    'frequency': preference_score,
                    'avg_watch_time': avg_watch_time,
                    'total_videos': count
                }
            
            # Calculate personality insights
            personality_insights = {}
            for trait, scores in personality_indicators.items():
                if scores:
                    personality_insights[trait.value] = {
                        'average_score': sum(scores) / len(scores),
                        'confidence': min(len(scores) / 10, 1.0),  # Higher confidence with more data
                        'evidence_count': len(scores)
                    }
            
            return {
                'genre_preferences': genre_preferences,
                'personality_insights': personality_insights,
                'total_videos_analyzed': total_videos,
                'most_watched_genre': max(genre_counts.items(), key=lambda x: x[1])[0] if genre_counts else None,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing user genres: {e}")
            return {}

    async def _process_video_data(self, video_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process raw YouTube API video data."""
        processed_videos = []
        
        for item in video_items:
            try:
                snippet = item.get('snippet', {})
                statistics = item.get('statistics', {})
                content_details = item.get('contentDetails', {})
                
                # Parse duration
                duration = self._parse_duration(content_details.get('duration', 'PT0S'))
                
                # Determine content themes
                themes = self._extract_content_themes(
                    snippet.get('title', ''),
                    snippet.get('description', ''),
                    snippet.get('tags', [])
                )
                
                processed_video = {
                    'id': item.get('id', ''),
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'channel_title': snippet.get('channelTitle', ''),
                    'channel_id': snippet.get('channelId', ''),
                    'published_at': snippet.get('publishedAt', ''),
                    'category_id': snippet.get('categoryId', ''),
                    'category_name': self._get_category_name(snippet.get('categoryId', '')),
                    'duration_seconds': duration,
                    'duration_formatted': self._format_duration(duration),
                    'view_count': int(statistics.get('viewCount', 0)),
                    'like_count': int(statistics.get('likeCount', 0)),
                    'comment_count': int(statistics.get('commentCount', 0)),
                    'tags': snippet.get('tags', []),
                    'thumbnail_url': snippet.get('thumbnails', {}).get('maxres', {}).get('url', 
                                    snippet.get('thumbnails', {}).get('high', {}).get('url', '')),
                    'youtube_url': f"https://www.youtube.com/watch?v={item.get('id', '')}",
                    'content_themes': themes,
                    'engagement_score': self._calculate_engagement_score(statistics),
                    'personality_indicators': self._extract_personality_indicators(snippet, themes)
                }
                
                processed_videos.append(processed_video)
                
            except Exception as e:
                self.logger.error(f"Error processing video item: {e}")
                continue
        
        return processed_videos

    def _parse_duration(self, duration_str: str) -> int:
        """Parse YouTube duration format (PT1H2M3S) to seconds."""
        import re
        
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds

    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to HH:MM:SS or MM:SS."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"

    def _get_category_name(self, category_id: str) -> str:
        """Get category name from category ID."""
        return self.category_map.get(category_id, 'Unknown')

    def _extract_content_themes(self, title: str, description: str, tags: List[str]) -> List[str]:
        """Extract content themes from video metadata."""
        themes = []
        text = f"{title} {description} {' '.join(tags)}".lower()
        
        theme_keywords = {
            'mindfulness': ['meditation', 'mindfulness', 'breathing', 'calm', 'zen', 'peaceful'],
            'productivity': ['productivity', 'efficiency', 'time management', 'organize', 'focus'],
            'creativity': ['creative', 'art', 'design', 'inspiration', 'imagination'],
            'social_interaction': ['social', 'communication', 'relationships', 'networking'],
            'self_improvement': ['self help', 'personal development', 'growth', 'motivation'],
            'technology': ['tech', 'technology', 'coding', 'programming', 'ai', 'computer'],
            'health': ['health', 'fitness', 'exercise', 'nutrition', 'wellness'],
            'education': ['learn', 'education', 'tutorial', 'course', 'lesson', 'teach']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text for keyword in keywords):
                themes.append(theme)
        
        return themes

    def _calculate_engagement_score(self, statistics: Dict[str, Any]) -> float:
        """Calculate engagement score based on video statistics."""
        try:
            views = int(statistics.get('viewCount', 0))
            likes = int(statistics.get('likeCount', 0))
            comments = int(statistics.get('commentCount', 0))
            
            if views == 0:
                return 0.0
            
            # Calculate engagement rate (likes + comments) / views
            engagement_rate = (likes + comments) / views
            
            # Normalize to 0-1 scale (typical engagement rates are 0.01-0.1)
            normalized_score = min(engagement_rate * 10, 1.0)
            
            return round(normalized_score, 3)
            
        except (ValueError, ZeroDivisionError):
            return 0.0

    def _extract_personality_indicators(self, snippet: Dict[str, Any], themes: List[str]) -> Dict[str, float]:
        """Extract personality indicators from video content."""
        indicators = {}
        
        # Get category-based indicators
        category = self._get_category_name(snippet.get('categoryId', ''))
        if category in self.genre_personality_map:
            for trait, score in self.genre_personality_map[category].items():
                indicators[trait.value] = score
        
        # Get theme-based indicators
        for theme in themes:
            if theme in self.content_themes:
                for trait, score in self.content_themes[theme].items():
                    # Average with existing score if present
                    if trait.value in indicators:
                        indicators[trait.value] = (indicators[trait.value] + score) / 2
                    else:
                        indicators[trait.value] = score
        
        return indicators

    def _get_preferred_categories(self, personality_profile: Dict[PersonalityTrait, float]) -> List[Tuple[str, float]]:
        """Get preferred video categories based on personality profile."""
        category_scores = []
        
        for category, trait_map in self.genre_personality_map.items():
            score = 0.0
            for trait, trait_score in trait_map.items():
                user_trait_score = personality_profile.get(trait, 0.5)
                score += trait_score * user_trait_score
            
            # Normalize score
            score = score / len(trait_map)
            category_scores.append((category, score))
        
        # Sort by score descending
        category_scores.sort(key=lambda x: x[1], reverse=True)
        return category_scores

    def _generate_personality_queries(self, personality_profile: Dict[PersonalityTrait, float]) -> List[str]:
        """Generate search queries based on personality traits."""
        queries = []
        
        # High openness queries
        if personality_profile.get(PersonalityTrait.OPENNESS, 0.5) > 0.6:
            queries.extend([
                "creative art tutorial", "philosophy explained", "science documentary",
                "innovative technology", "abstract concepts"
            ])
        
        # High conscientiousness queries
        if personality_profile.get(PersonalityTrait.CONSCIENTIOUSNESS, 0.5) > 0.6:
            queries.extend([
                "productivity tips", "organization methods", "time management",
                "goal setting", "planning strategies"
            ])
        
        # High extraversion queries
        if personality_profile.get(PersonalityTrait.EXTRAVERSION, 0.5) > 0.6:
            queries.extend([
                "social skills", "public speaking", "networking tips",
                "party games", "group activities"
            ])
        
        # High agreeableness queries
        if personality_profile.get(PersonalityTrait.AGREEABLENESS, 0.5) > 0.6:
            queries.extend([
                "helping others", "volunteering", "community service",
                "empathy building", "conflict resolution"
            ])
        
        # Low neuroticism (emotional stability) queries
        if personality_profile.get(PersonalityTrait.NEUROTICISM, 0.5) < 0.4:
            queries.extend([
                "adventure travel", "extreme sports", "risk taking",
                "challenges", "thrill seeking"
            ])
        # High neuroticism queries
        elif personality_profile.get(PersonalityTrait.NEUROTICISM, 0.5) > 0.6:
            queries.extend([
                "stress management", "anxiety relief", "meditation",
                "calming music", "relaxation techniques"
            ])
        
        return queries

    def _calculate_video_score(self, video: Dict[str, Any], 
                              personality_profile: Dict[PersonalityTrait, float],
                              user_history: List[Dict[str, Any]]) -> float:
        """Calculate personalized score for a video."""
        score = 0.0
        
        # Personality match score (40% of total)
        personality_indicators = video.get('personality_indicators', {})
        personality_match = 0.0
        for trait_str, video_score in personality_indicators.items():
            try:
                trait = PersonalityTrait(trait_str)
                user_score = personality_profile.get(trait, 0.5)
                # Higher score if video trait aligns with user trait
                trait_match = 1 - abs(video_score - user_score)
                personality_match += trait_match
            except ValueError:
                continue
        
        if personality_indicators:
            personality_match = personality_match / len(personality_indicators)
        
        score += personality_match * 0.4
        
        # Engagement score (20% of total)
        engagement = video.get('engagement_score', 0.0)
        score += engagement * 0.2
        
        # Content themes match (20% of total)
        themes = video.get('content_themes', [])
        theme_score = 0.0
        for theme in themes:
            if theme in self.content_themes:
                theme_match = 0.0
                for trait, theme_trait_score in self.content_themes[theme].items():
                    user_trait_score = personality_profile.get(trait, 0.5)
                    theme_match += 1 - abs(theme_trait_score - user_trait_score)
                
                if self.content_themes[theme]:
                    theme_match = theme_match / len(self.content_themes[theme])
                    theme_score += theme_match
        
        if themes:
            theme_score = theme_score / len(themes)
        
        score += theme_score * 0.2
        
        # Diversity bonus (10% of total) - prefer content from categories not heavily watched
        category = video.get('category_name', '')
        user_categories = [h.get('category', '') for h in user_history]
        category_frequency = user_categories.count(category) / len(user_categories) if user_categories else 0
        diversity_bonus = max(0, 1 - category_frequency * 2)  # Bonus for less watched categories
        score += diversity_bonus * 0.1
        
        # Freshness bonus (10% of total) - slight preference for newer content
        try:
            published_date = datetime.fromisoformat(video.get('published_at', '').replace('Z', '+00:00'))
            days_old = (datetime.now(published_date.tzinfo) - published_date).days
            freshness_bonus = max(0, 1 - days_old / 365)  # Bonus decreases over a year
            score += freshness_bonus * 0.1
        except:
            pass
        
        return min(score, 1.0)  # Cap at 1.0

    async def _build_search_query(self, personality_profile: Dict[PersonalityTrait, float], 
                                  user_history: List[Dict[str, Any]], 
                                  num_history_items: int = 5, 
                                  num_personality_items: int = 3) -> Tuple[str, Dict[str, Any]]:
        """Build a robust search query based on personality and history."""
        try:
            query_parts = []
            query_tags = {}
            
            # Boosted keywords based on personality traits
            openness = personality_profile.get(PersonalityTrait.OPENNESS, 0.5)
            conscientiousness = personality_profile.get(PersonalityTrait.CONSCIENTIOUSNESS, 0.5)
            extraversion = personality_profile.get(PersonalityTrait.EXTRAVERSION, 0.5)
            agreeableness = personality_profile.get(PersonalityTrait.AGREEABLENESS, 0.5)
            neuroticism = personality_profile.get(PersonalityTrait.NEUROTICISM, 0.5)
            
            # High openness - creative, artistic, novel experiences
            if openness > 0.6:
                query_parts.append("creative OR artistic OR innovative")
                query_tags['openness_boost'] = True
            
            # High conscientiousness - structured, informative, educational content
            if conscientiousness > 0.6:
                query_parts.append("tutorial OR guide OR tips OR tricks")
                query_tags['conscientiousness_boost'] = True
            
            # High extraversion - social, interactive, entertaining content
            if extraversion > 0.6:
                query_parts.append("social OR networking OR party")
                query_tags['extraversion_boost'] = True
            
            # High agreeableness - helpful, community-oriented content
            if agreeableness > 0.6:
                query_parts.append("helping OR volunteering OR charity")
                query_tags['agreeableness_boost'] = True
            
            # Low neuroticism - adventurous, exciting content
            if neuroticism < 0.4:
                query_parts.append("adventure OR travel OR extreme")
                query_tags['neuroticism_boost'] = True
            # High neuroticism - calming, relaxing content
            elif neuroticism > 0.6:
                query_parts.append("meditation OR relaxation OR calm")
                query_tags['neuroticism_boost'] = True
            
            # Add user history keywords
            if user_history:
                history_keywords = []
                for video in user_history[:num_history_items]:
                    title = video.get('title', '')
                    keywords = title.split()[:3]  # Take first 3 words as keywords
                    history_keywords.extend(keywords)
                
                if history_keywords:
                    query_parts.append(" OR ".join(history_keywords))
                    query_tags['history_boost'] = True
            
            # Add personality-based content themes
            personality_queries = await self._generate_personality_queries(personality_profile)
            if personality_queries:
                query_parts.append(" OR ".join(personality_queries))
                query_tags['personality_themes'] = True
            
            # Combine all parts into a final query
            final_query = " AND ".join(query_parts)
            
            return final_query, query_tags
        
        except Exception as e:
            self.logger.error(f"Error building search query: {e}")
            return "", {}

    async def get_personalized_recommendations(self, personality_profile: Dict[PersonalityTrait, float], 
                                              user_history: List[Dict[str, Any]], 
                                              max_results: int = 20) -> List[Dict[str, Any]]:
        """Get personalized video recommendations based on personality and history with intelligent caching."""
        # Create cache key based on personality and history
        personality_key = hashlib.md5(str(sorted(personality_profile.items())).encode()).hexdigest()[:8]
        history_key = hashlib.md5(str([v.get('id', '') for v in user_history[-10:]]).encode()).hexdigest()[:8]  # Last 10 videos
        cache_key = self._generate_cache_key("recommendations", personality_key, history_key)
        
        # Try to get from cache first and return shuffled subset for variety
        cached_videos = self._get_cached_videos_with_shuffle(cache_key, max_results)
        if cached_videos:
            self.logger.info(f"Returning {len(cached_videos)} personalized recommendations from cache")
            return cached_videos
        
        try:
            recommendations = []
            
            # Part 1: Watch History-Based Recommendations (40% weight)
            if user_history:
                history_recommendations = await self._get_history_based_recommendations(
                    user_history, int(max_results * 0.4)
                )
                recommendations.extend(history_recommendations)
                self.logger.info(f"Added {len(history_recommendations)} history-based recommendations")
            
            # Part 2: Personality-Based Recommendations (40% weight)  
            personality_recommendations = await self._get_personality_based_recommendations(
                personality_profile, int(max_results * 0.4)
            )
            recommendations.extend(personality_recommendations)
            self.logger.info(f"Added {len(personality_recommendations)} personality-based recommendations")
            
            # Part 3: Hybrid recommendations using both history and personality (20% weight)
            if user_history:
                hybrid_recommendations = await self._get_hybrid_recommendations(
                    personality_profile, user_history, int(max_results * 0.2)
                )
                recommendations.extend(hybrid_recommendations)
                self.logger.info(f"Added {len(hybrid_recommendations)} hybrid recommendations")
            
            # If no watch history, give more weight to personality
            if not user_history:
                extra_personality = await self._get_personality_based_recommendations(
                    personality_profile, int(max_results * 0.6)
                )
                recommendations.extend(extra_personality)
                self.logger.info(f"No watch history - added {len(extra_personality)} extra personality recommendations")
            
            # Remove duplicates and score videos
            unique_videos = {video['id']: video for video in recommendations}
            scored_videos = []
            
            for video in unique_videos.values():
                # Enhanced scoring that considers both personality and history
                score = self._calculate_enhanced_video_score(video, personality_profile, user_history)
                video['personality_score'] = score
                scored_videos.append(video)
            
            # Sort by enhanced score and add randomization for variety
            scored_videos.sort(key=lambda x: x['personality_score'], reverse=True)
            
            # Add some randomization to prevent identical results every time
            # Take top 70% by score, then shuffle for variety (more variety than before)
            top_70_percent = int(len(scored_videos) * 0.7) if len(scored_videos) > 5 else len(scored_videos)
            top_videos = scored_videos[:top_70_percent]
            remaining_videos = scored_videos[top_70_percent:]
            
            random.shuffle(top_videos)
            random.shuffle(remaining_videos)
            
            final_results = (top_videos + remaining_videos)[:max_results]
            
            # Add metadata about recommendation sources for debugging
            source_counts = {}
            for video in final_results:
                source = video.get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            self.logger.info(f"Final recommendations by source: {source_counts}")
            
            # If no personalized recommendations found, fallback to popular videos
            if not final_results:
                self.logger.warning("No personalized recommendations found. Falling back to popular videos.")
                fallback_results = await self.get_trending_videos(max_results=max_results)
                return fallback_results
            
            # Cache the larger set of recommendations for future variety
            extended_results = scored_videos[:max_results * 2]  # Cache more for variety
            self._set_cached_data(cache_key, {'videos': extended_results}, self.cache_ttl['recommendations'])
            
            return final_results
            
        except Exception as e:
            self.logger.error(f"Error generating personalized recommendations: {e}")
            # Try to return cached results even if fresh generation failed
            cached_videos = self._get_cached_videos_with_shuffle(cache_key, max_results)
            if cached_videos:
                self.logger.info(f"Returning {len(cached_videos)} cached recommendations after error")
                return cached_videos
            return []

    async def _get_fallback_trending_videos(self) -> List[Dict[str, Any]]:
        """Provide fallback trending videos when YouTube API quota is exceeded."""
        # Static fallback data with popular video categories
        fallback_videos = [
            {
                'id': f'fallback_trending_{i}',
                'title': f'Popular {category} Content - API Quota Exceeded',
                'description': f'Trending {category.lower()} content. YouTube API quota exceeded, showing fallback recommendations.',
                'channel_title': 'Bondhu AI Recommendations',
                'thumbnail_url': 'https://via.placeholder.com/320x180?text=Video+Unavailable',
                'youtube_url': f'https://youtube.com/watch?v=fallback_{i}',
                'category_name': category,
                'view_count': random.randint(100000, 1000000),
                'like_count': random.randint(1000, 10000),
                'duration_formatted': f'{random.randint(2, 15)}:00',
                'duration_seconds': random.randint(120, 900),
                'content_themes': [category.lower(), 'trending'],
                'personality_score': random.uniform(0.6, 0.9)
            }
            for i, category in enumerate(['Music', 'Entertainment', 'Gaming', 'Education', 'Comedy', 'Technology'], 1)
        ]
        
        random.shuffle(fallback_videos)
        return fallback_videos

    async def _get_fallback_search_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Provide fallback search results when YouTube API quota is exceeded."""
        # Generate fallback results based on the search query
        search_terms = query.lower().split()
        main_term = search_terms[0] if search_terms else 'content'
        
        fallback_videos = [
            {
                'id': f'fallback_search_{query}_{i}',
                'title': f'{main_term.title()} Video {i} - API Quota Exceeded',
                'description': f'Content related to "{query}". YouTube API quota exceeded, showing fallback recommendations.',
                'channel_title': 'Bondhu AI Search',
                'thumbnail_url': 'https://via.placeholder.com/320x180?text=Search+Unavailable',
                'youtube_url': f'https://youtube.com/watch?v=search_{query}_{i}',
                'category_name': main_term.title(),
                'view_count': random.randint(50000, 500000),
                'like_count': random.randint(500, 5000),
                'duration_formatted': f'{random.randint(3, 20)}:00',
                'duration_seconds': random.randint(180, 1200),
                'content_themes': search_terms + ['search_result'],
                'personality_score': random.uniform(0.5, 0.8)
            }
            for i in range(1, min(max_results + 1, 11))  # Cap at 10 fallback results
        ]
        
        return fallback_videos

    async def _get_fallback_video_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """Provide fallback video details when YouTube API quota is exceeded."""
        fallback_videos = []
        
        for i, video_id in enumerate(video_ids[:10]):  # Limit to 10 videos
            fallback_video = {
                'id': video_id,
                'title': f'Video {i+1} - API Quota Exceeded',
                'description': 'Video details unavailable due to YouTube API quota limits. Please try again later.',
                'channel_title': 'Unknown Channel',
                'thumbnail_url': 'https://via.placeholder.com/320x180?text=Quota+Exceeded',
                'youtube_url': f'https://youtube.com/watch?v={video_id}',
                'category_name': 'Entertainment',
                'view_count': random.randint(10000, 100000),
                'like_count': random.randint(100, 1000),
                'duration_formatted': f'{random.randint(2, 10)}:00',
                'duration_seconds': random.randint(120, 600),
                'content_themes': ['quota_exceeded'],
                'personality_score': random.uniform(0.4, 0.7)
            }
            fallback_videos.append(fallback_video)
        
        return fallback_videos

    async def _get_history_based_recommendations(self, user_history: List[Dict[str, Any]], max_results: int) -> List[Dict[str, Any]]:
        """Get recommendations based on user's watch history patterns."""
        if not user_history:
            return []
        
        try:
            # Analyze watch history to extract patterns
            category_preferences = {}
            channel_preferences = {}
            keyword_frequency = {}
            
            for video in user_history:
                # Track category preferences
                category = video.get('category_name', 'Unknown')
                watch_time = video.get('watch_time', 0)
                completion_rate = video.get('completion_rate', 0.0)
                
                # Weight by engagement (watch time * completion rate)
                engagement_score = watch_time * (completion_rate + 0.1)  # Add small base to avoid zero
                
                category_preferences[category] = category_preferences.get(category, 0) + engagement_score
                
                # Track channel preferences
                channel = video.get('channel_title', '')
                if channel:
                    channel_preferences[channel] = channel_preferences.get(channel, 0) + engagement_score
                
                # Extract keywords from video titles
                title = video.get('video_title', '')
                if title:
                    # Simple keyword extraction
                    words = title.lower().split()
                    for word in words:
                        if len(word) > 3:  # Skip short words
                            keyword_frequency[word] = keyword_frequency.get(word, 0) + engagement_score
            
            # Get top categories and keywords
            top_categories = sorted(category_preferences.items(), key=lambda x: x[1], reverse=True)[:3]
            top_keywords = sorted(keyword_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
            
            recommendations = []
            
            # Search based on top categories
            for category, score in top_categories:
                if category != 'Unknown':
                    query_results = await self.search_videos(
                        query=category.lower().replace(' & ', ' '),
                        max_results=max(2, max_results // len(top_categories))
                    )
                    # Tag these as history-based
                    for video in query_results:
                        video['source'] = 'watch_history'
                        video['history_category'] = category
                    recommendations.extend(query_results)
            
            # Search based on top keywords
            if top_keywords:
                keyword_query = ' OR '.join([kw[0] for kw in top_keywords[:3]])
                keyword_results = await self.search_videos(
                    query=keyword_query,
                    max_results=max(2, max_results // 3)
                )
                # Tag these as keyword-based
                for video in keyword_results:
                    video['source'] = 'watch_history_keywords'
                recommendations.extend(keyword_results)
            
            return recommendations[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error generating history-based recommendations: {e}")
            return []

    async def _get_personality_based_recommendations(self, personality_profile: Dict[PersonalityTrait, float], max_results: int) -> List[Dict[str, Any]]:
        """Get recommendations based purely on personality profile."""
        try:
            # Analyze user's personality preferences
            preferred_categories = self._get_preferred_categories(personality_profile)
            
            # Generate search queries based on personality
            search_queries = self._generate_personality_queries(personality_profile)
            
            recommendations = []
            
            # Search for videos in preferred categories
            for category, score in preferred_categories[:3]:  # Top 3 categories
                if score > 0.3:  # Only include categories with decent match
                    query_results = await self.search_videos(
                        query=category.lower().replace('&', '').replace(' ', '+'),
                        max_results=max(2, int(max_results * score / 2))
                    )
                    # Tag these as personality-based
                    for video in query_results:
                        video['source'] = 'personality'
                        video['personality_category'] = category
                    recommendations.extend(query_results)
            
            # Search for personality-based content themes
            for query in search_queries[:2]:  # Limit to top 2 queries
                query_results = await self.search_videos(query, max_results=max(1, max_results // 4))
                # Tag these as personality themes
                for video in query_results:
                    video['source'] = 'personality_theme'
                recommendations.extend(query_results)
            
            return recommendations[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error generating personality-based recommendations: {e}")
            return []

    async def _get_hybrid_recommendations(self, personality_profile: Dict[PersonalityTrait, float], 
                                         user_history: List[Dict[str, Any]], max_results: int) -> List[Dict[str, Any]]:
        """Get recommendations that combine both personality and watch history insights."""
        try:
            if not user_history:
                return []
            
            # Analyze watch history to understand user's actual vs predicted preferences
            history_categories = {}
            for video in user_history:
                category = video.get('category_name', '')
                completion_rate = video.get('completion_rate', 0.0)
                if category and completion_rate > 0.5:  # Only well-watched videos
                    history_categories[category] = history_categories.get(category, 0) + 1
            
            # Get personality-predicted categories
            personality_categories = dict(self._get_preferred_categories(personality_profile))
            
            # Find intersection - categories both predicted and actually watched
            hybrid_categories = []
            for category in history_categories:
                if category in personality_categories:
                    # Boost score for categories that match both
                    combined_score = personality_categories[category] * (1 + history_categories[category] * 0.1)
                    hybrid_categories.append((category, combined_score))
            
            # Sort by combined score
            hybrid_categories.sort(key=lambda x: x[1], reverse=True)
            
            recommendations = []
            
            # Search for hybrid recommendations
            for category, score in hybrid_categories[:2]:  # Top 2 hybrid categories
                query_results = await self.search_videos(
                    query=f"{category} tutorial OR {category} guide OR {category} tips",
                    max_results=max(1, max_results // 2)
                )
                # Tag these as hybrid recommendations
                for video in query_results:
                    video['source'] = 'hybrid'
                    video['hybrid_category'] = category
                    video['hybrid_score'] = score
                recommendations.extend(query_results)
            
            return recommendations[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error generating hybrid recommendations: {e}")
            return []

    def _calculate_enhanced_video_score(self, video: Dict[str, Any], 
                                       personality_profile: Dict[PersonalityTrait, float], 
                                       user_history: List[Dict[str, Any]]) -> float:
        """Enhanced video scoring that considers both personality and watch history."""
        base_score = self._calculate_video_score(video, personality_profile, user_history)
        
        # Bonus points based on recommendation source
        source_bonus = 0.0
        source = video.get('source', '')
        
        if source == 'watch_history':
            source_bonus = 0.3  # Strong bonus for history-based recommendations
        elif source == 'hybrid':
            source_bonus = 0.4  # Highest bonus for hybrid recommendations
        elif source == 'watch_history_keywords':
            source_bonus = 0.2  # Medium bonus for keyword-based
        elif source == 'personality':
            source_bonus = 0.1  # Small bonus for pure personality
        
        # Additional bonus if video category matches user's historical preferences
        if user_history:
            watched_categories = [v.get('category_name', '') for v in user_history]
            video_category = video.get('category_name', '')
            
            if video_category in watched_categories:
                category_frequency = watched_categories.count(video_category) / len(watched_categories)
                source_bonus += category_frequency * 0.2  # Up to 0.2 bonus for frequently watched categories
        
        final_score = min(base_score + source_bonus, 1.0)
        return final_score