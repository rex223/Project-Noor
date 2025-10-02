"""
Music Intelligence Agent for analyzing user music preferences and personality insights.
Integrates with Spotify API to gather listening data and patterns.
"""

import asyncio
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent
from core.config import get_config
from api.models.schemas import DataSource, PersonalityTraitModel as PersonalityTrait, MusicPreferences

class MusicIntelligenceAgent(BaseAgent):
    """
    Agent specialized in analyzing music preferences for personality insights.
    Uses Spotify API to gather listening data and correlate with Big Five traits.
    """
    
    def __init__(self, user_id: str, spotify_token: Optional[str] = None, **kwargs):
        """
        Initialize Music Intelligence Agent.
        
        Args:
            user_id: User ID for this agent session
            spotify_token: OAuth token for Spotify API access
            **kwargs: Additional arguments passed to BaseAgent
        """
        super().__init__(
            agent_type=DataSource.MUSIC,
            user_id=user_id,
            **kwargs
        )
        
        self.spotify_token = spotify_token
        self.spotify_client = None
        self._initialize_spotify_client()
        
        # Genre-to-personality mappings based on research
        self.genre_personality_map = {
            # Openness correlations
            "jazz": {"openness": 0.8, "conscientiousness": 0.3},
            "classical": {"openness": 0.7, "conscientiousness": 0.6},
            "experimental": {"openness": 0.9, "neuroticism": 0.4},
            "indie": {"openness": 0.7, "extraversion": -0.2},
            "world": {"openness": 0.8, "agreeableness": 0.5},
            
            # Extraversion correlations
            "pop": {"extraversion": 0.6, "agreeableness": 0.4},
            "dance": {"extraversion": 0.8, "openness": 0.3},
            "hip-hop": {"extraversion": 0.7, "neuroticism": 0.3},
            "electronic": {"extraversion": 0.5, "openness": 0.6},
            
            # Conscientiousness correlations
            "country": {"conscientiousness": 0.6, "agreeableness": 0.5},
            "folk": {"conscientiousness": 0.5, "agreeableness": 0.6},
            
            # Agreeableness correlations
            "r&b": {"agreeableness": 0.6, "extraversion": 0.4},
            "soul": {"agreeableness": 0.7, "openness": 0.5},
            "gospel": {"agreeableness": 0.8, "conscientiousness": 0.6},
            
            # Neuroticism correlations
            "metal": {"neuroticism": 0.6, "openness": 0.4},
            "punk": {"neuroticism": 0.7, "openness": 0.5},
            "emo": {"neuroticism": 0.8, "extraversion": -0.3},
            "blues": {"neuroticism": 0.5, "openness": 0.6}
        }
        
        # Audio features to personality mappings
        self.audio_feature_map = {
            "energy": {"extraversion": 0.6, "neuroticism": 0.3},
            "valence": {"extraversion": 0.5, "neuroticism": -0.7},
            "danceability": {"extraversion": 0.7, "agreeableness": 0.3},
            "acousticness": {"openness": 0.4, "conscientiousness": 0.3},
            "instrumentalness": {"openness": 0.6, "extraversion": -0.4},
            "complexity": {"openness": 0.8, "conscientiousness": 0.4}
        }
    
    def _initialize_spotify_client(self):
        """Initialize Spotify API client."""
        if self.spotify_token:
            try:
                # Use existing token
                self.spotify_client = spotipy.Spotify(auth=self.spotify_token)
                self.logger.info("Spotify client initialized with provided token")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Spotify with token: {e}")
        else:
            self.logger.info("No Spotify token provided - will need OAuth flow")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Music Intelligence Agent."""
        return """You are a Music Intelligence Agent specialized in analyzing music preferences for personality insights.

Your capabilities include:
- Analyzing Spotify listening data and patterns
- Correlating music genres with Big Five personality traits
- Interpreting audio features for personality insights
- Understanding listening behavior patterns
- Providing music-based personality assessments

You have access to:
- User's Spotify listening history
- Audio feature analysis (energy, valence, danceability, etc.)
- Genre preferences and distributions
- Listening time patterns and habits
- Artist and track preferences

When analyzing music data, consider:
- Genre diversity indicates openness to experience
- High-energy music often correlates with extraversion
- Complex music (jazz, classical) suggests openness
- Repetitive listening may indicate conscientiousness
- Mood-based listening patterns reflect emotional stability

Provide insights based on established music psychology research while being sensitive to individual differences and cultural contexts."""
    
    async def collect_data(self, force_refresh: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Collect music data from Spotify API.
        
        Args:
            force_refresh: Whether to force refresh of cached data
            **kwargs: Additional arguments
            
        Returns:
            Dictionary containing music data
        """
        if not self.spotify_client:
            self.logger.warning("Spotify client not initialized")
            return {}
        
        try:
            data = {
                "recently_played": await self._get_recently_played(),
                "top_tracks": await self._get_top_tracks(),
                "top_artists": await self._get_top_artists(),
                "audio_features": {},
                "genre_analysis": {},
                "listening_patterns": {},
                "playlist_analysis": await self._analyze_playlists()
            }
            
            # Get audio features for top tracks
            if data["top_tracks"]:
                track_ids = [track["id"] for track in data["top_tracks"][:50]]
                data["audio_features"] = await self._get_audio_features(track_ids)
            
            # Analyze genres
            data["genre_analysis"] = await self._analyze_genres(data["top_artists"])
            
            # Analyze listening patterns
            data["listening_patterns"] = await self._analyze_listening_patterns(data["recently_played"])
            
            self.logger.info(f"Collected music data: {len(data['top_tracks'])} tracks, {len(data['top_artists'])} artists")
            return data
            
        except Exception as e:
            self.logger.error(f"Error collecting music data: {e}")
            return {}
    
    async def _get_recently_played(self) -> List[Dict[str, Any]]:
        """Get recently played tracks."""
        try:
            results = await asyncio.to_thread(
                self.spotify_client.current_user_recently_played,
                limit=50
            )
            return results.get("items", [])
        except Exception as e:
            self.logger.error(f"Error getting recently played: {e}")
            return []
    
    async def _get_top_tracks(self, time_range: str = "medium_term") -> List[Dict[str, Any]]:
        """Get user's top tracks."""
        try:
            results = await asyncio.to_thread(
                self.spotify_client.current_user_top_tracks,
                limit=50,
                time_range=time_range
            )
            return results.get("items", [])
        except Exception as e:
            self.logger.error(f"Error getting top tracks: {e}")
            return []
    
    async def _get_top_artists(self, time_range: str = "medium_term") -> List[Dict[str, Any]]:
        """Get user's top artists."""
        try:
            results = await asyncio.to_thread(
                self.spotify_client.current_user_top_artists,
                limit=50,
                time_range=time_range
            )
            return results.get("items", [])
        except Exception as e:
            self.logger.error(f"Error getting top artists: {e}")
            return []
    
    async def _get_audio_features(self, track_ids: List[str]) -> Dict[str, Any]:
        """Get audio features for tracks."""
        try:
            # Process in batches of 100 (Spotify limit)
            all_features = []
            for i in range(0, len(track_ids), 100):
                batch = track_ids[i:i+100]
                features = await asyncio.to_thread(
                    self.spotify_client.audio_features,
                    batch
                )
                if features:
                    all_features.extend(features)
            
            # Calculate averages
            if not all_features:
                return {}
            
            # Filter out None values
            valid_features = [f for f in all_features if f is not None]
            if not valid_features:
                return {}
            
            # Calculate mean values for audio features
            feature_keys = ["energy", "valence", "danceability", "acousticness", 
                           "instrumentalness", "speechiness", "liveness", "tempo"]
            
            averaged_features = {}
            for key in feature_keys:
                values = [f[key] for f in valid_features if key in f and f[key] is not None]
                if values:
                    averaged_features[key] = sum(values) / len(values)
            
            return averaged_features
            
        except Exception as e:
            self.logger.error(f"Error getting audio features: {e}")
            return {}
    
    async def _analyze_genres(self, artists: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze genre distribution from artists."""
        genre_counts = {}
        total_genres = 0
        
        for artist in artists:
            for genre in artist.get("genres", []):
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
                total_genres += 1
        
        # Calculate genre percentages
        if total_genres == 0:
            return {}
        
        genre_percentages = {
            genre: count / total_genres 
            for genre, count in genre_counts.items()
        }
        
        return genre_percentages
    
    async def _analyze_listening_patterns(self, recently_played: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze listening patterns and habits."""
        if not recently_played:
            return {}
        
        patterns = {
            "listening_times": [],
            "track_repetition": {},
            "session_lengths": [],
            "diversity_score": 0.0
        }
        
        # Analyze listening times
        for item in recently_played:
            played_at = item.get("played_at")
            if played_at:
                # Extract hour for time pattern analysis
                hour = datetime.fromisoformat(played_at.replace('Z', '+00:00')).hour
                patterns["listening_times"].append(hour)
        
        # Calculate track repetition
        track_ids = [item["track"]["id"] for item in recently_played if "track" in item]
        for track_id in track_ids:
            patterns["track_repetition"][track_id] = patterns["track_repetition"].get(track_id, 0) + 1
        
        # Calculate diversity score (unique tracks / total tracks)
        if track_ids:
            patterns["diversity_score"] = len(set(track_ids)) / len(track_ids)
        
        return patterns
    
    async def _analyze_playlists(self) -> Dict[str, Any]:
        """Analyze user's playlists for additional insights."""
        try:
            playlists = await asyncio.to_thread(
                self.spotify_client.current_user_playlists,
                limit=50
            )
            
            playlist_analysis = {
                "total_playlists": len(playlists.get("items", [])),
                "public_playlists": 0,
                "collaborative_playlists": 0,
                "playlist_names": []
            }
            
            for playlist in playlists.get("items", []):
                if playlist.get("public"):
                    playlist_analysis["public_playlists"] += 1
                if playlist.get("collaborative"):
                    playlist_analysis["collaborative_playlists"] += 1
                playlist_analysis["playlist_names"].append(playlist.get("name", ""))
            
            return playlist_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing playlists: {e}")
            return {}
    
    async def analyze_personality(self, data: Dict[str, Any]) -> Dict[PersonalityTrait, float]:
        """
        Analyze personality traits from music data.
        
        Args:
            data: Music data collected from Spotify
            
        Returns:
            Dictionary mapping personality traits to scores (0-100)
        """
        personality_scores = {trait: 50.0 for trait in PersonalityTrait}
        
        if not data:
            return personality_scores
        
        # Analyze based on audio features
        audio_features = data.get("audio_features", {})
        self._apply_audio_feature_analysis(personality_scores, audio_features)
        
        # Analyze based on genres
        genre_analysis = data.get("genre_analysis", {})
        self._apply_genre_analysis(personality_scores, genre_analysis)
        
        # Analyze based on listening patterns
        listening_patterns = data.get("listening_patterns", {})
        self._apply_listening_pattern_analysis(personality_scores, listening_patterns)
        
        # Analyze based on playlist behavior
        playlist_analysis = data.get("playlist_analysis", {})
        self._apply_playlist_analysis(personality_scores, playlist_analysis)
        
        # Normalize scores to 0-100 range
        for trait in personality_scores:
            personality_scores[trait] = max(0, min(100, personality_scores[trait]))
        
        self.logger.info(f"Music personality analysis completed: {personality_scores}")
        return personality_scores
    
    def _apply_audio_feature_analysis(self, scores: Dict[PersonalityTrait, float], features: Dict[str, float]):
        """Apply audio feature analysis to personality scores."""
        for feature, value in features.items():
            if feature in self.audio_feature_map:
                for trait, correlation in self.audio_feature_map[feature].items():
                    trait_enum = PersonalityTrait(trait)
                    # Apply correlation with audio feature value
                    adjustment = correlation * (value - 0.5) * 20  # Scale to ±10 points
                    scores[trait_enum] += adjustment
    
    def _apply_genre_analysis(self, scores: Dict[PersonalityTrait, float], genres: Dict[str, float]):
        """Apply genre analysis to personality scores."""
        for genre, percentage in genres.items():
            # Find closest matching genre in our mapping
            matched_genre = self._find_closest_genre(genre)
            if matched_genre and matched_genre in self.genre_personality_map:
                for trait, correlation in self.genre_personality_map[matched_genre].items():
                    trait_enum = PersonalityTrait(trait)
                    # Apply correlation weighted by genre percentage
                    adjustment = correlation * percentage * 30  # Scale adjustment
                    scores[trait_enum] += adjustment
    
    def _apply_listening_pattern_analysis(self, scores: Dict[PersonalityTrait, float], patterns: Dict[str, Any]):
        """Apply listening pattern analysis to personality scores."""
        # Diversity score affects openness
        diversity = patterns.get("diversity_score", 0.5)
        scores[PersonalityTrait.OPENNESS] += (diversity - 0.5) * 20
        
        # Track repetition affects conscientiousness
        repetition_data = patterns.get("track_repetition", {})
        if repetition_data:
            avg_repetition = sum(repetition_data.values()) / len(repetition_data)
            if avg_repetition > 2:  # High repetition
                scores[PersonalityTrait.CONSCIENTIOUSNESS] += 10
        
        # Listening time patterns affect extraversion
        listening_times = patterns.get("listening_times", [])
        if listening_times:
            evening_listening = sum(1 for hour in listening_times if 18 <= hour <= 23) / len(listening_times)
            if evening_listening > 0.5:  # More evening listening
                scores[PersonalityTrait.EXTRAVERSION] += 5
    
    def _apply_playlist_analysis(self, scores: Dict[PersonalityTrait, float], playlist_data: Dict[str, Any]):
        """Apply playlist analysis to personality scores."""
        total_playlists = playlist_data.get("total_playlists", 0)
        public_playlists = playlist_data.get("public_playlists", 0)
        collaborative_playlists = playlist_data.get("collaborative_playlists", 0)
        
        # Many playlists suggest conscientiousness
        if total_playlists > 10:
            scores[PersonalityTrait.CONSCIENTIOUSNESS] += 5
        
        # Public playlists suggest extraversion
        if total_playlists > 0:
            public_ratio = public_playlists / total_playlists
            scores[PersonalityTrait.EXTRAVERSION] += public_ratio * 10
        
        # Collaborative playlists suggest agreeableness
        if collaborative_playlists > 0:
            scores[PersonalityTrait.AGREEABLENESS] += min(collaborative_playlists * 3, 10)
    
    def _find_closest_genre(self, genre: str) -> Optional[str]:
        """Find the closest matching genre in our personality mapping."""
        genre_lower = genre.lower()
        
        # Direct match
        if genre_lower in self.genre_personality_map:
            return genre_lower
        
        # Partial match
        for mapped_genre in self.genre_personality_map:
            if mapped_genre in genre_lower or genre_lower in mapped_genre:
                return mapped_genre
        
        return None
    
    async def _get_trait_confidence(self, trait: PersonalityTrait, data: Dict[str, Any]) -> float:
        """Calculate confidence for specific traits based on music data."""
        base_confidence = 0.2
        
        # Increase confidence based on data richness
        top_tracks = len(data.get("top_tracks", []))
        audio_features = len(data.get("audio_features", {}))
        genres = len(data.get("genre_analysis", {}))
        
        # More data = higher confidence
        if top_tracks > 20:
            base_confidence += 0.1
        if audio_features > 5:
            base_confidence += 0.1
        if genres > 3:
            base_confidence += 0.1
        
        # Trait-specific confidence adjustments
        if trait == PersonalityTrait.OPENNESS and genres > 5:
            base_confidence += 0.15  # Genre diversity is strong indicator for openness
        elif trait == PersonalityTrait.EXTRAVERSION and audio_features:
            energy = data.get("audio_features", {}).get("energy", 0)
            if energy > 0.7 or energy < 0.3:  # Strong energy signal
                base_confidence += 0.1
        
        return min(0.3, base_confidence)  # Cap additional confidence
    
    def get_spotify_auth_url(self) -> str:
        """Get Spotify OAuth authorization URL."""
        try:
            scope = self.config.spotify.scope
            sp_oauth = SpotifyOAuth(
                client_id=self.config.spotify.client_id,
                client_secret=self.config.spotify.client_secret,
                redirect_uri=self.config.spotify.redirect_uri,
                scope=scope
            )
            return sp_oauth.get_authorize_url()
        except Exception as e:
            self.logger.error(f"Error generating Spotify auth URL: {e}")
            return ""
    
    async def handle_spotify_callback(self, code: str) -> bool:
        """Handle Spotify OAuth callback and initialize client."""
        try:
            sp_oauth = SpotifyOAuth(
                client_id=self.config.spotify.client_id,
                client_secret=self.config.spotify.client_secret,
                redirect_uri=self.config.spotify.redirect_uri,
                scope=self.config.spotify.scope
            )
            
            token_info = sp_oauth.get_access_token(code)
            if token_info:
                self.spotify_token = token_info["access_token"]
                self._initialize_spotify_client()
                self.logger.info("Spotify authentication successful")
                return True
        except Exception as e:
            self.logger.error(f"Error handling Spotify callback: {e}")
        
        return False