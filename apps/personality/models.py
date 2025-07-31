"""
Personality modeling and assessment models for The Last Neuron.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
import uuid
import json

User = get_user_model()


class PersonalityTrait(models.Model):
    """
    Base personality traits (Big Five model).
    """
    BIG_FIVE_TRAITS = [
        ('openness', 'Openness to Experience'),
        ('conscientiousness', 'Conscientiousness'),
        ('extraversion', 'Extraversion'),
        ('agreeableness', 'Agreeableness'),
        ('neuroticism', 'Neuroticism'),
    ]

    name = models.CharField(max_length=50, choices=BIG_FIVE_TRAITS, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.get_name_display()


class PersonalityAssessment(models.Model):
    """
    Stores the results of personality assessments.
    """
    ASSESSMENT_TYPES = [
        ('onboarding', 'Initial Onboarding'),
        ('survey', 'Periodic Survey'),
        ('behavioral', 'Behavioral Analysis'),
        ('game_based', 'Game-based Assessment'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personality_assessments')
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    
    # Big Five scores (0.0 to 1.0)
    openness = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    conscientiousness = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    extraversion = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    agreeableness = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    neuroticism = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Confidence scores for each trait
    confidence_scores = models.JSONField(default=dict)
    
    # Additional insights
    insights = models.JSONField(default=dict, blank=True)
    
    # Assessment metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.assessment_type} - {self.created_at.strftime('%Y-%m-%d')}"

    @property
    def personality_vector(self):
        """Return personality as a vector for ML processing."""
        return [
            self.openness,
            self.conscientiousness,
            self.extraversion,
            self.agreeableness,
            self.neuroticism
        ]

    def get_dominant_traits(self, threshold=0.7):
        """Get traits above a certain threshold."""
        traits = {
            'openness': self.openness,
            'conscientiousness': self.conscientiousness,
            'extraversion': self.extraversion,
            'agreeableness': self.agreeableness,
            'neuroticism': self.neuroticism,
        }
        return {trait: score for trait, score in traits.items() if score >= threshold}


class PersonalityEvolution(models.Model):
    """
    Track how personality scores change over time.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personality_evolution')
    from_assessment = models.ForeignKey(
        PersonalityAssessment, 
        on_delete=models.CASCADE, 
        related_name='evolution_from'
    )
    to_assessment = models.ForeignKey(
        PersonalityAssessment, 
        on_delete=models.CASCADE, 
        related_name='evolution_to'
    )
    
    # Change deltas for each trait
    openness_change = models.FloatField()
    conscientiousness_change = models.FloatField()
    extraversion_change = models.FloatField()
    agreeableness_change = models.FloatField()
    neuroticism_change = models.FloatField()
    
    # Evolution metadata
    days_between = models.PositiveIntegerField()
    trigger_event = models.CharField(max_length=100, blank=True)  # What caused the evolution
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - Evolution ({self.days_between} days)"

    @classmethod
    def create_evolution(cls, from_assessment, to_assessment):
        """Create an evolution record between two assessments."""
        days_diff = (to_assessment.created_at - from_assessment.created_at).days
        
        return cls.objects.create(
            user=to_assessment.user,
            from_assessment=from_assessment,
            to_assessment=to_assessment,
            openness_change=to_assessment.openness - from_assessment.openness,
            conscientiousness_change=to_assessment.conscientiousness - from_assessment.conscientiousness,
            extraversion_change=to_assessment.extraversion - from_assessment.extraversion,
            agreeableness_change=to_assessment.agreeableness - from_assessment.agreeableness,
            neuroticism_change=to_assessment.neuroticism - from_assessment.neuroticism,
            days_between=days_diff
        )


class PersonalityInsight(models.Model):
    """
    AI-generated insights about user personality.
    """
    INSIGHT_TYPES = [
        ('strength', 'Personality Strength'),
        ('growth_area', 'Growth Area'),
        ('behavior_pattern', 'Behavior Pattern'),
        ('recommendation', 'Recommendation'),
        ('mood_trigger', 'Mood Trigger'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personality_insights')
    assessment = models.ForeignKey(
        PersonalityAssessment, 
        on_delete=models.CASCADE, 
        related_name='personality_insights'
    )
    
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Relevance and confidence
    relevance_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.5
    )
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.5
    )
    
    # User interaction
    is_read = models.BooleanField(default=False)
    is_helpful = models.BooleanField(null=True, blank=True)  # User feedback
    user_rating = models.PositiveSmallIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"


class AdaptationPolicy(models.Model):
    """
    RL-based policies for agent adaptation to user personality.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='adaptation_policy')
    
    # Current policy weights (learned through RL)
    policy_weights = models.JSONField(default=dict)
    
    # Adaptation parameters
    communication_style = models.CharField(max_length=50, default='balanced')
    proactivity_level = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    formality_level = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    empathy_level = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # Learning metrics
    total_interactions = models.PositiveIntegerField(default=0)
    successful_interactions = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Model versioning
    model_version = models.CharField(max_length=20, default='v1.0')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - Adaptation Policy"

    @property
    def success_rate(self):
        """Calculate interaction success rate."""
        if self.total_interactions == 0:
            return 0.0
        return self.successful_interactions / self.total_interactions

    def update_policy(self, new_weights, interaction_success=None):
        """Update the policy weights based on RL feedback."""
        self.policy_weights = new_weights
        self.total_interactions += 1
        
        if interaction_success is not None and interaction_success:
            self.successful_interactions += 1
        
        self.save()

    def get_response_style(self):
        """Get the current response style based on policy."""
        return {
            'communication_style': self.communication_style,
            'proactivity_level': self.proactivity_level,
            'formality_level': self.formality_level,
            'empathy_level': self.empathy_level,
        }
