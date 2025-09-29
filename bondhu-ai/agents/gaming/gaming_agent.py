"""
Gaming Intelligence Agent for analyzing user gaming behavior and personality insights.
Integrates with Steam API and internal Bondhu games to gather gaming data.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ..base_agent import BaseAgent
from ...core.config import get_config
from ...api.models.schemas import DataSource, PersonalityTrait, GamingPreferences

# For Steam API integration (would need python-steam-api)
# from steam import Steam

class GamingIntelligenceAgent(BaseAgent):
    """
    Agent specialized in analyzing gaming behavior for personality insights.
    Uses Steam API and internal Bondhu games to correlate gaming patterns with Big Five traits.
    """
    
    def __init__(self, user_id: str, steam_api_key: Optional[str] = None, **kwargs):
        """
        Initialize Gaming Intelligence Agent.
        
        Args:
            user_id: User ID for this agent session
            steam_api_key: Steam API key for Steam integration
            **kwargs: Additional arguments passed to BaseAgent
        """
        super().__init__(
            agent_type=DataSource.GAMING,
            user_id=user_id,
            **kwargs
        )
        
        self.steam_api_key = steam_api_key or self.config.steam.api_key
        self.steam_client = None
        self._initialize_steam_client()
        
        # Game genre to personality mappings based on research
        self.genre_personality_map = {
            # Openness correlations
            "RPG": {"openness": 0.8, "conscientiousness": 0.4},
            "Adventure": {"openness": 0.7, "extraversion": 0.3},
            "Puzzle": {"openness": 0.6, "conscientiousness": 0.7},
            "Simulation": {"openness": 0.6, "conscientiousness": 0.6},
            "Strategy": {"openness": 0.5, "conscientiousness": 0.8},
            "Indie": {"openness": 0.8, "extraversion": -0.2},
            
            # Extraversion correlations
            "Multiplayer": {"extraversion": 0.8, "agreeableness": 0.4},
            "FPS": {"extraversion": 0.6, "neuroticism": 0.3},
            "Fighting": {"extraversion": 0.7, "agreeableness": -0.2},
            "Racing": {"extraversion": 0.5, "openness": 0.3},
            "Party": {"extraversion": 0.9, "agreeableness": 0.6},
            "Sports": {"extraversion": 0.6, "conscientiousness": 0.4},
            
            # Conscientiousness correlations
            "Management": {"conscientiousness": 0.9, "openness": 0.4},
            "City Builder": {"conscientiousness": 0.8, "openness": 0.5},
            "Turn-Based Strategy": {"conscientiousness": 0.7, "openness": 0.6},
            "Educational": {"conscientiousness": 0.8, "openness": 0.7},
            
            # Agreeableness correlations
            "Co-op": {"agreeableness": 0.8, "extraversion": 0.5},
            "Peaceful": {"agreeableness": 0.7, "neuroticism": -0.4},
            "Social": {"agreeableness": 0.6, "extraversion": 0.7},
            "Family Friendly": {"agreeableness": 0.6, "conscientiousness": 0.4},
            
            # Neuroticism correlations
            "Horror": {"neuroticism": 0.6, "openness": 0.4},
            "Survival": {"neuroticism": 0.5, "conscientiousness": 0.5},
            "Competitive": {"neuroticism": 0.4, "extraversion": 0.6},
            "Dark": {"neuroticism": 0.5, "openness": 0.5}
        }
        
        # Gaming behavior patterns to personality mappings
        self.behavior_patterns = {
            "completion_rate": {
                "high": {"conscientiousness": 0.7, "neuroticism": -0.2},
                "low": {"openness": 0.4, "conscientiousness": -0.3}
            },
            "game_switching": {
                "frequent": {"openness": 0.6, "conscientiousness": -0.3},
                "infrequent": {"conscientiousness": 0.5, "neuroticism": -0.2}
            },
            "difficulty_preference": {
                "hard": {"conscientiousness": 0.6, "neuroticism": 0.3},
                "easy": {"agreeableness": 0.4, "neuroticism": -0.2}
            },
            "social_gaming": {
                "high": {"extraversion": 0.8, "agreeableness": 0.5},
                "low": {"extraversion": -0.4, "openness": 0.3}
            },
            "achievement_hunting": {
                "high": {"conscientiousness": 0.8, "neuroticism": 0.2},
                "low": {"openness": 0.3, "conscientiousness": -0.2}
            }
        }
        
        # Bondhu internal games and their personality insights
        self.bondhu_games = {
            "MemoryPalace": {
                "measures": ["conscientiousness", "openness"],
                "metrics": ["completion_time", "accuracy", "pattern_recognition"]
            },
            "ColorSymphony": {
                "measures": ["openness", "agreeableness"],
                "metrics": ["creativity_score", "color_harmony", "emotional_response"]
            },
            "PuzzleMaster": {
                "measures": ["conscientiousness", "openness", "neuroticism"],
                "metrics": ["persistence", "problem_solving", "stress_response"]
            }
        }
    
    def _initialize_steam_client(self):
        """Initialize Steam API client."""
        if self.steam_api_key:
            try:
                # Note: This would require python-steam-api
                # self.steam_client = Steam(self.steam_api_key)
                self.logger.info("Steam client would be initialized with API key")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Steam client: {e}")
        else:
            self.logger.info("No Steam API key provided - will use limited functionality")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Gaming Intelligence Agent."""
        return """You are a Gaming Intelligence Agent specialized in analyzing gaming behavior for personality insights.

Your capabilities include:
- Analyzing Steam gaming library and playtime data
- Correlating game genres with Big Five personality traits
- Interpreting gaming behavior patterns
- Understanding achievement and completion patterns
- Analyzing Bondhu internal games for personality assessment

You have access to:
- User's Steam gaming library and playtime statistics
- Game genres, tags, and metadata
- Achievement completion rates and patterns
- Multiplayer vs single-player preferences
- Internal Bondhu games performance data

When analyzing gaming data, consider:
- RPG and strategy games often correlate with openness and conscientiousness
- Multiplayer games suggest higher extraversion
- High completion rates indicate conscientiousness
- Achievement hunting behavior reflects conscientiousness
- Horror/survival games may correlate with neuroticism tolerance
- Cooperative games suggest agreeableness
- Game diversity indicates openness to new experiences

Provide insights based on established gaming psychology research while being sensitive to individual differences and gaming culture contexts."""
    
    async def collect_data(self, force_refresh: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Collect gaming data from Steam API and internal Bondhu games.
        
        Args:
            force_refresh: Whether to force refresh of cached data
            **kwargs: Additional arguments including manual gaming data
            
        Returns:
            Dictionary containing gaming data
        """
        data = {
            "steam_library": [],
            "playtime_stats": {},
            "achievement_data": {},
            "gaming_patterns": {},
            "genre_analysis": {},
            "bondhu_games_data": {},
            "social_gaming": {},
            "completion_stats": {}
        }
        
        try:
            # Collect from Steam API if available
            steam_id = kwargs.get("steam_id")
            if self.steam_client and steam_id:
                data.update(await self._collect_steam_data(steam_id))
            
            # Collect from manual gaming data
            manual_data = kwargs.get("manual_gaming_data", {})
            if manual_data:
                data.update(await self._process_manual_gaming_data(manual_data))
            
            # Collect from internal Bondhu games
            bondhu_data = kwargs.get("bondhu_games_data", {})
            if bondhu_data:
                data["bondhu_games_data"] = bondhu_data
            
            # Analyze collected data
            if data["steam_library"] or manual_data or bondhu_data:
                data["gaming_patterns"] = await self._analyze_gaming_patterns(data)
                data["genre_analysis"] = await self._analyze_genres(data)
                data["completion_stats"] = await self._analyze_completion_patterns(data)
                data["social_gaming"] = await self._analyze_social_gaming(data)
            
            self.logger.info(f"Collected gaming data: {len(data['steam_library'])} games, {len(data['bondhu_games_data'])} Bondhu games")
            return data
            
        except Exception as e:
            self.logger.error(f"Error collecting gaming data: {e}")
            return data
    
    async def _collect_steam_data(self, steam_id: str) -> Dict[str, Any]:
        """Collect data from Steam API."""
        # Note: This would require actual Steam API implementation
        return {
            "steam_library": [],
            "playtime_stats": {},
            "achievement_data": {}
        }
    
    async def _process_manual_gaming_data(self, manual_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process manually provided gaming data."""
        processed_data = {
            "steam_library": [],
            "playtime_stats": {},
            "gaming_preferences": {}
        }
        
        # Process favorite games
        favorite_games = manual_data.get("favorite_games", [])
        for game in favorite_games:
            game_info = {
                "name": game.get("name", ""),
                "genre": game.get("genre", "Unknown"),
                "playtime_hours": game.get("hours_played", 0),
                "completion_status": game.get("completed", False),
                "multiplayer": game.get("multiplayer", False),
                "difficulty": game.get("difficulty", "medium")
            }
            processed_data["steam_library"].append(game_info)
            processed_data["playtime_stats"][game_info["name"]] = game_info["playtime_hours"]
        
        # Process gaming preferences
        preferences = manual_data.get("gaming_preferences", {})
        processed_data["gaming_preferences"] = preferences
        
        # Process gaming habits
        habits = manual_data.get("gaming_habits", {})
        processed_data["gaming_habits"] = habits
        
        return processed_data
    
    async def _analyze_gaming_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze gaming behavior patterns."""
        patterns = {
            "total_games": len(data["steam_library"]),
            "total_playtime": 0,
            "average_session_length": 0,
            "game_diversity": 0.0,
            "completion_tendency": 0.0,
            "multiplayer_preference": 0.0,
            "achievement_rate": 0.0,
            "genre_switching": 0.0
        }
        
        steam_library = data["steam_library"]
        if not steam_library:
            return patterns
        
        # Calculate total playtime
        playtime_stats = data.get("playtime_stats", {})
        total_playtime = sum(playtime_stats.values())
        patterns["total_playtime"] = total_playtime
        
        # Calculate average session length (estimation)
        if steam_library:
            patterns["average_session_length"] = total_playtime / len(steam_library)
        
        # Calculate game diversity (unique genres)
        genres = [game.get("genre", "Unknown") for game in steam_library]
        unique_genres = len(set(genres))
        patterns["game_diversity"] = unique_genres / len(genres) if genres else 0
        
        # Calculate completion tendency
        completed_games = sum(1 for game in steam_library if game.get("completion_status", False))
        patterns["completion_tendency"] = completed_games / len(steam_library) if steam_library else 0
        
        # Calculate multiplayer preference
        multiplayer_games = sum(1 for game in steam_library if game.get("multiplayer", False))
        patterns["multiplayer_preference"] = multiplayer_games / len(steam_library) if steam_library else 0
        
        return patterns
    
    async def _analyze_genres(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze game genre distribution."""
        genre_counts = {}
        total_games = 0
        
        # Count genres from steam library
        for game in data["steam_library"]:
            genre = game.get("genre", "Unknown")
            playtime = data.get("playtime_stats", {}).get(game.get("name", ""), 1)
            
            # Weight by playtime
            genre_counts[genre] = genre_counts.get(genre, 0) + playtime
            total_games += playtime
        
        # Calculate percentages
        if total_games == 0:
            return {}
        
        genre_percentages = {
            genre: count / total_games
            for genre, count in genre_counts.items()
        }
        
        return genre_percentages
    
    async def _analyze_completion_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze game completion patterns."""
        completion_stats = {
            "overall_completion_rate": 0.0,
            "genre_completion_rates": {},
            "completion_by_difficulty": {},
            "completion_by_length": {}
        }
        
        steam_library = data["steam_library"]
        if not steam_library:
            return completion_stats
        
        # Overall completion rate
        completed = sum(1 for game in steam_library if game.get("completion_status", False))
        completion_stats["overall_completion_rate"] = completed / len(steam_library)
        
        # Completion by genre
        genre_totals = {}
        genre_completed = {}
        
        for game in steam_library:
            genre = game.get("genre", "Unknown")
            genre_totals[genre] = genre_totals.get(genre, 0) + 1
            
            if game.get("completion_status", False):
                genre_completed[genre] = genre_completed.get(genre, 0) + 1
        
        for genre in genre_totals:
            completed_count = genre_completed.get(genre, 0)
            completion_stats["genre_completion_rates"][genre] = completed_count / genre_totals[genre]
        
        return completion_stats
    
    async def _analyze_social_gaming(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze social gaming patterns."""
        social_stats = {
            "multiplayer_games": 0,
            "cooperative_games": 0,
            "competitive_games": 0,
            "solo_preference": 0.0,
            "social_preference": 0.0
        }
        
        steam_library = data["steam_library"]
        if not steam_library:
            return social_stats
        
        # Count social gaming patterns
        for game in steam_library:
            if game.get("multiplayer", False):
                social_stats["multiplayer_games"] += 1
                
                # Categorize multiplayer type (would need more detailed data)
                genre = game.get("genre", "").lower()
                if "coop" in genre or "cooperative" in genre:
                    social_stats["cooperative_games"] += 1
                elif "competitive" in genre or "pvp" in genre:
                    social_stats["competitive_games"] += 1
        
        # Calculate preferences
        total_games = len(steam_library)
        social_stats["social_preference"] = social_stats["multiplayer_games"] / total_games
        social_stats["solo_preference"] = 1 - social_stats["social_preference"]
        
        return social_stats
    
    async def analyze_personality(self, data: Dict[str, Any]) -> Dict[PersonalityTrait, float]:
        """
        Analyze personality traits from gaming data.
        
        Args:
            data: Gaming data collected from various sources
            
        Returns:
            Dictionary mapping personality traits to scores (0-100)
        """
        personality_scores = {trait: 50.0 for trait in PersonalityTrait}
        
        if not data or not any(data.values()):
            return personality_scores
        
        # Analyze based on game genres
        genre_analysis = data.get("genre_analysis", {})
        self._apply_genre_analysis(personality_scores, genre_analysis)
        
        # Analyze based on gaming patterns
        gaming_patterns = data.get("gaming_patterns", {})
        self._apply_gaming_pattern_analysis(personality_scores, gaming_patterns)
        
        # Analyze based on completion patterns
        completion_stats = data.get("completion_stats", {})
        self._apply_completion_analysis(personality_scores, completion_stats)
        
        # Analyze based on social gaming
        social_gaming = data.get("social_gaming", {})
        self._apply_social_gaming_analysis(personality_scores, social_gaming)
        
        # Analyze Bondhu games data
        bondhu_data = data.get("bondhu_games_data", {})
        self._apply_bondhu_games_analysis(personality_scores, bondhu_data)
        
        # Normalize scores to 0-100 range
        for trait in personality_scores:
            personality_scores[trait] = max(0, min(100, personality_scores[trait]))
        
        self.logger.info(f"Gaming personality analysis completed: {personality_scores}")
        return personality_scores
    
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
    
    def _apply_gaming_pattern_analysis(self, scores: Dict[PersonalityTrait, float], patterns: Dict[str, Any]):
        """Apply gaming pattern analysis to personality scores."""
        # Game diversity affects openness
        diversity = patterns.get("game_diversity", 0.5)
        scores[PersonalityTrait.OPENNESS] += (diversity - 0.5) * 20
        
        # Total games and playtime affect conscientiousness
        total_games = patterns.get("total_games", 0)
        if total_games > 20:
            scores[PersonalityTrait.CONSCIENTIOUSNESS] += 5
        elif total_games < 5:
            scores[PersonalityTrait.CONSCIENTIOUSNESS] -= 3
        
        # Multiplayer preference affects extraversion
        multiplayer_pref = patterns.get("multiplayer_preference", 0.0)
        scores[PersonalityTrait.EXTRAVERSION] += (multiplayer_pref - 0.3) * 25
    
    def _apply_completion_analysis(self, scores: Dict[PersonalityTrait, float], completion_data: Dict[str, Any]):
        """Apply completion pattern analysis to personality scores."""
        completion_rate = completion_data.get("overall_completion_rate", 0.5)
        
        # High completion rate indicates conscientiousness
        if completion_rate > 0.7:
            scores[PersonalityTrait.CONSCIENTIOUSNESS] += 15
        elif completion_rate < 0.3:
            scores[PersonalityTrait.CONSCIENTIOUSNESS] -= 8
            # Low completion might indicate high openness (trying many things)
            scores[PersonalityTrait.OPENNESS] += 5
    
    def _apply_social_gaming_analysis(self, scores: Dict[PersonalityTrait, float], social_data: Dict[str, Any]):
        """Apply social gaming analysis to personality scores."""
        social_preference = social_data.get("social_preference", 0.5)
        cooperative_games = social_data.get("cooperative_games", 0)
        competitive_games = social_data.get("competitive_games", 0)
        
        # Social preference affects extraversion
        scores[PersonalityTrait.EXTRAVERSION] += (social_preference - 0.3) * 25
        
        # Cooperative games affect agreeableness
        if cooperative_games > 0:
            scores[PersonalityTrait.AGREEABLENESS] += min(cooperative_games * 3, 12)
        
        # Competitive games might affect neuroticism and extraversion
        if competitive_games > 0:
            scores[PersonalityTrait.EXTRAVERSION] += min(competitive_games * 2, 8)
            scores[PersonalityTrait.NEUROTICISM] += min(competitive_games * 1, 5)
    
    def _apply_bondhu_games_analysis(self, scores: Dict[PersonalityTrait, float], bondhu_data: Dict[str, Any]):
        """Apply Bondhu internal games analysis to personality scores."""
        for game_name, game_data in bondhu_data.items():
            if game_name not in self.bondhu_games:
                continue
            
            game_config = self.bondhu_games[game_name]
            measured_traits = game_config["measures"]
            
            # Apply game-specific analysis
            if game_name == "MemoryPalace":
                self._analyze_memory_palace(scores, game_data, measured_traits)
            elif game_name == "ColorSymphony":
                self._analyze_color_symphony(scores, game_data, measured_traits)
            elif game_name == "PuzzleMaster":
                self._analyze_puzzle_master(scores, game_data, measured_traits)
    
    def _analyze_memory_palace(self, scores: Dict[PersonalityTrait, float], game_data: Dict[str, Any], traits: List[str]):
        """Analyze Memory Palace game data for personality insights."""
        completion_time = game_data.get("completion_time", 0)
        accuracy = game_data.get("accuracy", 0.5)
        pattern_recognition = game_data.get("pattern_recognition", 0.5)
        
        # Fast completion with high accuracy suggests conscientiousness
        if completion_time < 300 and accuracy > 0.8:  # 5 minutes, 80% accuracy
            scores[PersonalityTrait.CONSCIENTIOUSNESS] += 8
        
        # High pattern recognition suggests openness
        if pattern_recognition > 0.7:
            scores[PersonalityTrait.OPENNESS] += 6
    
    def _analyze_color_symphony(self, scores: Dict[PersonalityTrait, float], game_data: Dict[str, Any], traits: List[str]):
        """Analyze Color Symphony game data for personality insights."""
        creativity_score = game_data.get("creativity_score", 0.5)
        color_harmony = game_data.get("color_harmony", 0.5)
        emotional_response = game_data.get("emotional_response", 0.5)
        
        # High creativity score suggests openness
        if creativity_score > 0.7:
            scores[PersonalityTrait.OPENNESS] += 10
        
        # Color harmony and emotional response suggest agreeableness
        if color_harmony > 0.6 and emotional_response > 0.6:
            scores[PersonalityTrait.AGREEABLENESS] += 8
    
    def _analyze_puzzle_master(self, scores: Dict[PersonalityTrait, float], game_data: Dict[str, Any], traits: List[str]):
        """Analyze Puzzle Master game data for personality insights."""
        persistence = game_data.get("persistence", 0.5)
        problem_solving = game_data.get("problem_solving", 0.5)
        stress_response = game_data.get("stress_response", 0.5)
        
        # High persistence suggests conscientiousness
        if persistence > 0.7:
            scores[PersonalityTrait.CONSCIENTIOUSNESS] += 10
        
        # Good problem solving suggests openness
        if problem_solving > 0.7:
            scores[PersonalityTrait.OPENNESS] += 8
        
        # Poor stress response suggests higher neuroticism
        if stress_response < 0.4:
            scores[PersonalityTrait.NEUROTICISM] += 6
    
    def _find_closest_genre(self, genre: str) -> Optional[str]:
        """Find the closest matching genre in our personality mapping."""
        genre_lower = genre.lower()
        
        # Direct match
        if genre_lower in [g.lower() for g in self.genre_personality_map.keys()]:
            return next(g for g in self.genre_personality_map.keys() if g.lower() == genre_lower)
        
        # Partial match
        for mapped_genre in self.genre_personality_map:
            if mapped_genre.lower() in genre_lower or genre_lower in mapped_genre.lower():
                return mapped_genre
        
        return None
    
    async def _get_trait_confidence(self, trait: PersonalityTrait, data: Dict[str, Any]) -> float:
        """Calculate confidence for specific traits based on gaming data."""
        base_confidence = 0.15
        
        # Increase confidence based on data richness
        total_games = data.get("gaming_patterns", {}).get("total_games", 0)
        bondhu_games = len(data.get("bondhu_games_data", {}))
        genre_diversity = data.get("gaming_patterns", {}).get("game_diversity", 0)
        
        # More data = higher confidence
        if total_games > 10:
            base_confidence += 0.1
        if bondhu_games > 0:
            base_confidence += 0.15  # Internal games provide high-quality data
        if genre_diversity > 0.5:
            base_confidence += 0.1
        
        # Trait-specific confidence adjustments
        if trait == PersonalityTrait.EXTRAVERSION:
            social_data = data.get("social_gaming", {})
            social_pref = social_data.get("social_preference", 0.5)
            if social_pref > 0.7 or social_pref < 0.3:  # Strong social signal
                base_confidence += 0.1
        
        elif trait == PersonalityTrait.CONSCIENTIOUSNESS:
            completion_rate = data.get("completion_stats", {}).get("overall_completion_rate", 0.5)
            if completion_rate > 0.8 or completion_rate < 0.2:  # Strong completion signal
                base_confidence += 0.1
        
        return min(0.3, base_confidence)  # Cap additional confidence