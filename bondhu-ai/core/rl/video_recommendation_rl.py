"""
Reinforcement Learning system for video recommendation feedback processing.
Implements deep Q-learning for improving video suggestions based on user interactions.
"""

import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
import asyncio

from core.database.models import PersonalityTrait  # Use Enum for iteration


class VideoRecommendationRL:
    """
    Reinforcement Learning system for video recommendations.
    Uses Q-learning to improve suggestions based on user feedback.
    """
    
    def __init__(self, user_id: str, learning_rate: float = 0.1, 
                 discount_factor: float = 0.95, epsilon: float = 0.1):
        """
        Initialize RL system for video recommendations.
        
        Args:
            user_id: User identifier
            learning_rate: Learning rate for Q-learning
            discount_factor: Discount factor for future rewards
            epsilon: Exploration rate for epsilon-greedy policy
        """
        self.user_id = user_id
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        
        self.logger = logging.getLogger("bondhu.video_rl")
        
        # Q-table for state-action values
        # State: (personality_profile, video_features)
        # Action: (recommend, not_recommend)
        self.q_table = {}
        
        # Experience replay buffer
        self.experience_buffer = deque(maxlen=10000)
        
        # Reward mapping
        self.reward_map = {
            'like': 1.0,
            'dislike': -1.0,
            'watch': 0.5,
            'skip': -0.3,
            'share': 1.5,
            'comment': 1.2,
            'subscribe': 2.0
        }
        
        # Feature extractors
        self.personality_features = [trait.value for trait in PersonalityTrait]
        self.video_features = [
            'duration_normalized', 'engagement_score', 'category_match',
            'theme_match', 'freshness_score', 'quality_score'
        ]
        
        # Training statistics
        self.training_episodes = 0
        self.total_reward = 0.0
        self.last_update = datetime.now()

    async def process_feedback(self, video_data: Dict[str, Any], 
                             personality_profile: Dict[PersonalityTrait, float],
                             feedback_type: str, 
                             additional_data: Optional[Dict[str, Any]] = None) -> float:
        """
        Process user feedback and update Q-values.
        
        Args:
            video_data: Video metadata and features
            personality_profile: User's personality scores
            feedback_type: Type of feedback ('like', 'dislike', etc.)
            additional_data: Additional feedback context
            
        Returns:
            Updated Q-value for the state-action pair
        """
        try:
            # Extract state features
            state = self._extract_state_features(video_data, personality_profile)
            
            # Calculate reward
            reward = self._calculate_reward(feedback_type, additional_data)
            
            # Update Q-value
            updated_q_value = await self._update_q_value(state, reward)
            
            # Store experience for replay learning
            experience = {
                'state': state,
                'action': 'recommend',  # We recommended this video
                'reward': reward,
                'next_state': None,  # Will be filled by next interaction
                'timestamp': datetime.now(),
                'feedback_type': feedback_type
            }
            
            self.experience_buffer.append(experience)
            
            # Update training statistics
            self.total_reward += reward
            self.training_episodes += 1
            
            # Periodic batch learning
            if len(self.experience_buffer) >= 32 and self.training_episodes % 10 == 0:
                await self._batch_learning()
            
            self.logger.info(f"Processed {feedback_type} feedback with reward {reward:.2f}")
            return updated_q_value
            
        except Exception as e:
            self.logger.error(f"Error processing feedback: {e}")
            return 0.0

    async def get_recommendation_scores(self, candidate_videos: List[Dict[str, Any]],
                                     personality_profile: Dict[PersonalityTrait, float]) -> List[Tuple[Dict[str, Any], float]]:
        """
        Get RL-enhanced recommendation scores for candidate videos.
        
        Args:
            candidate_videos: List of candidate videos
            personality_profile: User's personality profile
            
        Returns:
            List of (video, rl_score) tuples
        """
        try:
            scored_videos = []
            
            for video in candidate_videos:
                # Extract state features
                state = self._extract_state_features(video, personality_profile)
                
                # Get Q-value for recommending this video
                q_value = self._get_q_value(state, 'recommend')
                
                # Apply epsilon-greedy exploration
                if np.random.random() < self.epsilon:
                    # Exploration: add some randomness
                    exploration_bonus = np.random.uniform(-0.1, 0.1)
                    rl_score = q_value + exploration_bonus
                else:
                    # Exploitation: use learned values
                    rl_score = q_value
                
                scored_videos.append((video, rl_score))
            
            # Sort by RL score
            scored_videos.sort(key=lambda x: x[1], reverse=True)
            
            return scored_videos
            
        except Exception as e:
            self.logger.error(f"Error getting recommendation scores: {e}")
            return [(video, 0.0) for video in candidate_videos]

    def _extract_state_features(self, video_data: Dict[str, Any], 
                               personality_profile: Dict[PersonalityTrait, float]) -> str:
        """Extract state features for Q-learning."""
        try:
            # Personality features (discretized)
            personality_state = []
            for trait in PersonalityTrait:
                score = personality_profile.get(trait, 0.5)
                # Discretize into low, medium, high
                if score < 0.33:
                    personality_state.append(f"{trait.value}_low")
                elif score < 0.67:
                    personality_state.append(f"{trait.value}_med")
                else:
                    personality_state.append(f"{trait.value}_high")
            
            # Video features (discretized)
            video_state = []
            
            # Duration
            duration = video_data.get('duration_seconds', 0)
            if duration < 300:  # < 5 minutes
                video_state.append("duration_short")
            elif duration < 1200:  # < 20 minutes
                video_state.append("duration_medium")
            else:
                video_state.append("duration_long")
            
            # Engagement score
            engagement = video_data.get('engagement_score', 0.0)
            if engagement < 0.3:
                video_state.append("engagement_low")
            elif engagement < 0.7:
                video_state.append("engagement_med")
            else:
                video_state.append("engagement_high")
            
            # Category
            category = video_data.get('category_name', 'Unknown')
            video_state.append(f"category_{category.replace(' ', '_').lower()}")
            
            # Content themes
            themes = video_data.get('content_themes', [])
            if themes:
                primary_theme = themes[0]  # Use primary theme
                video_state.append(f"theme_{primary_theme}")
            else:
                video_state.append("theme_none")
            
            # Combine into state string
            state_features = personality_state + video_state
            state = "|".join(sorted(state_features))
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error extracting state features: {e}")
            return "unknown_state"

    def _calculate_reward(self, feedback_type: str, 
                         additional_data: Optional[Dict[str, Any]] = None) -> float:
        """Calculate reward based on feedback type and additional context."""
        base_reward = self.reward_map.get(feedback_type, 0.0)
        
        # Apply modifiers based on additional data
        if additional_data:
            # Watch time bonus/penalty
            if 'watch_time' in additional_data and 'duration' in additional_data:
                watch_ratio = additional_data['watch_time'] / additional_data['duration']
                if watch_ratio > 0.8:
                    base_reward += 0.3  # Bonus for high completion
                elif watch_ratio < 0.2:
                    base_reward -= 0.2  # Penalty for early skip
            
            # Engagement modifiers
            if 'interactions' in additional_data:
                interactions = additional_data['interactions']
                if 'pause' in interactions:
                    base_reward += 0.1  # Engaged viewing
                if 'rewind' in interactions:
                    base_reward += 0.2  # High engagement
            
            # Time-based modifiers
            if 'time_to_click' in additional_data:
                time_to_click = additional_data['time_to_click']
                if time_to_click < 2.0:  # Quick positive response
                    base_reward += 0.1
        
        return base_reward

    def _get_q_value(self, state: str, action: str) -> float:
        """Get Q-value for state-action pair."""
        key = f"{state}_{action}"
        return self.q_table.get(key, 0.0)

    def _set_q_value(self, state: str, action: str, value: float) -> None:
        """Set Q-value for state-action pair."""
        key = f"{state}_{action}"
        self.q_table[key] = value

    async def _update_q_value(self, state: str, reward: float) -> float:
        """Update Q-value using Q-learning update rule."""
        try:
            action = 'recommend'
            current_q = self._get_q_value(state, action)
            
            # Q-learning update: Q(s,a) = Q(s,a) + α[r + γ*max(Q(s',a')) - Q(s,a)]
            # Since we don't have next state yet, use simplified update
            new_q = current_q + self.learning_rate * (reward - current_q)
            
            self._set_q_value(state, action, new_q)
            
            return new_q
            
        except Exception as e:
            self.logger.error(f"Error updating Q-value: {e}")
            return 0.0

    async def _batch_learning(self) -> None:
        """Perform batch learning from experience replay buffer."""
        try:
            if len(self.experience_buffer) < 16:
                return
            
            # Sample random batch from experience buffer
            batch_size = min(32, len(self.experience_buffer))
            batch_indices = np.random.choice(len(self.experience_buffer), batch_size, replace=False)
            batch = [self.experience_buffer[i] for i in batch_indices]
            
            # Process each experience in batch
            for experience in batch:
                state = experience['state']
                action = experience['action']
                reward = experience['reward']
                
                # Update Q-value
                current_q = self._get_q_value(state, action)
                new_q = current_q + self.learning_rate * (reward - current_q)
                self._set_q_value(state, action, new_q)
            
            # Decay exploration rate
            self.epsilon = max(0.01, self.epsilon * 0.995)
            
            self.logger.info(f"Completed batch learning with {batch_size} experiences")
            
        except Exception as e:
            self.logger.error(f"Error in batch learning: {e}")

    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get learning statistics and metrics."""
        return {
            'training_episodes': self.training_episodes,
            'total_reward': self.total_reward,
            'average_reward': self.total_reward / max(1, self.training_episodes),
            'epsilon': self.epsilon,
            'q_table_size': len(self.q_table),
            'experience_buffer_size': len(self.experience_buffer),
            'last_update': self.last_update.isoformat(),
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor
        }

    async def save_model(self, filepath: str) -> bool:
        """Save Q-table and learning state to file."""
        try:
            import json
            
            model_data = {
                'user_id': self.user_id,
                'q_table': self.q_table,
                'learning_rate': self.learning_rate,
                'discount_factor': self.discount_factor,
                'epsilon': self.epsilon,
                'training_episodes': self.training_episodes,
                'total_reward': self.total_reward,
                'last_update': self.last_update.isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(model_data, f, indent=2)
            
            self.logger.info(f"Saved RL model to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
            return False

    async def load_model(self, filepath: str) -> bool:
        """Load Q-table and learning state from file."""
        try:
            import json
            
            with open(filepath, 'r') as f:
                model_data = json.load(f)
            
            self.q_table = model_data.get('q_table', {})
            self.learning_rate = model_data.get('learning_rate', self.learning_rate)
            self.discount_factor = model_data.get('discount_factor', self.discount_factor)
            self.epsilon = model_data.get('epsilon', self.epsilon)
            self.training_episodes = model_data.get('training_episodes', 0)
            self.total_reward = model_data.get('total_reward', 0.0)
            
            last_update_str = model_data.get('last_update')
            if last_update_str:
                self.last_update = datetime.fromisoformat(last_update_str)
            
            self.logger.info(f"Loaded RL model from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            return False