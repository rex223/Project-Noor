"""
Enhanced YouTube Data V3 API service for fetching video data and analyzing user preferences.
Integrates with personality system to provide personalized video recommendations.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode
import random

from core.config import get_config
from core.database.models import PersonalityTrait  # Enum for iteration


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

    async def get_trending_videos(self, region_code: str = "US", max_results: int = 50) -> List[Dict[str, Any]]:
        """Fetch trending videos from YouTube."""
        try:
            params = {
                'part': 'snippet,statistics,contentDetails',
                'chart': 'mostPopular',
                'regionCode': region_code,
                'maxResults': max_results,
                'key': self.api_key
            }
            
            url = f"{self.base_url}/videos?" + urlencode(params)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._process_video_data(data.get('items', []))
                    else:
                        self.logger.error(f"YouTube API error: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"Error fetching trending videos: {e}")
            return []

    async def search_videos(self, query: str, max_results: int = 25, category_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for videos based on query and optional category."""
        try:
            params = {
                'part': 'snippet',
                'type': 'video',
                'q': query,
                'maxResults': max_results,
                'order': 'relevance',
                'key': self.api_key
            }
            
            if category_id:
                params['videoCategoryId'] = category_id
            
            url = f"{self.base_url}/search?" + urlencode(params)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        video_ids = [item['id']['videoId'] for item in data.get('items', [])]
                        
                        # Get detailed video information
                        return await self.get_video_details(video_ids)
                    else:
                        self.logger.error(f"YouTube search API error: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"Error searching videos: {e}")
            return []

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
            
            url = f"{self.base_url}/videos?" + urlencode(params)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._process_video_data(data.get('items', []))
                    else:
                        self.logger.error(f"YouTube video details API error: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"Error fetching video details: {e}")
            return []

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

            return scored_videos[:max_results]

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
            
            # If no personalized recommendations found, fallback to popular videos
            if not scored_videos:
                self.logger.warning("No personalized recommendations found. Falling back to popular videos.")
                fallback_results = await self.get_trending_videos(max_results=max_results)
                return fallback_results
            
            return scored_videos[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error generating personalized recommendations: {e}")
            return []