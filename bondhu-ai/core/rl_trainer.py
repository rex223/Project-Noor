"""
Reinforcement Learning Training System for Personality-Based Recommendations.

This module implements a Q-learning approach to optimize recommendation parameters
based on user feedback and personality traits.
"""

import logging
import json
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

from core.database.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class RecommendationState:
    """
    Represents the state space for RL.
    State = (personality_profile, content_type, mood, time_of_day)
    """
    
    def __init__(
        self,
        openness: float,
        conscientiousness: float,
        extraversion: float,
        agreeableness: float,
        neuroticism: float,
        content_type: str,
        mood: str = "neutral",
        time_of_day: str = "any"
    ):
        self.openness = self._discretize(openness)
        self.conscientiousness = self._discretize(conscientiousness)
        self.extraversion = self._discretize(extraversion)
        self.agreeableness = self._discretize(agreeableness)
        self.neuroticism = self._discretize(neuroticism)
        self.content_type = content_type
        self.mood = mood
        self.time_of_day = time_of_day
    
    @staticmethod
    def _discretize(value: float, bins: int = 5) -> int:
        """Discretize continuous personality scores into bins."""
        return min(int(value / (100.0 / bins)), bins - 1)
    
    def to_tuple(self) -> Tuple:
        """Convert state to hashable tuple for Q-table."""
        return (
            self.openness,
            self.conscientiousness,
            self.extraversion,
            self.agreeableness,
            self.neuroticism,
            self.content_type,
            self.mood,
            self.time_of_day
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism,
            "content_type": self.content_type,
            "mood": self.mood,
            "time_of_day": self.time_of_day
        }


class RecommendationAction:
    """
    Represents the action space for RL.
    Action = recommendation parameters (energy_level, genre_diversity, novelty_factor)
    """
    
    # Discrete action space
    ENERGY_LEVELS = ["low", "medium", "high"]
    DIVERSITY_LEVELS = ["focused", "balanced", "diverse"]
    NOVELTY_LEVELS = ["familiar", "mixed", "exploratory"]
    
    def __init__(self, energy: str, diversity: str, novelty: str):
        self.energy = energy
        self.diversity = diversity
        self.novelty = novelty
    
    def to_tuple(self) -> Tuple[str, str, str]:
        """Convert action to hashable tuple."""
        return (self.energy, self.diversity, self.novelty)
    
    def to_dict(self) -> Dict[str, str]:
        """Convert action to dictionary."""
        return {
            "energy": self.energy,
            "diversity": self.diversity,
            "novelty": self.novelty
        }
    
    @classmethod
    def all_actions(cls) -> List['RecommendationAction']:
        """Generate all possible actions."""
        actions = []
        for energy in cls.ENERGY_LEVELS:
            for diversity in cls.DIVERSITY_LEVELS:
                for novelty in cls.NOVELTY_LEVELS:
                    actions.append(cls(energy, diversity, novelty))
        return actions
    
    def to_recommendation_params(self) -> Dict[str, Any]:
        """
        Convert action to actual recommendation parameters.
        These are used by Spotify/YouTube APIs.
        """
        # Energy mapping
        energy_map = {
            "low": {"min_energy": 0.0, "max_energy": 0.4, "valence": 0.3},
            "medium": {"min_energy": 0.3, "max_energy": 0.7, "valence": 0.5},
            "high": {"min_energy": 0.6, "max_energy": 1.0, "valence": 0.7}
        }
        
        # Diversity mapping (how broad genre/category selection)
        diversity_map = {
            "focused": {"genre_count": 1, "exploration_rate": 0.1},
            "balanced": {"genre_count": 3, "exploration_rate": 0.3},
            "diverse": {"genre_count": 5, "exploration_rate": 0.5}
        }
        
        # Novelty mapping (prefer popular vs niche)
        novelty_map = {
            "familiar": {"popularity_min": 60, "popularity_max": 100},
            "mixed": {"popularity_min": 30, "popularity_max": 80},
            "exploratory": {"popularity_min": 0, "popularity_max": 50}
        }
        
        return {
            **energy_map[self.energy],
            **diversity_map[self.diversity],
            **novelty_map[self.novelty]
        }


class RewardFunction:
    """
    Calculates reward based on user interaction feedback.
    """
    
    @staticmethod
    def calculate_reward(interaction: Dict[str, Any]) -> float:
        """
        Calculate reward from user interaction.
        
        Reward components:
        - Like: +1.0
        - Dislike: -1.0
        - Complete: +0.5
        - Skip: -0.3
        - Share: +0.8
        - Completion rate: 0 to +0.5
        - Mood improvement: -0.5 to +0.5
        """
        reward = 0.0
        
        interaction_type = interaction.get("interaction_type")
        
        # Base rewards
        if interaction_type == "like":
            reward += 1.0
        elif interaction_type == "dislike":
            reward -= 1.0
        elif interaction_type == "complete":
            reward += 0.5
        elif interaction_type == "skip":
            reward -= 0.3
        elif interaction_type == "share":
            reward += 0.8
        elif interaction_type == "play" or interaction_type == "view":
            reward += 0.2  # Neutral engagement
        
        # Completion rate bonus
        completion_pct = interaction.get("completion_percentage", 0)
        if completion_pct is not None:
            reward += (completion_pct / 100.0) * 0.5
        
        # Mood change bonus
        mood_before = interaction.get("mood_before")
        mood_after = interaction.get("mood_after")
        
        if mood_before and mood_after:
            mood_improvement = RewardFunction._calculate_mood_improvement(
                mood_before, mood_after
            )
            reward += mood_improvement * 0.5
        
        # Duration bonus (for music/video)
        duration = interaction.get("duration_seconds", 0)
        if duration and duration > 0:
            # Bonus for engagement over 30 seconds
            if duration > 30:
                reward += min(0.3, duration / 600)  # Cap at 10 minutes
        
        return reward
    
    @staticmethod
    def _calculate_mood_improvement(mood_before: str, mood_after: str) -> float:
        """
        Calculate mood improvement score.
        Returns -1.0 to +1.0
        """
        mood_values = {
            "very_negative": -2,
            "negative": -1,
            "neutral": 0,
            "positive": 1,
            "very_positive": 2,
            "happy": 2,
            "sad": -2,
            "anxious": -1,
            "calm": 1,
            "energetic": 1,
            "relaxed": 1
        }
        
        before_val = mood_values.get(mood_before.lower(), 0)
        after_val = mood_values.get(mood_after.lower(), 0)
        
        improvement = after_val - before_val
        return max(-1.0, min(1.0, improvement / 2.0))


class QLearningAgent:
    """
    Q-Learning agent for optimizing recommendation parameters.
    """
    
    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        exploration_rate: float = 0.3,
        exploration_decay: float = 0.995,
        min_exploration_rate: float = 0.05
    ):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration_rate = min_exploration_rate
        
        # Q-table: {state: {action: Q-value}}
        self.q_table: Dict[Tuple, Dict[Tuple, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        
        # Visit counts for exploration bonus
        self.visit_counts: Dict[Tuple, Dict[Tuple, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        
        # All possible actions
        self.actions = RecommendationAction.all_actions()
        
        logger.info(f"Q-Learning agent initialized with {len(self.actions)} actions")
    
    def get_action(
        self,
        state: RecommendationState,
        explore: bool = True
    ) -> RecommendationAction:
        """
        Select action using epsilon-greedy policy.
        """
        state_tuple = state.to_tuple()
        
        # Exploration
        if explore and np.random.random() < self.exploration_rate:
            action = np.random.choice(self.actions)
            logger.debug(f"Exploring: selected random action {action.to_tuple()}")
            return action
        
        # Exploitation: choose best known action
        q_values = self.q_table[state_tuple]
        
        if not q_values:
            # No experience yet, return random action
            return np.random.choice(self.actions)
        
        # Select action with highest Q-value
        best_action_tuple = max(
            q_values.items(),
            key=lambda x: x[1]
        )[0]
        
        # Convert tuple back to action
        best_action = RecommendationAction(*best_action_tuple)
        logger.debug(f"Exploiting: selected best action {best_action_tuple} with Q={q_values[best_action_tuple]:.3f}")
        
        return best_action
    
    def update(
        self,
        state: RecommendationState,
        action: RecommendationAction,
        reward: float,
        next_state: Optional[RecommendationState] = None
    ):
        """
        Update Q-value using Q-learning update rule.
        Q(s,a) = Q(s,a) + α[r + γ·max_a'Q(s',a') - Q(s,a)]
        """
        state_tuple = state.to_tuple()
        action_tuple = action.to_tuple()
        
        # Current Q-value
        current_q = self.q_table[state_tuple][action_tuple]
        
        # Maximum Q-value for next state (if available)
        if next_state:
            next_state_tuple = next_state.to_tuple()
            next_q_values = self.q_table[next_state_tuple]
            max_next_q = max(next_q_values.values()) if next_q_values else 0.0
        else:
            max_next_q = 0.0
        
        # Q-learning update
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state_tuple][action_tuple] = new_q
        self.visit_counts[state_tuple][action_tuple] += 1
        
        logger.debug(
            f"Updated Q({state_tuple}, {action_tuple}): "
            f"{current_q:.3f} -> {new_q:.3f} (reward={reward:.3f})"
        )
        
        # Decay exploration rate
        self.exploration_rate = max(
            self.min_exploration_rate,
            self.exploration_rate * self.exploration_decay
        )
    
    def get_q_value(
        self,
        state: RecommendationState,
        action: RecommendationAction
    ) -> float:
        """Get Q-value for state-action pair."""
        return self.q_table[state.to_tuple()][action.to_tuple()]
    
    def get_state_value(self, state: RecommendationState) -> float:
        """Get state value (max Q-value)."""
        state_tuple = state.to_tuple()
        q_values = self.q_table[state_tuple]
        return max(q_values.values()) if q_values else 0.0
    
    def save(self, filepath: str):
        """Save Q-table to file."""
        data = {
            "q_table": {
                str(state): {str(action): q_val for action, q_val in actions.items()}
                for state, actions in self.q_table.items()
            },
            "visit_counts": {
                str(state): {str(action): count for action, count in actions.items()}
                for state, actions in self.visit_counts.items()
            },
            "exploration_rate": self.exploration_rate,
            "learning_rate": self.learning_rate,
            "discount_factor": self.discount_factor
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Q-table saved to {filepath}")
    
    def load(self, filepath: str):
        """Load Q-table from file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Reconstruct Q-table
            self.q_table = defaultdict(lambda: defaultdict(float))
            for state_str, actions in data["q_table"].items():
                state_tuple = eval(state_str)
                for action_str, q_val in actions.items():
                    action_tuple = eval(action_str)
                    self.q_table[state_tuple][action_tuple] = q_val
            
            # Reconstruct visit counts
            self.visit_counts = defaultdict(lambda: defaultdict(int))
            for state_str, actions in data["visit_counts"].items():
                state_tuple = eval(state_str)
                for action_str, count in actions.items():
                    action_tuple = eval(action_str)
                    self.visit_counts[state_tuple][action_tuple] = count
            
            self.exploration_rate = data["exploration_rate"]
            self.learning_rate = data["learning_rate"]
            self.discount_factor = data["discount_factor"]
            
            logger.info(f"Q-table loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load Q-table: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get training statistics."""
        total_states = len(self.q_table)
        total_state_actions = sum(len(actions) for actions in self.q_table.values())
        
        all_q_values = [
            q for actions in self.q_table.values() for q in actions.values()
        ]
        
        return {
            "total_states": total_states,
            "total_state_actions": total_state_actions,
            "exploration_rate": self.exploration_rate,
            "avg_q_value": np.mean(all_q_values) if all_q_values else 0.0,
            "max_q_value": max(all_q_values) if all_q_values else 0.0,
            "min_q_value": min(all_q_values) if all_q_values else 0.0
        }
