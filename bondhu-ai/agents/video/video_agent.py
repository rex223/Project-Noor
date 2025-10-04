"""
Enhanced Video Intelligence Agent for analyzing user video consumption patterns and personality insights.
Integrates with YouTube Data API to gather viewing data, provide recommendations, and analyze personality traits.
"""

import asyncio
import re
from collections import Counter, defaultdict
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

from agents.base_agent import BaseAgent
from core.config import get_config
from core.services.youtube_service import YouTubeService
from api.models.schemas import DataSource, PersonalityTrait, VideoPreferences

class VideoIntelligenceAgent(BaseAgent):
    """
    Agent specialized in analyzing video consumption patterns for personality insights.
    Uses YouTube Data API and user-provided data to correlate viewing habits with Big Five traits.
    """
    
    def __init__(self, user_id: str, youtube_api_key: Optional[str] = None, **kwargs):
        """
        Initialize Enhanced Video Intelligence Agent.
        
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
        self.youtube_service = YouTubeService(self.youtube_api_key)
        
        # Initialize recommendation engine state
        self.user_feedback_history = []
        self.recommendation_cache = {}
        self.genre_analysis_cache = {}
        self.last_refresh_time = None
        
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

    async def get_personalized_recommendations(self, personality_profile: Dict[PersonalityTrait, float], 
                                             watch_history: List[Dict[str, Any]], 
                                             max_results: int = 20, 
                                             force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get personalized video recommendations based on user's personality and viewing history.
        
        Args:
            personality_profile: User's Big Five personality scores
            watch_history: User's video viewing history
            max_results: Maximum number of recommendations to return
            force_refresh: Whether to force refresh recommendations
            
        Returns:
            List of recommended videos with metadata and personality scores
        """
        try:
            # Check if we need to refresh recommendations
            should_refresh = (
                force_refresh or 
                not self.recommendation_cache or 
                self._should_refresh_recommendations()
            )
            
            if should_refresh:
                # Get fresh recommendations from YouTube service
                recommendations = await self.youtube_service.get_personalized_recommendations(
                    personality_profile=personality_profile,
                    user_history=watch_history,
                    max_results=max_results
                )
                
                # Apply user feedback filtering
                filtered_recommendations = self._apply_feedback_filtering(recommendations)
                
                # Cache recommendations
                self.recommendation_cache = {
                    'recommendations': filtered_recommendations,
                    'timestamp': datetime.now(),
                    'personality_profile': personality_profile.copy()
                }
                
                self.last_refresh_time = datetime.now()
                
                self.logger.info(f"Generated {len(filtered_recommendations)} personalized video recommendations")
                return filtered_recommendations
            else:
                # Return cached recommendations
                return self.recommendation_cache.get('recommendations', [])
                
        except Exception as e:
            self.logger.error(f"Error generating personalized recommendations: {e}")
            return []

    async def get_genre_recommendation_clusters(
        self,
        personality_profile: Dict[PersonalityTrait, float],
        watch_history: List[Dict[str, Any]],
        max_genres: int = 6,
        videos_per_genre: int = 3
    ) -> List[Dict[str, Any]]:
        """Build genre-based clusters of recommendations with persona alignment."""
        ranked_genres = self._rank_genres_by_persona_and_history(
            personality_profile,
            watch_history
        )

        clusters: List[Dict[str, Any]] = []
        seen_video_ids: set[str] = set()

        for genre_entry in ranked_genres:
            if len(clusters) >= max_genres:
                break

            genre_name = genre_entry['genre']
            cluster_position = len(clusters) + 1
            genre_videos = await self.youtube_service.get_genre_recommendations(
                genre_name=genre_name,
                personality_profile=personality_profile,
                user_history=watch_history,
                max_results=videos_per_genre * 2
            )

            curated_videos: List[Dict[str, Any]] = []

            for video in genre_videos:
                if len(curated_videos) >= videos_per_genre:
                    break
                video_id = video.get('id')
                if not video_id or video_id in seen_video_ids:
                    continue

                seen_video_ids.add(video_id)

                curated_videos.append({
                    **video,
                    "genre": genre_name,
                    "watch_url": f"https://www.youtube.com/watch?v={video_id}",
                    "embed_url": f"https://www.youtube.com/embed/{video_id}",
                    "personality_match": round(video.get('personality_score', 0.0) * 100, 1),
                    "combined_score": max(video.get('personality_score', 0.0), genre_entry['combined_score']),
                    "genre_rank": cluster_position,
                    "source": "genre_personalized",
                    "genre_combined_score": round(genre_entry['combined_score'], 3),
                    "thumbnail_urls": {
                        "default": video.get('thumbnail_url', ''),
                        "medium": video.get('thumbnail_url', '').replace('maxresdefault', 'mqdefault'),
                        "high": video.get('thumbnail_url', '').replace('maxresdefault', 'hqdefault')
                    }
                })

            if not curated_videos:
                continue

            clusters.append({
                "genre": genre_name,
                "cluster_rank": cluster_position,
                "history_score": round(genre_entry['history_score'], 3),
                "personality_score": round(genre_entry['personality_score'], 3),
                "combined_score": round(genre_entry['combined_score'], 3),
                "reason": self._generate_genre_reason(
                    genre_name,
                    genre_entry['history_score'],
                    genre_entry['personality_score'],
                    personality_profile
                ),
                "videos": curated_videos
            })

        return clusters

    def _rank_genres_by_persona_and_history(
        self,
        personality_profile: Dict[PersonalityTrait, float],
        watch_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank genres by combining viewing history and personality alignment."""

        history_counter: Counter[str] = Counter()
        watch_time_totals = defaultdict(float)

        for entry in watch_history:
            genre = (
                entry.get('category_name')
                or entry.get('category')
                or self.youtube_service._get_category_name(str(entry.get('category_id', '')))
            )

            if not genre or genre == 'Unknown':
                continue

            history_counter[genre] += 1
            try:
                watch_time_totals[genre] += float(entry.get('watch_time', 0))
            except (TypeError, ValueError):
                continue

        max_count = max(history_counter.values()) if history_counter else 0
        max_watch_time = max(watch_time_totals.values()) if watch_time_totals else 0.0

        history_scores: Dict[str, float] = {}

        for genre in set(list(history_counter.keys()) + list(watch_time_totals.keys())):
            if genre == 'Unknown':
                continue

            count_component = (history_counter[genre] / max_count) if max_count else 0.0
            time_component = (watch_time_totals[genre] / max_watch_time) if max_watch_time else 0.0

            # Weighted combination prioritizing consistency of viewing
            history_scores[genre] = 0.7 * count_component + 0.3 * time_component

        personality_preferences = self.youtube_service._get_preferred_categories(personality_profile)
        personality_scores: Dict[str, float] = {}
        personality_max = max((score for _, score in personality_preferences), default=0.0)
        if personality_max == 0:
            personality_max = 1.0

        for genre, score in personality_preferences:
            if genre == 'Unknown':
                continue
            personality_scores[genre] = score / personality_max

        candidate_genres = set(history_scores.keys()) | set(personality_scores.keys())

        ranked: List[Dict[str, Any]] = []
        for genre in candidate_genres:
            history_score = history_scores.get(genre, 0.0)
            personality_score = personality_scores.get(genre, 0.0)
            combined_score = 0.6 * history_score + 0.4 * personality_score

            ranked.append({
                "genre": genre,
                "history_score": history_score,
                "personality_score": personality_score,
                "combined_score": combined_score
            })

        if not ranked and personality_preferences:
            # As a fallback, surface top personality genres directly
            for genre, score in personality_preferences[:6]:
                ranked.append({
                    "genre": genre,
                    "history_score": 0.0,
                    "personality_score": score / personality_max,
                    "combined_score": score / personality_max
                })

        ranked.sort(key=lambda item: item['combined_score'], reverse=True)

        return ranked

    def _generate_genre_reason(
        self,
        genre: str,
        history_score: float,
        personality_score: float,
        personality_profile: Dict[PersonalityTrait, float]
    ) -> str:
        """Create a human-readable explanation for a genre recommendation."""

        reason_clauses: List[str] = []

        if history_score >= 0.25:
            reason_clauses.append("You've been engaging with this genre recently")

        if personality_score >= 0.2:
            dominant_trait = max(personality_profile.items(), key=lambda item: item[1])[0]
            trait_label = dominant_trait.value.replace('_', ' ').title()
            reason_clauses.append(f"It aligns with your {trait_label.lower()} strengths")

        if not reason_clauses:
            reason_clauses.append("Curated to expand your interests while staying personality-aware")

        return " • ".join(reason_clauses)

    async def analyze_user_video_genres(self, watch_history: List[Dict[str, Any]], 
                                      force_refresh: bool = False) -> Dict[str, Any]:
        """
        Analyze user's video genre preferences and extract personality insights.
        
        Args:
            watch_history: User's video viewing history
            force_refresh: Whether to force refresh analysis
            
        Returns:
            Dictionary containing genre analysis and personality insights
        """
        try:
            cache_key = f"genre_analysis_{self.user_id}"
            
            # Check cache
            if not force_refresh and cache_key in self.genre_analysis_cache:
                cached_data = self.genre_analysis_cache[cache_key]
                if (datetime.now() - cached_data['timestamp']).hours < 6:  # Cache for 6 hours
                    return cached_data['analysis']
            
            # Perform fresh analysis
            analysis = await self.youtube_service.analyze_user_genres(watch_history)
            
            # Enhance analysis with behavioral patterns
            enhanced_analysis = await self._enhance_genre_analysis(analysis, watch_history)
            
            # Cache results
            self.genre_analysis_cache[cache_key] = {
                'analysis': enhanced_analysis,
                'timestamp': datetime.now()
            }
            
            self.logger.info(f"Analyzed {len(watch_history)} videos for genre preferences")
            return enhanced_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing user video genres: {e}")
            return {}

    async def process_user_feedback(self, video_id: str, feedback_type: str, 
                                  additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Process user feedback (like/dislike) for reinforcement learning.
        
        Args:
            video_id: ID of the video being rated
            feedback_type: 'like', 'dislike', 'watch', 'skip'
            additional_data: Additional feedback data (watch time, etc.)
            
        Returns:
            True if feedback was processed successfully
        """
        try:
            feedback_entry = {
                'video_id': video_id,
                'feedback_type': feedback_type,
                'timestamp': datetime.now(),
                'user_id': self.user_id,
                'additional_data': additional_data or {}
            }
            
            # Add to feedback history
            self.user_feedback_history.append(feedback_entry)
            
            # Limit history size to prevent memory issues
            if len(self.user_feedback_history) > 1000:
                self.user_feedback_history = self.user_feedback_history[-800:]  # Keep recent 800
            
            # Store watch history in database for persistent learning
            if feedback_type in ['watch', 'like']:  # Only store positive interactions
                await self._store_watch_history(video_id, additional_data)
            
            # Update recommendation weights based on feedback
            await self._update_recommendation_weights(feedback_entry)
            
            # Log feedback for analysis
            self.logger.info(f"Processed {feedback_type} feedback for video {video_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing user feedback: {e}")
            return False

    async def _store_watch_history(self, video_id: str, additional_data: Dict[str, Any]):
        """Store video watch history in database for persistent recommendations."""
        try:
            from core.database.supabase_client import get_supabase_client
            
            supabase = get_supabase_client()
            
            # Calculate completion rate
            watch_time = additional_data.get('watch_time', 0)
            total_duration = additional_data.get('duration', 0)
            completion_rate = (watch_time / total_duration) if total_duration > 0 else 0.0
            
            # Fetch video metadata (you might want to get this from the video data passed in)
            # For now, we'll use what we have and fetch additional data later
            video_data = {
                'user_id': self.user_id,
                'video_id': video_id,
                'video_title': additional_data.get('video_title', 'Unknown Title'),
                'channel_title': additional_data.get('channel_title', 'Unknown Channel'),
                'category_name': additional_data.get('category_name', 'Entertainment'),
                'watch_time': watch_time,
                'completion_rate': completion_rate,
                'watched_at': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            # Insert into user_video_history table
            result = supabase.supabase.table('user_video_history').insert(video_data).execute()
            
            if result.data:
                self.logger.info(f"Stored watch history for video {video_id}")
            else:
                self.logger.warning(f"Failed to store watch history for video {video_id}")
                
        except Exception as e:
            self.logger.error(f"Error storing watch history: {e}")

    async def get_trending_videos_by_personality(self, personality_profile: Dict[PersonalityTrait, float], 
                                               region_code: str = "US", 
                                               max_results: int = 25) -> List[Dict[str, Any]]:
        """
        Get trending videos filtered and scored by personality compatibility.
        
        Args:
            personality_profile: User's personality profile
            region_code: Regional code for trending videos
            max_results: Maximum number of videos to return
            
        Returns:
            List of trending videos scored for personality compatibility
        """
        try:
            # Get trending videos
            trending_videos = await self.youtube_service.get_trending_videos(
                region_code=region_code,
                max_results=max_results * 2  # Get more to filter from
            )
            
            # Score videos for personality compatibility
            scored_videos = []
            for video in trending_videos:
                score = self.youtube_service._calculate_video_score(
                    video, personality_profile, []
                )
                video['personality_score'] = score
                scored_videos.append(video)
            
            # Sort by personality score and return top results
            scored_videos.sort(key=lambda x: x['personality_score'], reverse=True)
            
            self.logger.info(f"Retrieved {len(scored_videos[:max_results])} personality-matched trending videos")
            return scored_videos[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error getting trending videos by personality: {e}")
            return []

    def should_refresh_recommendations(self) -> bool:
        """Check if recommendations should be refreshed (3x daily schedule)."""
        return self._should_refresh_recommendations()

    def _should_refresh_recommendations(self) -> bool:
        """Determine if recommendations should be refreshed based on schedule."""
        if not self.last_refresh_time:
            return True
        
        # Refresh 3 times daily (every 8 hours)
        hours_since_refresh = (datetime.now() - self.last_refresh_time).total_seconds() / 3600
        return hours_since_refresh >= 8

    def _apply_feedback_filtering(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter recommendations based on user feedback history."""
        if not self.user_feedback_history:
            return recommendations
        
        # Get disliked video IDs and categories
        disliked_videos = set()
        disliked_categories = {}
        liked_categories = {}
        
        for feedback in self.user_feedback_history[-100:]:  # Consider recent feedback
            video_id = feedback['video_id']
            feedback_type = feedback['feedback_type']
            
            if feedback_type == 'dislike':
                disliked_videos.add(video_id)
                # Track disliked categories (would need video metadata)
            elif feedback_type == 'like':
                # Track liked categories (would need video metadata)
                pass
        
        # Filter out disliked videos
        filtered_recommendations = []
        for video in recommendations:
            if video['id'] not in disliked_videos:
                # Apply category-based filtering here if needed
                filtered_recommendations.append(video)
        
        return filtered_recommendations

    async def _enhance_genre_analysis(self, base_analysis: Dict[str, Any], 
                                    watch_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance genre analysis with additional behavioral insights."""
        enhanced = base_analysis.copy()
        
        # Add viewing behavior patterns
        viewing_patterns = await self._analyze_viewing_patterns(watch_history)
        enhanced['viewing_patterns'] = viewing_patterns
        
        # Add content engagement analysis
        engagement_analysis = self._analyze_content_engagement(watch_history)
        enhanced['engagement_patterns'] = engagement_analysis
        
        # Add personality evolution tracking
        if 'personality_insights' in enhanced:
            evolution = self._track_personality_evolution(enhanced['personality_insights'])
            enhanced['personality_evolution'] = evolution
        
        return enhanced

    async def _analyze_viewing_patterns(self, watch_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze detailed viewing behavior patterns."""
        patterns = {
            'total_watch_time': 0,
            'average_session_length': 0,
            'preferred_times': [],
            'binge_watching_score': 0.0,
            'content_diversity_score': 0.0,
            'completion_rate': 0.0
        }
        
        if not watch_history:
            return patterns
        
        # Calculate total watch time
        total_watch_time = sum(video.get('watch_time', 0) for video in watch_history)
        patterns['total_watch_time'] = total_watch_time
        
        # Calculate average session length
        if watch_history:
            patterns['average_session_length'] = total_watch_time / len(watch_history)
        
        # Analyze viewing times
        viewing_hours = []
        for video in watch_history:
            timestamp = video.get('timestamp')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    viewing_hours.append(dt.hour)
                except:
                    pass
        
        if viewing_hours:
            # Group by time periods
            morning = sum(1 for h in viewing_hours if 6 <= h < 12)
            afternoon = sum(1 for h in viewing_hours if 12 <= h < 18)
            evening = sum(1 for h in viewing_hours if 18 <= h < 24)
            night = sum(1 for h in viewing_hours if 0 <= h < 6)
            
            patterns['preferred_times'] = {
                'morning': morning / len(viewing_hours),
                'afternoon': afternoon / len(viewing_hours),
                'evening': evening / len(viewing_hours),
                'night': night / len(viewing_hours)
            }
        
        # Calculate content diversity
        categories = [video.get('category', 'Unknown') for video in watch_history]
        unique_categories = len(set(categories))
        patterns['content_diversity_score'] = unique_categories / len(categories) if categories else 0
        
        # Calculate completion rate
        completed_videos = sum(1 for video in watch_history 
                             if video.get('completion_rate', 0) > 0.8)
        patterns['completion_rate'] = completed_videos / len(watch_history) if watch_history else 0
        
        return patterns

    def _analyze_content_engagement(self, watch_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user engagement with different types of content."""
        engagement = {
            'high_engagement_categories': [],
            'low_engagement_categories': [],
            'skip_patterns': [],
            'replay_patterns': []
        }
        
        category_engagement = {}
        
        for video in watch_history:
            category = video.get('category', 'Unknown')
            completion_rate = video.get('completion_rate', 0)
            
            if category not in category_engagement:
                category_engagement[category] = []
            
            category_engagement[category].append(completion_rate)
        
        # Calculate average engagement per category
        for category, rates in category_engagement.items():
            avg_rate = sum(rates) / len(rates)
            
            if avg_rate > 0.7:
                engagement['high_engagement_categories'].append((category, avg_rate))
            elif avg_rate < 0.3:
                engagement['low_engagement_categories'].append((category, avg_rate))
        
        # Sort by engagement level
        engagement['high_engagement_categories'].sort(key=lambda x: x[1], reverse=True)
        engagement['low_engagement_categories'].sort(key=lambda x: x[1])
        
        return engagement

    def _track_personality_evolution(self, personality_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Track how personality insights evolve over time."""
        evolution = {
            'stable_traits': [],
            'evolving_traits': [],
            'confidence_trends': {}
        }
        
        # This would compare with historical personality data
        # For now, return basic structure
        for trait, data in personality_insights.items():
            confidence = data.get('confidence', 0)
            evolution['confidence_trends'][trait] = confidence
            
            if confidence > 0.7:
                evolution['stable_traits'].append(trait)
            elif confidence < 0.4:
                evolution['evolving_traits'].append(trait)
        
        return evolution

    async def _update_recommendation_weights(self, feedback_entry: Dict[str, Any]) -> None:
        """Update recommendation algorithm weights based on user feedback."""
        # This would implement reinforcement learning logic
        # For now, just log the feedback for future processing
        feedback_type = feedback_entry['feedback_type']
        video_id = feedback_entry['video_id']
        
        # In a full implementation, this would:
        # 1. Update neural network weights
        # 2. Adjust category preferences
        # 3. Update personality-content mappings
        # 4. Store feedback for batch learning
        
        self.logger.debug(f"Updated recommendation weights based on {feedback_type} for {video_id}")

    def _initialize_youtube_service(self):
        """Initialize YouTube Data API service (legacy method for compatibility)."""
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