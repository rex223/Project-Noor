"""
Game models for personality assessment and engagement.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import json

User = get_user_model()


class GameType(models.Model):
    """
    Different types of games available for personality assessment.
    """
    GAME_CATEGORIES = [
        ('personality', 'Personality Assessment'),
        ('rpg', 'Role-Playing Game'),
        ('dilemma', 'Moral Dilemma'),
        ('scenario', 'Life Scenario'),
        ('creative', 'Creative Exercise'),
        ('memory', 'Memory Game'),
        ('logic', 'Logic Puzzle'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=GAME_CATEGORIES)
    description = models.TextField()
    instructions = models.TextField()
    
    # Personality traits this game assesses
    assesses_openness = models.BooleanField(default=False)
    assesses_conscientiousness = models.BooleanField(default=False)
    assesses_extraversion = models.BooleanField(default=False)
    assesses_agreeableness = models.BooleanField(default=False)
    assesses_neuroticism = models.BooleanField(default=False)
    
    # Game configuration
    estimated_duration_minutes = models.PositiveIntegerField(default=5)
    difficulty_level = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Game data
    game_data = models.JSONField(default=dict)  # Scenarios, questions, etc.
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

    @property
    def assessed_traits(self):
        """Return list of traits this game assesses."""
        traits = []
        if self.assesses_openness:
            traits.append('openness')
        if self.assesses_conscientiousness:
            traits.append('conscientiousness')
        if self.assesses_extraversion:
            traits.append('extraversion')
        if self.assesses_agreeableness:
            traits.append('agreeableness')
        if self.assesses_neuroticism:
            traits.append('neuroticism')
        return traits


class GameSession(models.Model):
    """
    A user's session playing a specific game.
    """
    SESSION_STATUS = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
        ('paused', 'Paused'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_sessions')
    game_type = models.ForeignKey(GameType, on_delete=models.CASCADE, related_name='sessions')
    
    # Session details
    status = models.CharField(max_length=15, choices=SESSION_STATUS, default='started')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Game state and progress
    current_step = models.PositiveIntegerField(default=0)
    total_steps = models.PositiveIntegerField(default=1)
    game_state = models.JSONField(default=dict)  # Current game state
    
    # Results and analytics
    responses = models.JSONField(default=list)  # All user responses
    personality_scores = models.JSONField(default=dict)  # Calculated personality scores
    engagement_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    
    # User feedback
    user_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    enjoyed_game = models.BooleanField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.email} - {self.game_type.name} - {self.status}"

    def complete_session(self):
        """Mark session as completed and calculate results."""
        from django.utils import timezone
        
        self.status = 'completed'
        self.completed_at = timezone.now()
        if self.started_at:
            duration = self.completed_at - self.started_at
            self.duration_minutes = int(duration.total_seconds() / 60)
        
        # Calculate engagement score
        self.calculate_engagement_score()
        
        # Calculate personality scores
        self.calculate_personality_scores()
        
        self.save()
        
        # Update user's game count
        self.user.profile.increment_games()

    def calculate_engagement_score(self):
        """Calculate user engagement score for this session."""
        # Base engagement on completion, response time, and interactions
        completion_score = 5.0 if self.status == 'completed' else 0.0
        response_count_score = min(len(self.responses) / 5, 3.0)
        time_score = min(self.duration_minutes / 10, 2.0) if self.duration_minutes else 0.0
        
        self.engagement_score = completion_score + response_count_score + time_score

    def calculate_personality_scores(self):
        """Calculate personality trait scores based on responses."""
        if not self.responses:
            return
        
        # This will be implemented with actual scoring algorithms
        # For now, placeholder implementation
        scores = {
            'openness': 0.5,
            'conscientiousness': 0.5,
            'extraversion': 0.5,
            'agreeableness': 0.5,
            'neuroticism': 0.5,
        }
        
        # Analyze responses based on game type
        if self.game_type.category == 'dilemma':
            scores = self._score_dilemma_responses()
        elif self.game_type.category == 'rpg':
            scores = self._score_rpg_responses()
        
        self.personality_scores = scores

    def _score_dilemma_responses(self):
        """Score responses for moral dilemma games."""
        # Placeholder implementation
        return {
            'openness': 0.6,
            'conscientiousness': 0.7,
            'extraversion': 0.5,
            'agreeableness': 0.8,
            'neuroticism': 0.3,
        }

    def _score_rpg_responses(self):
        """Score responses for RPG scenario games."""
        # Placeholder implementation
        return {
            'openness': 0.8,
            'conscientiousness': 0.6,
            'extraversion': 0.7,
            'agreeableness': 0.6,
            'neuroticism': 0.4,
        }


class GameResponse(models.Model):
    """
    Individual responses within a game session.
    """
    RESPONSE_TYPES = [
        ('choice', 'Multiple Choice'),
        ('text', 'Text Response'),
        ('rating', 'Rating Scale'),
        ('ranking', 'Ranking'),
        ('boolean', 'Yes/No'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='response_details')
    
    # Response details
    question_id = models.CharField(max_length=50)  # Reference to question in game data
    question_text = models.TextField()
    response_type = models.CharField(max_length=10, choices=RESPONSE_TYPES)
    
    # Response data
    response_value = models.TextField()  # The actual response
    response_time_seconds = models.PositiveIntegerField()  # Time taken to respond
    
    # Analysis
    personality_impact = models.JSONField(default=dict)  # How this affects personality scores
    confidence_level = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Response to {self.question_id} - {self.response_value[:50]}"


class GameScenario(models.Model):
    """
    Pre-defined scenarios for RPG and dilemma games.
    """
    SCENARIO_TYPES = [
        ('moral_dilemma', 'Moral Dilemma'),
        ('life_choice', 'Life Choice'),
        ('social_situation', 'Social Situation'),
        ('work_scenario', 'Work Scenario'),
        ('relationship', 'Relationship'),
        ('ethical_choice', 'Ethical Choice'),
    ]

    DIFFICULTY_LEVELS = [
        (1, 'Very Easy'),
        (2, 'Easy'),
        (3, 'Medium'),
        (4, 'Hard'),
        (5, 'Very Hard'),
    ]

    name = models.CharField(max_length=200)
    scenario_type = models.CharField(max_length=20, choices=SCENARIO_TYPES)
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_LEVELS, default=3)
    
    # Scenario content
    description = models.TextField()
    background_story = models.TextField()
    
    # Choices and outcomes
    choices = models.JSONField(default=list)  # List of possible choices
    outcomes = models.JSONField(default=dict)  # Outcomes for each choice
    
    # Personality mapping
    trait_weights = models.JSONField(default=dict)  # How choices affect personality traits
    
    # Usage analytics
    times_used = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.scenario_type})"

    def increment_usage(self):
        """Increment usage count when scenario is used."""
        self.times_used += 1
        self.save()


class Achievement(models.Model):
    """
    User achievements from games and interactions.
    """
    ACHIEVEMENT_TYPES = [
        ('game_completion', 'Game Completion'),
        ('personality_insight', 'Personality Insight'),
        ('engagement', 'Engagement'),
        ('streak', 'Activity Streak'),
        ('milestone', 'Milestone'),
        ('social', 'Social Achievement'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    
    # Achievement criteria
    criteria = models.JSONField(default=dict)  # What's needed to unlock
    icon = models.CharField(max_length=50, default='🏆')  # Emoji or icon name
    points = models.PositiveIntegerField(default=10)  # Points awarded
    
    # Rarity
    rarity = models.CharField(
        max_length=10,
        choices=[
            ('common', 'Common'),
            ('uncommon', 'Uncommon'),
            ('rare', 'Rare'),
            ('epic', 'Epic'),
            ('legendary', 'Legendary'),
        ],
        default='common'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.rarity})"


class UserAchievement(models.Model):
    """
    Achievements unlocked by users.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    
    # Unlock details
    unlocked_at = models.DateTimeField(auto_now_add=True)
    trigger_context = models.JSONField(default=dict, blank=True)  # What triggered the unlock
    
    # User interaction
    is_seen = models.BooleanField(default=False)
    is_celebrated = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'achievement']
        ordering = ['-unlocked_at']

    def __str__(self):
        return f"{self.user.email} - {self.achievement.name}"
