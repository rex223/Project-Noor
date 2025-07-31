"""
Core ML components for The Last Neuron.
"""

from django.db import models
from django.contrib.auth import get_user_model
import uuid
import json

User = get_user_model()


class MLModel(models.Model):
    """
    Tracks different ML models used in the system.
    """
    MODEL_TYPES = [
        ('personality_classifier', 'Personality Classifier'),
        ('sentiment_analyzer', 'Sentiment Analyzer'),
        ('rl_agent', 'Reinforcement Learning Agent'),
        ('recommendation_engine', 'Recommendation Engine'),
        ('mood_detector', 'Mood Detector'),
        ('response_generator', 'Response Generator'),
    ]

    MODEL_STATUS = [
        ('training', 'Training'),
        ('active', 'Active'),
        ('deprecated', 'Deprecated'),
        ('failed', 'Failed'),
    ]

    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=30, choices=MODEL_TYPES)
    version = models.CharField(max_length=20)
    
    # Model metadata
    description = models.TextField()
    file_path = models.CharField(max_length=500)  # Path to model file
    config = models.JSONField(default=dict)  # Model configuration
    
    # Performance metrics
    accuracy = models.FloatField(null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    
    # Training details
    training_data_size = models.PositiveIntegerField(null=True, blank=True)
    training_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    status = models.CharField(max_length=15, choices=MODEL_STATUS, default='training')
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['model_type', 'version']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} v{self.version} ({self.model_type})"


class ReinforcementLearningState(models.Model):
    """
    RL state for each user's agent adaptation.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rl_state')
    
    # Current state representation
    state_vector = models.JSONField(default=list)  # Current state features
    personality_vector = models.JSONField(default=list)  # User personality
    context_vector = models.JSONField(default=list)  # Current context
    
    # RL parameters
    policy_weights = models.JSONField(default=dict)
    value_function = models.JSONField(default=dict)
    exploration_rate = models.FloatField(default=0.1)  # Epsilon for exploration
    
    # Learning history
    total_interactions = models.PositiveIntegerField(default=0)
    total_rewards = models.FloatField(default=0.0)
    average_reward = models.FloatField(default=0.0)
    
    # Adaptation tracking
    last_action = models.JSONField(default=dict, blank=True)
    last_reward = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RL State for {self.user.email}"

    def update_state(self, new_state, action, reward):
        """Update RL state with new experience."""
        self.state_vector = new_state
        self.last_action = action
        self.last_reward = reward
        self.total_interactions += 1
        self.total_rewards += reward
        
        if self.total_interactions > 0:
            self.average_reward = self.total_rewards / self.total_interactions
        
        self.save()
