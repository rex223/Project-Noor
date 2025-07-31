"""
User and Profile models for The Last Neuron.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class User(AbstractUser):
    """
    Custom User model with additional fields for The Last Neuron.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_onboarded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    Extended profile information for users.
    """
    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('anxious', 'Anxious'),
        ('excited', 'Excited'),
        ('calm', 'Calm'),
        ('stressed', 'Stressed'),
        ('neutral', 'Neutral'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    current_mood = models.CharField(max_length=20, choices=MOOD_CHOICES, default='neutral')
    mood_updated_at = models.DateTimeField(auto_now=True)
    
    # Privacy preferences
    share_analytics = models.BooleanField(default=True)
    receive_recommendations = models.BooleanField(default=True)
    proactive_messaging = models.BooleanField(default=True)
    
    # Engagement metrics
    total_sessions = models.PositiveIntegerField(default=0)
    total_messages = models.PositiveIntegerField(default=0)
    total_games_played = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Personality insights (JSON field for flexibility)
    personality_insights = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Profile"

    def update_mood(self, mood):
        """Update user's current mood."""
        if mood in dict(self.MOOD_CHOICES):
            self.current_mood = mood
            self.save(update_fields=['current_mood', 'mood_updated_at'])

    def increment_session(self):
        """Increment session count."""
        self.total_sessions += 1
        self.save(update_fields=['total_sessions', 'last_activity'])

    def increment_messages(self, count=1):
        """Increment message count."""
        self.total_messages += count
        self.save(update_fields=['total_messages', 'last_activity'])

    def increment_games(self):
        """Increment games played count."""
        self.total_games_played += 1
        self.save(update_fields=['total_games_played', 'last_activity'])


class UserSession(models.Model):
    """
    Track user sessions for analytics and proactive engagement.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Session analytics
    messages_sent = models.PositiveIntegerField(default=0)
    games_played = models.PositiveIntegerField(default=0)
    mood_at_start = models.CharField(max_length=20, blank=True)
    mood_at_end = models.CharField(max_length=20, blank=True)
    
    # Engagement quality
    engagement_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    
    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.email} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"

    def end_session(self):
        """End the session and calculate duration."""
        from django.utils import timezone
        if not self.ended_at:
            self.ended_at = timezone.now()
            duration = self.ended_at - self.started_at
            self.duration_minutes = int(duration.total_seconds() / 60)
            self.save()

    def calculate_engagement_score(self):
        """Calculate engagement score based on session activity."""
        if self.duration_minutes:
            # Base score on duration, messages, and games
            duration_score = min(self.duration_minutes / 10, 5)  # Max 5 points for duration
            message_score = min(self.messages_sent / 5, 3)  # Max 3 points for messages
            game_score = self.games_played * 2  # 2 points per game
            
            self.engagement_score = min(duration_score + message_score + game_score, 10)
            self.save(update_fields=['engagement_score'])
