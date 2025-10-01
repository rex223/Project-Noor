"""
Personality context service for fetching and managing user personality data.
"""

from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from .models import (
    PersonalityProfile, 
    LLMContext, 
    OnboardingStatus, 
    PersonalityContextResponse,
    AgentAnalysisRecord
)
from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class PersonalityContextService:
    """Service for managing personality context and LLM prompts with caching."""
    
    def __init__(self, cache_ttl_minutes: int = 30):
        self.db_client = get_supabase_client()
        self._cache: Dict[str, tuple[PersonalityContextResponse, datetime]] = {}
        self._cache_ttl = timedelta(minutes=cache_ttl_minutes)
    
    def _get_cached_context(self, user_id: str) -> Optional[PersonalityContextResponse]:
        """Get cached personality context if available and not expired."""
        if user_id in self._cache:
            context, cached_at = self._cache[user_id]
            if datetime.now() - cached_at < self._cache_ttl:
                logger.info(f"Using cached personality context for user {user_id}")
                return context
            else:
                # Remove expired cache
                del self._cache[user_id]
        return None
    
    def _cache_context(self, user_id: str, context: PersonalityContextResponse):
        """Cache personality context for user."""
        self._cache[user_id] = (context, datetime.now())
        logger.debug(f"Cached personality context for user {user_id}")
    
    async def get_user_personality_context(
        self, 
        user_id: str,
        include_analysis_history: bool = False,
        use_cache: bool = True
    ) -> PersonalityContextResponse:
        """
        Get comprehensive personality context for a user with caching.
        
        Args:
            user_id: User's UUID
            include_analysis_history: Whether to include agent analysis history
            use_cache: Whether to use cached data (default True)
            
        Returns:
            Complete personality context response
        """
        # Check cache first
        if use_cache and not include_analysis_history:
            cached = self._get_cached_context(user_id)
            if cached:
                return cached
        
        try:
            # Get onboarding status
            onboarding_status_data = await self.db_client.check_user_onboarding_status(user_id)
            onboarding_status = OnboardingStatus(**onboarding_status_data)
            
            # If user doesn't exist or hasn't completed personality assessment
            if not onboarding_status.user_exists or not onboarding_status.has_personality_assessment:
                result = PersonalityContextResponse(
                    user_id=user_id,
                    has_assessment=False,
                    onboarding_status=onboarding_status
                )
                # Cache even negative results to avoid repeated DB calls
                if use_cache:
                    self._cache_context(user_id, result)
                return result
            
            # Get personality data
            personality_data = await self.db_client.get_user_personality(user_id)
            if not personality_data:
                result = PersonalityContextResponse(
                    user_id=user_id,
                    has_assessment=False,
                    onboarding_status=onboarding_status
                )
                if use_cache:
                    self._cache_context(user_id, result)
                return result
            
            # Create personality profile
            personality_profile = PersonalityProfile(**personality_data)
            
            # Parse LLM context
            llm_context = None
            if personality_data.get('llm_context'):
                llm_context_data = personality_data['llm_context']
                llm_context = LLMContext(
                    system_prompt=llm_context_data.get('systemPrompt', ''),
                    language_style=llm_context_data.get('languageStyle', ''),
                    stress_response=llm_context_data.get('stressResponse', ''),
                    motivation_style=llm_context_data.get('motivationStyle', ''),
                    support_approach=llm_context_data.get('supportApproach', ''),
                    conflict_approach=llm_context_data.get('conflictApproach', ''),
                    emotional_support=llm_context_data.get('emotionalSupport', ''),
                    topic_preferences=llm_context_data.get('topicPreferences', []),
                    conversation_style=llm_context_data.get('conversationStyle', ''),
                    interaction_frequency=llm_context_data.get('interactionFrequency', ''),
                    communication_preferences=llm_context_data.get('communicationPreferences', '')
                )
            
            # Get analysis history if requested
            agent_history = None
            if include_analysis_history:
                history_data = await self.db_client.get_agent_analysis_history(user_id)
                agent_history = [
                    AgentAnalysisRecord(**record) for record in history_data
                ]
            
            result = PersonalityContextResponse(
                user_id=user_id,
                has_assessment=True,
                personality_profile=personality_profile,
                llm_context=llm_context,
                onboarding_status=onboarding_status,
                agent_history=agent_history
            )
            
            # Cache the result
            if use_cache and not include_analysis_history:
                self._cache_context(user_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting personality context for user {user_id}: {e}")
            # Return minimal response with error info
            error_status = OnboardingStatus(
                user_id=user_id,
                user_exists=False,
                error=str(e)
            )
            return PersonalityContextResponse(
                user_id=user_id,
                has_assessment=False,
                onboarding_status=error_status
            )
    
    async def get_llm_system_prompt(self, user_id: str) -> Optional[str]:
        """
        Get the LLM system prompt for a user.
        
        Args:
            user_id: User's UUID
            
        Returns:
            System prompt string or None if not available
        """
        try:
            llm_context_data = await self.db_client.get_personality_llm_context(user_id)
            if llm_context_data and 'systemPrompt' in llm_context_data:
                return llm_context_data['systemPrompt']
            return None
        except Exception as e:
            logger.error(f"Error getting LLM system prompt for user {user_id}: {e}")
            return None
    
    async def store_agent_result(
        self, 
        user_id: str, 
        agent_type: str, 
        result_data: Dict[str, Any]
    ) -> bool:
        """
        Store agent analysis result.
        
        Args:
            user_id: User's UUID
            agent_type: Type of agent
            result_data: Analysis result data
            
        Returns:
            True if successful
        """
        try:
            return await self.db_client.store_agent_analysis(
                user_id, agent_type, result_data
            )
        except Exception as e:
            logger.error(f"Error storing agent result for user {user_id}: {e}")
            return False
    
    def get_trait_insights(self, personality_profile: PersonalityProfile) -> Dict[str, str]:
        """
        Get personality trait insights for agents to use.
        
        Args:
            personality_profile: User's personality profile
            
        Returns:
            Dictionary of trait insights
        """
        insights = {}
        
        # Openness insights
        openness_level = personality_profile.get_trait_level("openness")
        if openness_level == "High":
            insights["openness"] = "User is highly creative and open to new experiences. Engage with abstract concepts, creative projects, and philosophical discussions."
        elif openness_level == "Moderate":
            insights["openness"] = "User has balanced openness. Mix practical and creative content based on context."
        else:
            insights["openness"] = "User prefers practical, conventional approaches. Focus on concrete, actionable advice."
        
        # Conscientiousness insights
        conscientiousness_level = personality_profile.get_trait_level("conscientiousness")
        if conscientiousness_level == "High":
            insights["conscientiousness"] = "User is highly organized and goal-oriented. Provide structured plans and systematic approaches."
        elif conscientiousness_level == "Moderate":
            insights["conscientiousness"] = "User has moderate organization. Balance structure with flexibility."
        else:
            insights["conscientiousness"] = "User is more spontaneous. Keep suggestions flexible and adaptable."
        
        # Extraversion insights
        extraversion_level = personality_profile.get_trait_level("extraversion")
        if extraversion_level == "High":
            insights["extraversion"] = "User is highly social and energetic. Suggest social activities and group interactions."
        elif extraversion_level == "Moderate":
            insights["extraversion"] = "User has balanced social preferences. Adapt to their current mood and energy."
        else:
            insights["extraversion"] = "User prefers quieter, solitary activities. Suggest individual pursuits and reflection."
        
        # Agreeableness insights
        agreeableness_level = personality_profile.get_trait_level("agreeableness")
        if agreeableness_level == "High":
            insights["agreeableness"] = "User is highly cooperative and empathetic. Focus on collaborative and helping activities."
        elif agreeableness_level == "Moderate":
            insights["agreeableness"] = "User has balanced interpersonal approach. Mix cooperative and independent suggestions."
        else:
            insights["agreeableness"] = "User is more competitive and independent. Suggest challenging and achievement-oriented activities."
        
        # Neuroticism insights
        neuroticism_level = personality_profile.get_trait_level("neuroticism")
        if neuroticism_level == "High":
            insights["neuroticism"] = "User may experience higher stress levels. Provide calming, stress-reducing suggestions and emotional support."
        elif neuroticism_level == "Moderate":
            insights["neuroticism"] = "User has moderate emotional stability. Provide balanced support based on current stress levels."
        else:
            insights["neuroticism"] = "User is emotionally stable. Can handle more challenging or stimulating content."
        
        return insights
    
    def get_agent_guidelines(self, personality_profile: PersonalityProfile) -> Dict[str, Any]:
        """
        Get specific guidelines for agents based on personality profile.
        
        Args:
            personality_profile: User's personality profile
            
        Returns:
            Dictionary of agent-specific guidelines
        """
        return {
            "music_preferences": self._get_music_guidelines(personality_profile),
            "video_preferences": self._get_video_guidelines(personality_profile),
            "gaming_preferences": self._get_gaming_guidelines(personality_profile),
            "conversation_style": self._get_conversation_guidelines(personality_profile)
        }
    
    def _get_music_guidelines(self, profile: PersonalityProfile) -> Dict[str, str]:
        """Get music-specific guidelines based on personality."""
        guidelines = {}
        
        if profile.openness >= 70:
            guidelines["genres"] = "Explore diverse, experimental, and complex musical genres"
            guidelines["discovery"] = "Recommend new and unique artists regularly"
        elif profile.openness >= 40:
            guidelines["genres"] = "Mix familiar and new musical styles"
            guidelines["discovery"] = "Introduce new music gradually"
        else:
            guidelines["genres"] = "Focus on familiar, mainstream genres"
            guidelines["discovery"] = "Stick to well-known artists and popular music"
        
        if profile.extraversion >= 70:
            guidelines["energy"] = "Prefer upbeat, energetic music for social settings"
        else:
            guidelines["energy"] = "Appreciate calmer, more introspective music"
        
        return guidelines
    
    def _get_video_guidelines(self, profile: PersonalityProfile) -> Dict[str, str]:
        """Get video-specific guidelines based on personality."""
        guidelines = {}
        
        if profile.openness >= 70:
            guidelines["content"] = "Educational, documentary, and creative content"
            guidelines["variety"] = "Diverse topics and experimental formats"
        else:
            guidelines["content"] = "Entertainment and familiar content types"
            guidelines["variety"] = "Consistent genres and formats"
        
        if profile.conscientiousness >= 70:
            guidelines["length"] = "Longer-form, educational content"
        else:
            guidelines["length"] = "Shorter, easily digestible content"
        
        return guidelines
    
    def _get_gaming_guidelines(self, profile: PersonalityProfile) -> Dict[str, str]:
        """Get gaming-specific guidelines based on personality."""
        guidelines = {}
        
        if profile.extraversion >= 70:
            guidelines["multiplayer"] = "Social and multiplayer gaming experiences"
            guidelines["competition"] = "Competitive and team-based games"
        else:
            guidelines["multiplayer"] = "Single-player and solo gaming experiences"
            guidelines["competition"] = "Cooperative or non-competitive games"
        
        if profile.conscientiousness >= 70:
            guidelines["complexity"] = "Strategy and complex games requiring planning"
            guidelines["completion"] = "Focus on completing games and achievements"
        else:
            guidelines["complexity"] = "Casual and easy-to-pick-up games"
            guidelines["completion"] = "Fun and exploration over completion"
        
        return guidelines
    
    def _get_conversation_guidelines(self, profile: PersonalityProfile) -> Dict[str, str]:
        """Get conversation-specific guidelines based on personality."""
        guidelines = {}
        
        if profile.extraversion >= 70:
            guidelines["energy"] = "Match high energy and enthusiasm"
            guidelines["interaction"] = "Encourage social sharing and discussion"
        else:
            guidelines["energy"] = "Use calm, thoughtful communication"
            guidelines["interaction"] = "Respect need for personal reflection"
        
        if profile.agreeableness >= 70:
            guidelines["tone"] = "Warm, supportive, and collaborative"
            guidelines["conflict"] = "Avoid confrontation, focus on harmony"
        else:
            guidelines["tone"] = "Direct, honest, and straightforward"
            guidelines["conflict"] = "Can handle disagreement and debate"
        
        if profile.neuroticism >= 70:
            guidelines["support"] = "Provide extra emotional support and reassurance"
            guidelines["stress"] = "Be mindful of stress levels and anxiety"
        else:
            guidelines["support"] = "Standard emotional support"
            guidelines["stress"] = "Can handle more challenging discussions"
        
        return guidelines


# Global service instance
_personality_service: Optional[PersonalityContextService] = None


def get_personality_service() -> PersonalityContextService:
    """Get the global personality context service instance."""
    global _personality_service
    if _personality_service is None:
        _personality_service = PersonalityContextService()
    return _personality_service