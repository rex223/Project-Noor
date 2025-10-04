"""
Rate-limited YouTube service adapter for centralized API management.

Wraps existing YouTube service with centralized rate limiting, caching,
and quota management for multi-user environment.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from core.services.youtube_service import YouTubeService
from core.services.rate_limiter_service import (
    rate_limiter_service, 
    RateLimitResult, 
    RequestPriority,
    APIQuotaExceeded
)
from core.database.models import PersonalityTrait

logger = logging.getLogger("bondhu.rate_limited.youtube")


class RateLimitedYouTubeService:
    """YouTube service with centralized rate limiting and quota management"""
    
    def __init__(self, user_id: str, user_tier: str = "free"):
        """Initialize rate-limited YouTube service"""
        self.user_id = user_id
        self.user_tier = user_tier
        self.youtube_service = YouTubeService()
        self.rate_limiter = rate_limiter_service
        
        logger.info(f"RateLimitedYouTubeService initialized for user {user_id} (tier: {user_tier})")
    
    async def search_videos(
        self,
        query: str,
        max_results: int = 20,
        priority: RequestPriority = RequestPriority.MEDIUM,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Search for videos with rate limiting and caching"""
        
        request_data = {
            "operation": "search",
            "query": query,
            "max_results": max_results
        }
        
        # Check cache first if not forcing refresh
        if not force_refresh:
            cached_result = await self.rate_limiter.process_cached_request(
                self.user_id, "youtube", "search", request_data
            )
            if cached_result:
                logger.debug(f"Cache hit for YouTube search: {query}")
                return cached_result
        
        # Check quota and consume if available
        result, metadata = await self.rate_limiter.check_and_consume_quota(
            self.user_id, self.user_tier, "youtube", "search", request_data, priority
        )
        
        if result == RateLimitResult.CACHED:
            logger.debug(f"YouTube search served from cache: {query}")
            return metadata["cached_data"]
        
        elif result == RateLimitResult.ALLOWED:
            # Make actual API call
            try:
                start_time = datetime.utcnow()
                
                # Use existing YouTube service
                search_results = await self.youtube_service.search_videos(
                    query=query,
                    max_results=max_results
                )
                
                # Calculate response time
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

                # Track metrics
                await self._track_api_call("search", response_time, True)

                # Normalize result: underlying YouTubeService.search_videos may
                # return a list of video dicts or a dict with 'items'. Ensure we
                # always cache and return a dict with an 'items' key to keep
                # backward-compatible callers working.
                if isinstance(search_results, dict):
                    items = search_results.get('items', [])
                elif isinstance(search_results, list):
                    items = search_results
                else:
                    items = []

                normalized = {'items': items}

                # Cache the normalized response
                await self.rate_limiter.cache_response(
                    self.user_id, "youtube", "search", request_data, normalized
                )

                logger.info(f"YouTube search completed: {query} ({len(items)} results)")
                return normalized
                
            except Exception as e:
                # Track failed call
                await self._track_api_call("search", 0, False)
                logger.error(f"YouTube search failed: {e}")
                raise
        
        elif result == RateLimitResult.QUEUED:
            logger.info(f"YouTube search queued (position: {metadata.get('queue_position', 'unknown')}): {query}")
            raise APIQuotaExceeded(
                "youtube", self.user_id, 
                metadata["quota_usage"], metadata["quota_limit"]
            )
        
        else:
            logger.warning(f"YouTube search denied: {metadata.get('error', 'Unknown error')}")
            raise APIQuotaExceeded(
                "youtube", self.user_id,
                metadata.get("quota_usage", 0), metadata.get("quota_limit", 0)
            )
    
    async def get_video_details(
        self,
        video_ids: List[str],
        priority: RequestPriority = RequestPriority.HIGH
    ) -> Dict[str, Any]:
        """Get video details with rate limiting"""
        
        request_data = {
            "operation": "video_details",
            "video_ids": video_ids
        }
        
        # Check cache first
        cached_result = await self.rate_limiter.process_cached_request(
            self.user_id, "youtube", "video_details", request_data
        )
        if cached_result:
            logger.debug(f"Cache hit for video details: {len(video_ids)} videos")
            return cached_result
        
        # Check quota
        result, metadata = await self.rate_limiter.check_and_consume_quota(
            self.user_id, self.user_tier, "youtube", "video_details", request_data, priority
        )
        
        if result == RateLimitResult.CACHED:
            return metadata["cached_data"]
        
        elif result == RateLimitResult.ALLOWED:
            try:
                start_time = datetime.utcnow()
                
                # Make API call
                video_details = await self.youtube_service.get_video_details(video_ids)
                
                # Track metrics
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                await self._track_api_call("video_details", response_time, True)
                
                # Cache response (longer TTL for video details)
                await self.rate_limiter.cache_response(
                    self.user_id, "youtube", "video_details", request_data, 
                    video_details, custom_ttl=604800  # 7 days
                )
                
                logger.info(f"Video details retrieved: {len(video_ids)} videos")
                return video_details
                
            except Exception as e:
                await self._track_api_call("video_details", 0, False)
                logger.error(f"Video details failed: {e}")
                raise
        
        else:
            logger.warning(f"Video details request denied or queued")
            raise APIQuotaExceeded(
                "youtube", self.user_id,
                metadata.get("quota_usage", 0), metadata.get("quota_limit", 0)
            )
    
    async def get_trending_videos(
        self,
        region_code: str = "US",
        max_results: int = 50,
        priority: RequestPriority = RequestPriority.LOW
    ) -> Dict[str, Any]:
        """Get trending videos with rate limiting"""
        
        request_data = {
            "operation": "trending_videos",
            "region_code": region_code,
            "max_results": max_results
        }
        
        # Check cache (trending videos change frequently, shorter TTL)
        cached_result = await self.rate_limiter.process_cached_request(
            self.user_id, "youtube", "trending_videos", request_data
        )
        if cached_result:
            logger.debug(f"Cache hit for trending videos: {region_code}")
            return cached_result
        
        # Check quota
        result, metadata = await self.rate_limiter.check_and_consume_quota(
            self.user_id, self.user_tier, "youtube", "trending_videos", request_data, priority
        )
        
        if result == RateLimitResult.CACHED:
            return metadata["cached_data"]
        
        elif result == RateLimitResult.ALLOWED:
            try:
                start_time = datetime.utcnow()
                
                # Make API call
                trending_videos = await self.youtube_service.get_trending_videos(
                    region_code=region_code,
                    max_results=max_results
                )
                
                # Track metrics
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                await self._track_api_call("trending_videos", response_time, True)

                # Normalize trend results similar to search results
                if isinstance(trending_videos, dict):
                    items = trending_videos.get('items', [])
                elif isinstance(trending_videos, list):
                    items = trending_videos
                else:
                    items = []

                normalized = {'items': items}

                # Cache with shorter TTL (trending changes frequently)
                await self.rate_limiter.cache_response(
                    self.user_id, "youtube", "trending_videos", request_data, 
                    normalized, custom_ttl=3600  # 1 hour
                )

                logger.info(f"Trending videos retrieved: {region_code} ({len(items)} videos)")
                return normalized
                
            except Exception as e:
                await self._track_api_call("trending_videos", 0, False)
                logger.error(f"Trending videos failed: {e}")
                raise
        
        else:
            logger.warning(f"Trending videos request denied or queued")
            raise APIQuotaExceeded(
                "youtube", self.user_id,
                metadata.get("quota_usage", 0), metadata.get("quota_limit", 0)
            )
    
    async def get_channel_details(
        self,
        channel_ids: List[str],
        priority: RequestPriority = RequestPriority.MEDIUM
    ) -> Dict[str, Any]:
        """Get channel details with rate limiting"""
        
        request_data = {
            "operation": "channel_details",
            "channel_ids": channel_ids
        }
        
        # Check cache first
        cached_result = await self.rate_limiter.process_cached_request(
            self.user_id, "youtube", "channel_details", request_data
        )
        if cached_result:
            return cached_result
        
        # Check quota
        result, metadata = await self.rate_limiter.check_and_consume_quota(
            self.user_id, self.user_tier, "youtube", "channel_details", request_data, priority
        )
        
        if result == RateLimitResult.ALLOWED:
            try:
                start_time = datetime.utcnow()
                
                # Make API call
                channel_details = await self.youtube_service.get_channel_details(channel_ids)
                
                # Track and cache
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                await self._track_api_call("channel_details", response_time, True)
                
                await self.rate_limiter.cache_response(
                    self.user_id, "youtube", "channel_details", request_data, 
                    channel_details, custom_ttl=259200  # 3 days
                )
                
                return channel_details
                
            except Exception as e:
                await self._track_api_call("channel_details", 0, False)
                raise
        
        else:
            raise APIQuotaExceeded(
                "youtube", self.user_id,
                metadata.get("quota_usage", 0), metadata.get("quota_limit", 0)
            )
    
    # ===== QUOTA MANAGEMENT METHODS =====
    
    async def get_quota_status(self) -> Dict[str, Any]:
        """Get current YouTube quota status for user"""
        return await self.rate_limiter.get_user_quota_status(self.user_id, self.user_tier)
    
    async def process_queued_requests(self, max_items: int = 3) -> List[Dict[str, Any]]:
        """Process queued YouTube requests"""
        return await self.rate_limiter.process_queue(self.user_id, max_items)
    
    def update_user_tier(self, new_tier: str):
        """Update user tier for quota calculations"""
        self.user_tier = new_tier
        logger.info(f"User tier updated to {new_tier} for user {self.user_id}")
    
    # ===== HELPER METHODS =====
    
    async def _track_api_call(self, operation: str, response_time_ms: float, success: bool):
        """Track API call metrics"""
        try:
            # Use Redis manager to track the call
            self.rate_limiter.redis.track_api_call(
                "youtube", self.user_id, response_time_ms, success
            )
        except Exception as e:
            logger.error(f"Failed to track API call metrics: {e}")
    
    # ===== COMPATIBILITY METHODS =====
    # These methods provide compatibility with existing VideoIntelligenceAgent
    
    async def search_videos_by_genre(
        self,
        genre: str,
        max_results: int = 20,
        priority: RequestPriority = RequestPriority.MEDIUM
    ) -> Dict[str, Any]:
        """Search videos by genre (compatibility method)"""
        return await self.search_videos(
            query=f"{genre} videos",
            max_results=max_results,
            priority=priority
        )
    
    async def get_personalized_recommendations(
        self,
        user_preferences: Dict[str, Any],
        max_results: int = 30,
        priority: RequestPriority = RequestPriority.HIGH
    ) -> List[Dict[str, Any]]:
        """Get personalized recommendations (compatibility method)"""
        
        # Build search query from preferences
        interests = user_preferences.get("interests", [])
        categories = user_preferences.get("categories", [])
        
        search_terms = interests + categories
        if not search_terms:
            search_terms = ["trending", "popular"]
        
        recommendations = []
        
        # Search for each term and combine results
        for term in search_terms[:3]:  # Limit to 3 terms to avoid quota exhaustion
            try:
                results = await self.search_videos(
                    query=term,
                    max_results=max_results // len(search_terms),
                    priority=priority
                )
                
                videos = results.get("items", [])
                recommendations.extend(videos)
                
            except APIQuotaExceeded:
                logger.warning(f"Quota exceeded while getting recommendations")
                break
            except Exception as e:
                logger.error(f"Error getting recommendations for term '{term}': {e}")
                continue
        
        return recommendations[:max_results]
    
    async def batch_get_video_details(
        self,
        video_ids: List[str],
        batch_size: int = 50
    ) -> List[Dict[str, Any]]:
        """Get video details in batches (YouTube allows up to 50 IDs per request)"""
        
        all_details = []
        
        # Process in batches
        for i in range(0, len(video_ids), batch_size):
            batch_ids = video_ids[i:i + batch_size]
            
            try:
                batch_details = await self.get_video_details(
                    batch_ids, priority=RequestPriority.HIGH
                )
                
                if "items" in batch_details:
                    all_details.extend(batch_details["items"])
                    
            except APIQuotaExceeded:
                logger.warning(f"Quota exceeded during batch processing at batch {i//batch_size + 1}")
                break
            except Exception as e:
                logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
                continue
        
        return all_details

    async def get_genre_recommendations(
        self,
        genre_name: str,
        personality_profile: Dict[PersonalityTrait, float],
        user_history: List[Dict[str, Any]],
        max_results: int = 6,
        priority: RequestPriority = RequestPriority.MEDIUM
    ) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a specific genre with rate limiting"""
        
        request_data = {
            "operation": "genre_recommendations",
            "genre": genre_name,
            "max_results": max_results,
            "personality_hash": hash(str(sorted(personality_profile.items())))
        }
        
        # Check cache first
        cached_result = await self.rate_limiter.process_cached_request(
            self.user_id, "youtube", "genre_recommendations", request_data
        )
        if cached_result:
            logger.debug(f"Cache hit for genre recommendations: {genre_name}")
            return cached_result
        
        # Check quota
        result, metadata = await self.rate_limiter.check_and_consume_quota(
            self.user_id, self.user_tier, "youtube", "genre_recommendations", request_data, priority
        )
        
        if result == RateLimitResult.CACHED:
            return metadata["cached_data"]
        
        elif result == RateLimitResult.ALLOWED:
            try:
                start_time = datetime.utcnow()
                
                # Use existing YouTube service genre method
                recommendations = await self.youtube_service.get_genre_recommendations(
                    genre_name=genre_name,
                    personality_profile=personality_profile,
                    user_history=user_history,
                    max_results=max_results
                )
                
                # Track metrics
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                await self._track_api_call("genre_recommendations", response_time, True)
                
                # Cache the response
                await self.rate_limiter.cache_response(
                    self.user_id, "youtube", "genre_recommendations", request_data, recommendations
                )
                
                logger.info(f"Genre recommendations completed: {genre_name} ({len(recommendations)} results)")
                return recommendations
                
            except Exception as e:
                await self._track_api_call("genre_recommendations", 0, False)
                logger.error(f"Genre recommendations failed for {genre_name}: {e}")
                
                # Return fallback recommendations
                return self._get_fallback_genre_recommendations(genre_name, max_results)
        
        else:
            logger.warning(f"Genre recommendations denied for {genre_name}")
            return self._get_fallback_genre_recommendations(genre_name, max_results)

    async def get_four_genre_recommendations(
        self,
        personality_profile: Dict[PersonalityTrait, float],
        watch_history: List[Dict[str, Any]],
        videos_per_genre: int = 6,
        priority: RequestPriority = RequestPriority.HIGH
    ) -> Dict[str, Any]:
        """
        Four-genre recommendations were removed from the system. Keep this
        method as a safe fallback to avoid runtime errors from any remaining
        callers. It returns the existing fallback recommendations where
        available and logs the event.
        """
        logger.info("Four-genre recommendations requested but feature removed. Returning fallback.")

        try:
            if hasattr(self, "_get_fallback_four_genre_recommendations"):
                return self._get_fallback_four_genre_recommendations(videos_per_genre)
        except Exception as e:
            logger.debug(f"Fallback helper failed: {e}")

        return {"genres": {}, "message": "Four-genre recommendations removed. Use /video/recommendations/{user_id}."}

    def _get_fallback_genre_recommendations(self, genre_name: str, max_results: int) -> List[Dict[str, Any]]:
        """Provide fallback recommendations when API fails"""
        fallback_videos = {
            "comedy": [
                {"id": "comedy1", "title": "Stand Up Comedy Special", "genre": genre_name},
                {"id": "comedy2", "title": "Funny Animal Compilation", "genre": genre_name},
                {"id": "comedy3", "title": "Comedy Sketch Show", "genre": genre_name},
            ],
            "education": [
                {"id": "edu1", "title": "How Things Work", "genre": genre_name},
                {"id": "edu2", "title": "Science Explained Simply", "genre": genre_name},
                {"id": "edu3", "title": "Learn Something New Today", "genre": genre_name},
            ],
            "technology": [
                {"id": "tech1", "title": "Latest Tech Reviews", "genre": genre_name},
                {"id": "tech2", "title": "Gadget Unboxing", "genre": genre_name},
                {"id": "tech3", "title": "Tech News Weekly", "genre": genre_name},
            ],
            "music": [
                {"id": "music1", "title": "Top Music Videos", "genre": genre_name},
                {"id": "music2", "title": "Live Concert Performance", "genre": genre_name},
                {"id": "music3", "title": "Cover Song Collection", "genre": genre_name},
            ]
        }
        
        default_videos = [
            {"id": f"{genre_name}1", "title": f"Great {genre_name.title()} Content", "genre": genre_name},
            {"id": f"{genre_name}2", "title": f"Popular {genre_name.title()} Videos", "genre": genre_name},
        ]
        
        videos = fallback_videos.get(genre_name.lower(), default_videos)
        return videos[:max_results]

    def _get_fallback_four_genre_recommendations(self, videos_per_genre: int) -> Dict[str, Any]:
        # Removed: four-genre fallback helper deleted as part of feature removal.
        # Keep a minimal placeholder to avoid attribute errors from older callers.
        return {}

# (Removed duplicated fallback block)
# Factory function for creating rate-limited YouTube services
def create_rate_limited_youtube_service(user_id: str, user_tier: str = "free") -> RateLimitedYouTubeService:
    """Create a new rate-limited YouTube service instance"""
    return RateLimitedYouTubeService(user_id, user_tier)