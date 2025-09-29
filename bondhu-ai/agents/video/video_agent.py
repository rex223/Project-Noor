"""
Video Intelligence Agent for analyzing user video consumption patterns and personality insights.
Integrates with YouTube Data API to gather viewing data and preferences.
"""

import asyncio
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

from ..base_agent import BaseAgent
from ...core.config import get_config
from ...api.models.schemas import DataSource, PersonalityTrait, VideoPreferences

# For YouTube API integration (would need google-api-python-client)
# from googleapiclient.discovery import build

class VideoIntelligenceAgent(BaseAgent):
    """
    Agent specialized in analyzing video consumption patterns for personality insights.
    Uses YouTube Data API and user-provided data to correlate viewing habits with Big Five traits.
    """
    
    def __init__(self, user_id: str, youtube_api_key: Optional[str] = None, **kwargs):
        """
        Initialize Video Intelligence Agent.
        
        Args:
            user_id: User ID for this agent session
            youtube_api_key: YouTube Data API key
            **kwargs: Additional arguments passed to BaseAgent
        """
        super().__init__(
            agent_type=DataSource.VIDEO,
            user_id=user_id,
            **kwargs
        )
        
        self.youtube_api_key = youtube_api_key or self.config.youtube.api_key
        self.youtube_service = None
        self._initialize_youtube_service()
        
        # Video category to personality mappings based on research
        self.category_personality_map = {
            # Openness correlations
            "Education": {"openness": 0.8, "conscientiousness": 0.6},
            "Science & Technology": {"openness": 0.7, "conscientiousness": 0.5},
            "Documentary": {"openness": 0.8, "conscientiousness": 0.4},
            "Film & Animation": {"openness": 0.6, "extraversion": 0.3},
            "Travel & Events": {"openness": 0.7, "extraversion": 0.5},
            "Arts": {"openness": 0.9, "agreeableness": 0.4},
            
            # Extraversion correlations
            "Entertainment": {"extraversion": 0.6, "agreeableness": 0.4},
            "Comedy": {"extraversion": 0.7, "agreeableness": 0.5},
            "Music": {"extraversion": 0.5, "openness": 0.6},
            "Sports": {"extraversion": 0.6, "conscientiousness": 0.4},
            "Gaming": {"extraversion": 0.4, "openness": 0.5},
            
            # Conscientiousness correlations
            "Howto & Style": {"conscientiousness": 0.7, "agreeableness": 0.4},
            "Autos & Vehicles": {"conscientiousness": 0.6, "openness": 0.3},
            "News & Politics": {"conscientiousness": 0.5, "openness": 0.6},
            
            # Agreeableness correlations
            "People & Blogs": {"agreeableness": 0.6, "extraversion": 0.4},
            "Pets & Animals": {"agreeableness": 0.8, "openness": 0.4},
            "Nonprofits & Activism": {"agreeableness": 0.9, "conscientiousness": 0.6},
            
            # Neuroticism correlations
            "News & Politics": {"neuroticism": 0.4, "openness": 0.6},
            "Horror": {"neuroticism": 0.6, "openness": 0.5}
        }
        
        # Content themes to personality mappings
        self.theme_personality_map = {
            "self_improvement": {"conscientiousness": 0.7, "openness": 0.5},
            "relationships": {"agreeableness": 0.6, "extraversion": 0.4},
            "creativity": {"openness": 0.8, "extraversion": 0.3},
            "productivity": {"conscientiousness": 0.8, "neuroticism": -0.3},
            "mindfulness": {"agreeableness": 0.6, "neuroticism": -0.5},
            "adventure": {"openness": 0.7, "extraversion": 0.6},
            "technology": {"openness": 0.6, "conscientiousness": 0.5},
            "social_issues": {"agreeableness": 0.7, "conscientiousness": 0.5}
        }
        
        # Viewing behavior patterns
        self.behavior_patterns = {
            "binge_watching": {"neuroticism": 0.4, "conscientiousness": -0.3},
            "diverse_content": {"openness": 0.7, "conscientiousness": 0.3},
            "repeat_viewing": {"conscientiousness": 0.5, "neuroticism": 0.2},
            "live_streams": {"extraversion": 0.6, "agreeableness": 0.4},
            "short_videos": {"extraversion": 0.4, "neuroticism": 0.3},
            "long_form": {"conscientiousness": 0.6, "openness": 0.5}
        }
    
    def _initialize_youtube_service(self):
        """Initialize YouTube Data API service."""
        if self.youtube_api_key:
            try:
                # Note: This would require google-api-python-client
                # self.youtube_service = build('youtube', 'v3', developerKey=self.youtube_api_key)
                self.logger.info("YouTube service would be initialized with API key")
            except Exception as e:
                self.logger.warning(f"Failed to initialize YouTube service: {e}")
        else:
            self.logger.info("No YouTube API key provided - will use limited functionality")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Video Intelligence Agent."""
        return """You are a Video Intelligence Agent specialized in analyzing video consumption patterns for personality insights.

Your capabilities include:
- Analyzing YouTube viewing history and preferences
- Correlating video categories with Big Five personality traits
- Interpreting viewing behavior patterns
- Understanding content engagement metrics
- Providing video-based personality assessments

You have access to:
- User's video viewing history
- Channel subscriptions and preferences
- Video categories and content themes
- Viewing time patterns and session lengths
- Engagement metrics (likes, comments, shares)

When analyzing video data, consider:
- Educational content consumption indicates openness to experience
- Entertainment preferences correlate with extraversion
- Diverse content viewing suggests openness
- Organized playlists indicate conscientiousness
- Social content engagement reflects agreeableness
- News/political content may indicate conscientiousness or neuroticism

Provide insights based on established media psychology research while being sensitive to individual differences and cultural contexts."""
    
    async def collect_data(self, force_refresh: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Collect video data from YouTube API and user input.
        
        Args:
            force_refresh: Whether to force refresh of cached data
            **kwargs: Additional arguments including manual video data
            
        Returns:
            Dictionary containing video data
        """
        data = {
            "watch_history": [],
            "subscriptions": [],
            "liked_videos": [],
            "playlists": [],
            "viewing_patterns": {},
            "category_analysis": {},
            "channel_analysis": {},
            "engagement_metrics": {},
            "content_themes": []
        }
        
        try:
            # If YouTube service is available, use API
            if self.youtube_service:
                data.update(await self._collect_youtube_api_data())
            
            # Collect from user-provided data
            manual_data = kwargs.get("manual_video_data", {})
            if manual_data:
                data.update(await self._process_manual_video_data(manual_data))
            
            # Analyze collected data
            if data["watch_history"] or data["subscriptions"]:
                data["viewing_patterns"] = await self._analyze_viewing_patterns(data)
                data["category_analysis"] = await self._analyze_categories(data)
                data["channel_analysis"] = await self._analyze_channels(data)
                data["content_themes"] = await self._extract_content_themes(data)
            
            self.logger.info(f"Collected video data: {len(data['watch_history'])} videos, {len(data['subscriptions'])} subscriptions")
            return data
            
        except Exception as e:
            self.logger.error(f"Error collecting video data: {e}")
            return data
    
    async def _collect_youtube_api_data(self) -> Dict[str, Any]:
        """Collect data using YouTube Data API."""
        # Note: This would require actual YouTube API implementation
        # For now, returning empty structure
        return {
            "watch_history": [],
            "subscriptions": [],
            "liked_videos": [],
            "playlists": []
        }
    
    async def _process_manual_video_data(self, manual_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process manually provided video data."""
        processed_data = {
            "watch_history": [],
            "subscriptions": [],
            "liked_videos": [],
            "playlists": []
        }
        
        # Process favorite channels
        favorite_channels = manual_data.get("favorite_channels", [])
        for channel in favorite_channels:
            processed_data["subscriptions"].append({
                "channel_name": channel.get("name", ""),
                "category": channel.get("category", "Entertainment"),
                "subscriber_count": channel.get("subscribers", 0),
                "engagement_level": channel.get("engagement", "medium")
            })
        
        # Process viewing preferences
        preferences = manual_data.get("viewing_preferences", {})
        if preferences:
            processed_data["viewing_preferences"] = preferences
        
        # Process video URLs if provided
        video_urls = manual_data.get("recent_videos", [])
        for url in video_urls:
            video_info = await self._extract_video_info_from_url(url)
            if video_info:
                processed_data["watch_history"].append(video_info)
        
        return processed_data
    
    async def _extract_video_info_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract video information from YouTube URL."""
        try:
            # Parse YouTube URL to get video ID
            parsed_url = urlparse(url)
            video_id = None
            
            if 'youtube.com' in parsed_url.netloc:
                video_id = parse_qs(parsed_url.query).get('v', [None])[0]
            elif 'youtu.be' in parsed_url.netloc:
                video_id = parsed_url.path.lstrip('/')
            
            if video_id:
                # In a real implementation, would fetch video details from API
                return {
                    "video_id": video_id,
                    "title": f"Video {video_id}",
                    "category": "Entertainment",  # Default category
                    "duration": 0,
                    "view_count": 0
                }
        except Exception as e:
            self.logger.error(f"Error extracting video info from URL {url}: {e}")
        
        return None
    
    async def _analyze_viewing_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze viewing behavior patterns."""
        patterns = {
            "total_videos_watched": len(data["watch_history"]),
            "average_session_length": 0,
            "preferred_times": [],
            "content_diversity": 0.0,
            "binge_watching_tendency": 0.0,
            "live_stream_preference": 0.0,
            "repeat_viewing": 0.0
        }
        
        watch_history = data["watch_history"]
        if not watch_history:
            return patterns
        
        # Analyze content diversity
        categories = [video.get("category", "Unknown") for video in watch_history]
        unique_categories = len(set(categories))
        patterns["content_diversity"] = unique_categories / len(categories) if categories else 0
        
        # Analyze viewing times (if timestamps available)
        timestamps = [video.get("watched_at") for video in watch_history if video.get("watched_at")]
        if timestamps:
            hours = []
            for timestamp in timestamps:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hours.append(dt.hour)
                except:
                    continue
            patterns["preferred_times"] = hours
        
        # Estimate binge watching (consecutive videos from same channel)
        channels = [video.get("channel_name") for video in watch_history]
        consecutive_same_channel = 0
        for i in range(1, len(channels)):
            if channels[i] == channels[i-1]:
                consecutive_same_channel += 1
        
        patterns["binge_watching_tendency"] = consecutive_same_channel / len(channels) if channels else 0
        
        return patterns
    
    async def _analyze_categories(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze video category distribution."""
        category_counts = {}
        total_videos = 0
        
        # Count categories from watch history
        for video in data["watch_history"]:
            category = video.get("category", "Unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
            total_videos += 1
        
        # Count categories from subscriptions
        for channel in data["subscriptions"]:
            category = channel.get("category", "Unknown")
            # Weight subscriptions higher than individual videos
            category_counts[category] = category_counts.get(category, 0) + 3
            total_videos += 3
        
        # Calculate percentages
        if total_videos == 0:
            return {}
        
        category_percentages = {
            category: count / total_videos
            for category, count in category_counts.items()
        }
        
        return category_percentages
    
    async def _analyze_channels(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze channel preferences and patterns."""
        analysis = {
            "total_subscriptions": len(data["subscriptions"]),
            "channel_diversity": 0.0,
            "educational_channels": 0,
            "entertainment_channels": 0,
            "creator_vs_corporate": {"creator": 0, "corporate": 0}
        }
        
        subscriptions = data["subscriptions"]
        if not subscriptions:
            return analysis
        
        # Count channel types
        educational_keywords = ["tutorial", "learning", "education", "course", "lecture"]
        entertainment_keywords = ["gaming", "comedy", "entertainment", "vlog", "fun"]
        
        for channel in subscriptions:
            channel_name = channel.get("channel_name", "").lower()
            category = channel.get("category", "").lower()
            
            # Check if educational
            if any(keyword in channel_name or keyword in category for keyword in educational_keywords):
                analysis["educational_channels"] += 1
            
            # Check if entertainment
            if any(keyword in channel_name or keyword in category for keyword in entertainment_keywords):
                analysis["entertainment_channels"] += 1
            
            # Estimate creator vs corporate (simple heuristic)
            subscriber_count = channel.get("subscriber_count", 0)
            if subscriber_count > 1000000:  # Large channels likely corporate
                analysis["creator_vs_corporate"]["corporate"] += 1
            else:
                analysis["creator_vs_corporate"]["creator"] += 1
        
        # Calculate diversity (different categories)
        categories = [channel.get("category", "Unknown") for channel in subscriptions]
        unique_categories = len(set(categories))
        analysis["channel_diversity"] = unique_categories / len(categories) if categories else 0
        
        return analysis
    
    async def _extract_content_themes(self, data: Dict[str, Any]) -> List[str]:
        """Extract content themes from video titles and descriptions."""
        themes = []
        
        # Keywords for different themes
        theme_keywords = {
            "self_improvement": ["productivity", "motivation", "success", "habits", "goals"],
            "relationships": ["dating", "relationship", "love", "friendship", "social"],
            "creativity": ["art", "creative", "design", "music", "writing"],
            "technology": ["tech", "coding", "programming", "software", "AI"],
            "mindfulness": ["meditation", "mindful", "wellness", "mental health", "anxiety"],
            "adventure": ["travel", "adventure", "explore", "outdoor", "hiking"],
            "social_issues": ["politics", "society", "justice", "environment", "activism"]
        }
        
        # Analyze video titles
        all_text = []
        for video in data["watch_history"]:
            title = video.get("title", "").lower()
            description = video.get("description", "").lower()
            all_text.append(title + " " + description)
        
        # Check for theme keywords
        for theme, keywords in theme_keywords.items():
            theme_score = 0
            for text in all_text:
                for keyword in keywords:
                    if keyword in text:
                        theme_score += 1
            
            if theme_score > 0:
                themes.append(theme)
        
        return themes
    
    async def analyze_personality(self, data: Dict[str, Any]) -> Dict[PersonalityTrait, float]:
        """
        Analyze personality traits from video consumption data.
        
        Args:
            data: Video data collected from various sources
            
        Returns:
            Dictionary mapping personality traits to scores (0-100)
        """
        personality_scores = {trait: 50.0 for trait in PersonalityTrait}
        
        if not data or not any(data.values()):
            return personality_scores
        
        # Analyze based on content categories
        category_analysis = data.get("category_analysis", {})
        self._apply_category_analysis(personality_scores, category_analysis)
        
        # Analyze based on viewing patterns
        viewing_patterns = data.get("viewing_patterns", {})
        self._apply_viewing_pattern_analysis(personality_scores, viewing_patterns)
        
        # Analyze based on channel preferences
        channel_analysis = data.get("channel_analysis", {})
        self._apply_channel_analysis(personality_scores, channel_analysis)
        
        # Analyze based on content themes
        content_themes = data.get("content_themes", [])
        self._apply_theme_analysis(personality_scores, content_themes)
        
        # Normalize scores to 0-100 range
        for trait in personality_scores:
            personality_scores[trait] = max(0, min(100, personality_scores[trait]))
        
        self.logger.info(f"Video personality analysis completed: {personality_scores}")
        return personality_scores
    
    def _apply_category_analysis(self, scores: Dict[PersonalityTrait, float], categories: Dict[str, float]):
        """Apply category analysis to personality scores."""
        for category, percentage in categories.items():
            if category in self.category_personality_map:
                for trait, correlation in self.category_personality_map[category].items():
                    trait_enum = PersonalityTrait(trait)
                    # Apply correlation weighted by category percentage
                    adjustment = correlation * percentage * 25  # Scale adjustment
                    scores[trait_enum] += adjustment
    
    def _apply_viewing_pattern_analysis(self, scores: Dict[PersonalityTrait, float], patterns: Dict[str, Any]):
        """Apply viewing pattern analysis to personality scores."""
        # Content diversity affects openness
        diversity = patterns.get("content_diversity", 0.5)
        scores[PersonalityTrait.OPENNESS] += (diversity - 0.5) * 20
        
        # Binge watching affects neuroticism and conscientiousness
        binge_tendency = patterns.get("binge_watching_tendency", 0.0)
        if binge_tendency > 0.3:
            scores[PersonalityTrait.NEUROTICISM] += binge_tendency * 15
            scores[PersonalityTrait.CONSCIENTIOUSNESS] -= binge_tendency * 10
        
        # Regular viewing times suggest conscientiousness
        preferred_times = patterns.get("preferred_times", [])
        if preferred_times:
            # Consistent viewing times (low variance) suggest conscientiousness
            if len(set(preferred_times)) < len(preferred_times) * 0.3:  # Low time diversity
                scores[PersonalityTrait.CONSCIENTIOUSNESS] += 8
    
    def _apply_channel_analysis(self, scores: Dict[PersonalityTrait, float], channel_data: Dict[str, Any]):
        """Apply channel analysis to personality scores."""
        total_subs = channel_data.get("total_subscriptions", 0)
        educational_channels = channel_data.get("educational_channels", 0)
        channel_diversity = channel_data.get("channel_diversity", 0.5)
        
        # Many subscriptions suggest conscientiousness and extraversion
        if total_subs > 20:
            scores[PersonalityTrait.CONSCIENTIOUSNESS] += 5
            scores[PersonalityTrait.EXTRAVERSION] += 3
        
        # Educational content suggests openness and conscientiousness
        if total_subs > 0:
            education_ratio = educational_channels / total_subs
            scores[PersonalityTrait.OPENNESS] += education_ratio * 15
            scores[PersonalityTrait.CONSCIENTIOUSNESS] += education_ratio * 10
        
        # Channel diversity suggests openness
        scores[PersonalityTrait.OPENNESS] += (channel_diversity - 0.5) * 15
    
    def _apply_theme_analysis(self, scores: Dict[PersonalityTrait, float], themes: List[str]):
        """Apply content theme analysis to personality scores."""
        for theme in themes:
            if theme in self.theme_personality_map:
                for trait, correlation in self.theme_personality_map[theme].items():
                    trait_enum = PersonalityTrait(trait)
                    # Apply correlation for theme presence
                    adjustment = correlation * 8  # Fixed adjustment per theme
                    scores[trait_enum] += adjustment
    
    async def _get_trait_confidence(self, trait: PersonalityTrait, data: Dict[str, Any]) -> float:
        """Calculate confidence for specific traits based on video data."""
        base_confidence = 0.1
        
        # Increase confidence based on data richness
        watch_history_size = len(data.get("watch_history", []))
        subscriptions_size = len(data.get("subscriptions", []))
        categories_count = len(data.get("category_analysis", {}))
        
        # More data = higher confidence
        if watch_history_size > 10:
            base_confidence += 0.1
        if subscriptions_size > 5:
            base_confidence += 0.15
        if categories_count > 3:
            base_confidence += 0.1
        
        # Trait-specific confidence adjustments
        if trait == PersonalityTrait.OPENNESS:
            diversity = data.get("viewing_patterns", {}).get("content_diversity", 0)
            if diversity > 0.6 or diversity < 0.3:  # Strong diversity signal
                base_confidence += 0.1
        
        elif trait == PersonalityTrait.CONSCIENTIOUSNESS:
            educational_ratio = 0
            channel_data = data.get("channel_analysis", {})
            total_subs = channel_data.get("total_subscriptions", 0)
            educational = channel_data.get("educational_channels", 0)
            if total_subs > 0:
                educational_ratio = educational / total_subs
                if educational_ratio > 0.3:  # High educational content
                    base_confidence += 0.1
        
        return min(0.25, base_confidence)  # Cap additional confidence