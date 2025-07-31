"""
Chat and messaging models for The Last Neuron.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class ChatSession(models.Model):
    """
    Represents a chat session between user and the AI agent.
    """
    SESSION_STATUS = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('ended', 'Ended'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    status = models.CharField(max_length=10, choices=SESSION_STATUS, default='active')
    
    # Session metadata
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Context and personality state
    session_context = models.JSONField(default=dict, blank=True)
    agent_personality_state = models.JSONField(default=dict, blank=True)
    
    # Analytics
    message_count = models.PositiveIntegerField(default=0)
    user_satisfaction = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5 rating
    
    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.email} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"

    def end_session(self, satisfaction_rating=None):
        """End the chat session."""
        self.status = 'ended'
        self.ended_at = timezone.now()
        if satisfaction_rating:
            self.user_satisfaction = satisfaction_rating
        self.save()

    @property
    def duration_minutes(self):
        """Get session duration in minutes."""
        if self.ended_at:
            return int((self.ended_at - self.started_at).total_seconds() / 60)
        return int((timezone.now() - self.started_at).total_seconds() / 60)


class Message(models.Model):
    """
    Individual messages within a chat session.
    """
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('agent', 'Agent Message'),
        ('system', 'System Message'),
        ('game', 'Game Message'),
    ]

    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
        ('mixed', 'Mixed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    
    # Message content
    content = models.TextField()
    encrypted_content = models.BinaryField(null=True, blank=True)  # Encrypted storage
    
    # Message metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    # NLP Analysis results
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, null=True, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)  # -1.0 to 1.0
    emotion_analysis = models.JSONField(default=dict, blank=True)
    keywords = models.JSONField(default=list, blank=True)
    
    # Agent response metadata (for agent messages)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    agent_confidence = models.FloatField(null=True, blank=True)
    
    # User feedback (for agent messages)
    user_rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5
    is_helpful = models.BooleanField(null=True, blank=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.message_type} - {self.timestamp.strftime('%H:%M:%S')} - {self.content[:50]}..."

    def analyze_sentiment(self):
        """Analyze message sentiment using NLP."""
        # This will be implemented with actual NLP models
        # For now, placeholder implementation
        pass

    def encrypt_content(self):
        """Encrypt message content for privacy."""
        # This will be implemented with actual encryption
        # For now, placeholder implementation
        pass


class ProactiveMessage(models.Model):
    """
    Messages that the agent can send proactively based on triggers.
    """
    TRIGGER_TYPES = [
        ('inactivity', 'User Inactivity'),
        ('mood_change', 'Mood Change Detected'),
        ('scheduled', 'Scheduled Check-in'),
        ('achievement', 'Achievement Unlock'),
        ('recommendation', 'Content Recommendation'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proactive_messages')
    
    # Message details
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPES)
    message_template = models.TextField()
    personalized_content = models.TextField()
    
    # Scheduling
    scheduled_for = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Context and metadata
    trigger_context = models.JSONField(default=dict, blank=True)
    priority = models.PositiveSmallIntegerField(default=1)  # 1-5, 5 being highest
    
    # Response tracking
    user_responded = models.BooleanField(default=False)
    response_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority', 'scheduled_for']

    def __str__(self):
        return f"{self.user.email} - {self.trigger_type} - {self.scheduled_for}"

    def mark_as_sent(self):
        """Mark the message as sent."""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()

    def cancel(self):
        """Cancel the proactive message."""
        self.status = 'cancelled'
        self.save()


class ConversationTopic(models.Model):
    """
    Track conversation topics for context awareness.
    """
    TOPIC_CATEGORIES = [
        ('personal', 'Personal Life'),
        ('education', 'Education'),
        ('career', 'Career'),
        ('relationships', 'Relationships'),
        ('hobbies', 'Hobbies & Interests'),
        ('mental_health', 'Mental Health'),
        ('goals', 'Goals & Aspirations'),
        ('entertainment', 'Entertainment'),
        ('technology', 'Technology'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='topics')
    
    # Topic details
    topic_name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=TOPIC_CATEGORIES)
    keywords = models.JSONField(default=list)
    
    # Topic metrics
    frequency = models.PositiveIntegerField(default=1)
    sentiment_avg = models.FloatField(default=0.0)
    last_discussed = models.DateTimeField(auto_now=True)
    
    # User engagement with topic
    user_interest_level = models.FloatField(default=0.5)  # 0.0 to 1.0
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['session', 'topic_name']
        ordering = ['-frequency', '-last_discussed']

    def __str__(self):
        return f"{self.topic_name} ({self.category})"

    def increment_frequency(self):
        """Increment topic frequency when discussed again."""
        self.frequency += 1
        self.save()


class AgentPersonality(models.Model):
    """
    The agent's current personality state for each user.
    """
    COMMUNICATION_STYLES = [
        ('casual', 'Casual & Friendly'),
        ('professional', 'Professional'),
        ('empathetic', 'Empathetic'),
        ('playful', 'Playful'),
        ('supportive', 'Supportive'),
        ('analytical', 'Analytical'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_personality')
    
    # Current personality configuration
    communication_style = models.CharField(max_length=20, choices=COMMUNICATION_STYLES, default='casual')
    enthusiasm_level = models.FloatField(default=0.7)  # 0.0 to 1.0
    formality_level = models.FloatField(default=0.3)   # 0.0 to 1.0
    proactivity_level = models.FloatField(default=0.5) # 0.0 to 1.0
    empathy_level = models.FloatField(default=0.8)     # 0.0 to 1.0
    
    # Learned preferences
    preferred_topics = models.JSONField(default=list, blank=True)
    conversation_patterns = models.JSONField(default=dict, blank=True)
    response_preferences = models.JSONField(default=dict, blank=True)
    
    # Adaptation tracking
    adaptation_count = models.PositiveIntegerField(default=0)
    last_adaptation = models.DateTimeField(auto_now=True)
    
    # Performance metrics
    user_satisfaction_avg = models.FloatField(default=0.0)
    successful_interactions = models.PositiveIntegerField(default=0)
    total_interactions = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Agent Personality for {self.user.email}"

    def adapt_personality(self, feedback_score, interaction_context):
        """Adapt personality based on user feedback."""
        self.adaptation_count += 1
        self.total_interactions += 1
        
        if feedback_score >= 4:  # Positive feedback
            self.successful_interactions += 1
        
        # Update satisfaction average
        if self.total_interactions > 0:
            self.user_satisfaction_avg = self.successful_interactions / self.total_interactions
        
        self.save()

    @property
    def success_rate(self):
        """Calculate interaction success rate."""
        if self.total_interactions == 0:
            return 0.0
        return self.successful_interactions / self.total_interactions
