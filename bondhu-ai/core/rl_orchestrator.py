"""
RL Training Orchestrator for Recommendation System.

Coordinates the training loop, data collection, and model persistence.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os

from core.rl_trainer import (
    QLearningAgent,
    RecommendationState,
    RecommendationAction,
    RewardFunction
)
from core.database.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class RLTrainingOrchestrator:
    """
    Orchestrates the RL training process for recommendation optimization.
    """
    
    def __init__(self, model_path: str = "models/q_table.json"):
        self.agent = QLearningAgent(
            learning_rate=0.1,
            discount_factor=0.95,
            exploration_rate=0.3,
            exploration_decay=0.995,
            min_exploration_rate=0.05
        )
        self.model_path = model_path
        self.reward_function = RewardFunction()
        
        # Load existing model if available
        if os.path.exists(model_path):
            try:
                self.agent.load(model_path)
                logger.info(f"Loaded existing Q-table from {model_path}")
            except Exception as e:
                logger.warning(f"Failed to load Q-table: {e}. Starting fresh.")
        
        logger.info("RL Training Orchestrator initialized")
    
    async def train_from_interactions(
        self,
        days_back: int = 7,
        min_interactions_per_user: int = 5
    ) -> Dict[str, Any]:
        """
        Train the RL agent from historical user interactions.
        
        Args:
            days_back: Number of days of historical data to use
            min_interactions_per_user: Minimum interactions required per user
            
        Returns:
            Training statistics
        """
        logger.info(f"Starting RL training from last {days_back} days of interactions...")
        
        supabase = get_supabase_client()
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        # Fetch interactions with personality context
        interactions_query = supabase.table("entertainment_interactions")\
            .select("*, user_id")\
            .gte("timestamp", cutoff_date)\
            .order("timestamp", desc=False)\
            .execute()
        
        if not interactions_query.data:
            logger.warning("No interactions found for training")
            return {"error": "No training data available"}
        
        interactions = interactions_query.data
        logger.info(f"Found {len(interactions)} interactions to train from")
        
        # Group interactions by user
        user_interactions: Dict[str, List[Dict]] = {}
        for interaction in interactions:
            user_id = interaction["user_id"]
            if user_id not in user_interactions:
                user_interactions[user_id] = []
            user_interactions[user_id].append(interaction)
        
        # Filter users with enough interactions
        valid_users = {
            uid: inters for uid, inters in user_interactions.items()
            if len(inters) >= min_interactions_per_user
        }
        
        logger.info(
            f"Training on {len(valid_users)} users with {min_interactions_per_user}+ interactions"
        )
        
        # Training statistics
        total_updates = 0
        total_reward = 0.0
        episodes_trained = 0
        
        # Train on each user's interaction sequence
        for user_id, user_inters in valid_users.items():
            # Get user's personality profile
            profile = await self._get_user_personality(user_id)
            if not profile:
                continue
            
            # Train episode for this user
            episode_reward = await self._train_episode(user_id, user_inters, profile)
            
            total_reward += episode_reward
            total_updates += len(user_inters)
            episodes_trained += 1
        
        # Save updated model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        self.agent.save(self.model_path)
        
        # Get agent statistics
        agent_stats = self.agent.get_stats()
        
        training_stats = {
            "training_date": datetime.now().isoformat(),
            "days_back": days_back,
            "total_interactions": len(interactions),
            "users_trained": len(valid_users),
            "episodes_trained": episodes_trained,
            "total_updates": total_updates,
            "average_reward": total_reward / episodes_trained if episodes_trained > 0 else 0.0,
            "agent_stats": agent_stats,
            "model_saved": self.model_path
        }
        
        logger.info(f"Training complete: {training_stats}")
        
        # Log training results to database
        try:
            supabase.table("system_tasks").insert({
                "task_name": "rl_training",
                "executed_at": datetime.now().isoformat(),
                "status": "completed",
                "users_processed": len(valid_users),
                "records_processed": total_updates,
                "metadata": training_stats
            }).execute()
        except Exception as e:
            logger.error(f"Failed to log training results: {e}")
        
        return training_stats
    
    async def _train_episode(
        self,
        user_id: str,
        interactions: List[Dict],
        personality_profile: Dict[str, float]
    ) -> float:
        """
        Train on a single user's interaction sequence (episode).
        """
        episode_reward = 0.0
        
        for i, interaction in enumerate(interactions):
            # Construct state
            state = RecommendationState(
                openness=personality_profile.get("openness", 50.0),
                conscientiousness=personality_profile.get("conscientiousness", 50.0),
                extraversion=personality_profile.get("extraversion", 50.0),
                agreeableness=personality_profile.get("agreeableness", 50.0),
                neuroticism=personality_profile.get("neuroticism", 50.0),
                content_type=interaction.get("content_type", "music"),
                mood=interaction.get("mood_before", "neutral"),
                time_of_day=self._get_time_of_day(interaction.get("timestamp"))
            )
            
            # Infer action from interaction context
            # (In real deployment, we'd store the actual recommendation params used)
            action = self._infer_action_from_interaction(interaction)
            
            # Calculate reward
            reward = self.reward_function.calculate_reward(interaction)
            episode_reward += reward
            
            # Get next state if available
            next_state = None
            if i < len(interactions) - 1:
                next_interaction = interactions[i + 1]
                next_state = RecommendationState(
                    openness=personality_profile.get("openness", 50.0),
                    conscientiousness=personality_profile.get("conscientiousness", 50.0),
                    extraversion=personality_profile.get("extraversion", 50.0),
                    agreeableness=personality_profile.get("agreeableness", 50.0),
                    neuroticism=personality_profile.get("neuroticism", 50.0),
                    content_type=next_interaction.get("content_type", "music"),
                    mood=next_interaction.get("mood_before", "neutral"),
                    time_of_day=self._get_time_of_day(next_interaction.get("timestamp"))
                )
            
            # Update Q-values
            self.agent.update(state, action, reward, next_state)
        
        return episode_reward
    
    async def _get_user_personality(self, user_id: str) -> Optional[Dict[str, float]]:
        """Fetch user's personality profile."""
        try:
            supabase = get_supabase_client()
            result = supabase.table("user_personality_profiles")\
                .select("*")\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if result.data:
                return {
                    "openness": result.data.get("openness", 50.0),
                    "conscientiousness": result.data.get("conscientiousness", 50.0),
                    "extraversion": result.data.get("extraversion", 50.0),
                    "agreeableness": result.data.get("agreeableness", 50.0),
                    "neuroticism": result.data.get("neuroticism", 50.0)
                }
        except Exception as e:
            logger.error(f"Failed to fetch personality for user {user_id}: {e}")
        
        return None
    
    def _infer_action_from_interaction(self, interaction: Dict) -> RecommendationAction:
        """
        Infer the action (recommendation parameters) that led to this interaction.
        
        In production, you would store the actual parameters used.
        For now, we infer from the content characteristics.
        """
        # Default to balanced parameters
        energy = "medium"
        diversity = "balanced"
        novelty = "mixed"
        
        # Try to infer from interaction context
        context = interaction.get("context", {})
        
        if isinstance(context, dict):
            # If parameters were stored in context
            energy = context.get("energy", "medium")
            diversity = context.get("diversity", "balanced")
            novelty = context.get("novelty", "mixed")
        
        return RecommendationAction(energy, diversity, novelty)
    
    def _get_time_of_day(self, timestamp: Optional[str]) -> str:
        """Extract time of day from timestamp."""
        if not timestamp:
            return "any"
        
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            hour = dt.hour
            
            if 6 <= hour < 12:
                return "morning"
            elif 12 <= hour < 18:
                return "afternoon"
            elif 18 <= hour < 22:
                return "evening"
            else:
                return "night"
        except:
            return "any"
    
    def get_recommendation_params(
        self,
        user_id: str,
        personality_profile: Dict[str, float],
        content_type: str,
        mood: str = "neutral",
        time_of_day: str = "any"
    ) -> Dict[str, Any]:
        """
        Get optimized recommendation parameters for a user.
        
        Uses the trained Q-table to select the best action.
        """
        state = RecommendationState(
            openness=personality_profile.get("openness", 50.0),
            conscientiousness=personality_profile.get("conscientiousness", 50.0),
            extraversion=personality_profile.get("extraversion", 50.0),
            agreeableness=personality_profile.get("agreeableness", 50.0),
            neuroticism=personality_profile.get("neuroticism", 50.0),
            content_type=content_type,
            mood=mood,
            time_of_day=time_of_day
        )
        
        # Get best action (no exploration in production)
        action = self.agent.get_action(state, explore=False)
        
        # Convert to API parameters
        params = action.to_recommendation_params()
        
        logger.info(
            f"Generated params for user {user_id} in state {state.to_dict()}: "
            f"action={action.to_dict()}, params={params}"
        )
        
        return params
    
    async def evaluate_model(self, test_days: int = 3) -> Dict[str, Any]:
        """
        Evaluate the trained model on recent interactions.
        """
        logger.info(f"Evaluating model on last {test_days} days...")
        
        supabase = get_supabase_client()
        cutoff_date = (datetime.now() - timedelta(days=test_days)).isoformat()
        
        test_interactions = supabase.table("entertainment_interactions")\
            .select("*")\
            .gte("timestamp", cutoff_date)\
            .execute()
        
        if not test_interactions.data:
            return {"error": "No test data available"}
        
        total_reward = 0.0
        like_rate = 0
        total = len(test_interactions.data)
        
        for interaction in test_interactions.data:
            reward = self.reward_function.calculate_reward(interaction)
            total_reward += reward
            
            if interaction.get("interaction_type") == "like":
                like_rate += 1
        
        return {
            "test_period_days": test_days,
            "total_interactions": total,
            "average_reward": total_reward / total if total > 0 else 0.0,
            "like_rate": like_rate / total if total > 0 else 0.0,
            "evaluation_date": datetime.now().isoformat()
        }


# Global orchestrator instance
_orchestrator: Optional[RLTrainingOrchestrator] = None


def get_rl_orchestrator() -> RLTrainingOrchestrator:
    """Get or create the global RL orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = RLTrainingOrchestrator()
    return _orchestrator
