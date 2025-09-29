"""
Database models for Bondhu AI personality data.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class PersonalityTrait(str, Enum):
    """Big Five personality traits."""
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"


class PersonalityScore(BaseModel):
    """Individual personality trait score."""
    trait: PersonalityTrait
    score: int = Field(..., ge=0, le=100, description="Personality trait score from 0-100")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in this score")


class PersonalityProfile(BaseModel):
    """Complete user personality profile from Big Five assessment."""
    user_id: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    scores: Dict[str, int] = Field(
        description="Big Five trait scores",
        example={
            "openness": 83,
            "conscientiousness": 67,
            "extraversion": 58,
            "agreeableness": 67,
            "neuroticism": 58
        }
    )
    llm_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Generated LLM context based on personality assessment"
    )
    completed_at: Optional[datetime] = None
    has_assessment: bool = Field(default=False)
    onboarding_completed: bool = Field(default=False)
    profile_completion_percentage: Optional[float] = Field(
        default=None,
        description="Overall profile completion percentage"
    )
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def openness(self) -> int:
        """Get openness score."""
        return self.scores.get("openness", 0)
    
    @property
    def conscientiousness(self) -> int:
        """Get conscientiousness score."""
        return self.scores.get("conscientiousness", 0)
    
    @property
    def extraversion(self) -> int:
        """Get extraversion score."""
        return self.scores.get("extraversion", 0)
    
    @property
    def agreeableness(self) -> int:
        """Get agreeableness score."""
        return self.scores.get("agreeableness", 0)
    
    @property
    def neuroticism(self) -> int:
        """Get neuroticism score."""
        return self.scores.get("neuroticism", 0)
    
    def get_trait_level(self, trait: str) -> str:
        """
        Get descriptive level for a trait score.
        
        Args:
            trait: Trait name
            
        Returns:
            Descriptive level (Low, Moderate, High)
        """
        score = self.scores.get(trait, 0)
        if score < 40:
            return "Low"
        elif score < 70:
            return "Moderate"
        else:
            return "High"
    
    def get_all_trait_levels(self) -> Dict[str, str]:
        """Get descriptive levels for all traits."""
        return {
            trait: self.get_trait_level(trait)
            for trait in self.scores.keys()
        }


class LLMContext(BaseModel):
    """LLM context data structure matching your existing format."""
    system_prompt: str = Field(description="Main system prompt for the LLM")
    language_style: str = Field(description="Language style guidance")
    stress_response: str = Field(description="Stress management approach")
    motivation_style: str = Field(description="Motivation approach")
    support_approach: str = Field(description="Emotional support approach")
    conflict_approach: str = Field(description="Conflict handling approach")
    emotional_support: str = Field(description="Emotional support style")
    topic_preferences: List[str] = Field(description="Preferred conversation topics")
    conversation_style: str = Field(description="Overall conversation style")
    interaction_frequency: str = Field(description="Interaction frequency preference")
    communication_preferences: str = Field(description="Communication preferences")


class OnboardingStatus(BaseModel):
    """User onboarding status information."""
    user_id: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    user_exists: bool = Field(default=False)
    onboarding_completed: bool = Field(default=False)
    has_personality_assessment: bool = Field(default=False)
    personality_completed_at: Optional[datetime] = None
    profile_completion_percentage: Optional[float] = Field(
        default=None,
        description="Overall profile completion percentage"
    )
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    error: Optional[str] = None


class AgentAnalysisType(str, Enum):
    """Types of agent analyses."""
    MUSIC = "music"
    VIDEO = "video"
    GAMING = "gaming"
    PERSONALITY = "personality"
    CROSS_MODAL = "cross_modal"


class AgentAnalysisRecord(BaseModel):
    """Agent analysis record for storage."""
    user_id: str
    agent_type: AgentAnalysisType
    analysis_data: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserPersonalityRequest(BaseModel):
    """Request to get user personality data."""
    user_id: str
    include_llm_context: bool = Field(default=True)
    include_analysis_history: bool = Field(default=False)


class PersonalityContextResponse(BaseModel):
    """Response containing personality context for agents."""
    user_id: str
    has_assessment: bool
    personality_profile: Optional[PersonalityProfile] = None
    llm_context: Optional[LLMContext] = None
    onboarding_status: OnboardingStatus
    agent_history: Optional[List[AgentAnalysisRecord]] = None
    
    def is_ready_for_analysis(self) -> bool:
        """Check if user is ready for personality analysis."""
        return (
            self.has_assessment and 
            self.personality_profile is not None and 
            self.onboarding_status.onboarding_completed
        )
    
    def get_system_prompt(self) -> Optional[str]:
        """Get the system prompt for LLM interactions."""
        if self.llm_context:
            return self.llm_context.system_prompt
        return None
    
    def get_conversation_guidelines(self) -> Dict[str, str]:
        """Get conversation guidelines for agents."""
        if not self.llm_context:
            return {}
        
        return {
            "language_style": self.llm_context.language_style,
            "conversation_style": self.llm_context.conversation_style,
            "support_approach": self.llm_context.support_approach,
            "motivation_style": self.llm_context.motivation_style,
            "stress_response": self.llm_context.stress_response
        }