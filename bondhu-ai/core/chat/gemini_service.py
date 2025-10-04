"""
Gemini Chat Service for Bondhu AI
Handles personality-aware chat interactions using Google Gemini Pro
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:
    ChatGoogleGenerativeAI = None
from langchain_core.messages import SystemMessage, HumanMessage

from core.config import get_config
from core.database.personality_service import get_personality_service

logger = logging.getLogger("bondhu.chat")


class GeminiChatService:
    """
    Service for handling chat interactions with Google Gemini Pro.
    Loads personality context and generates empathetic responses.
    """
    
    def __init__(self):
        """Initialize Gemini chat service with configuration."""
        self.config = get_config()
        # Provide a development fallback when the external Gemini LLM isn't
        # installed. This avoids import-time failures while you iterate locally.
        if ChatGoogleGenerativeAI is None:
            class _DevFallbackLLM:
                async def ainvoke(self, messages):
                    class _Resp:
                        content = "[dev-fallback] LLM unavailable - install langchain_google_genai to enable"
                    return _Resp()

            self.llm = _DevFallbackLLM()
            logger.warning("ChatGoogleGenerativeAI not installed - using development fallback LLM")
        else:
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.gemini.model,
                temperature=self.config.gemini.temperature,
                google_api_key=self.config.gemini.api_key
            )
        self.personality_service = get_personality_service()
        logger.info("GeminiChatService initialized")
    
    async def send_message(
        self, 
        user_id: str, 
        message: str,
        include_history: bool = False,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message and get personality-aware response.
        
        Args:
            user_id: The user's ID
            message: The user's message
            include_history: Whether to include chat history (future feature)
            session_id: Optional session ID for tracking conversations
            
        Returns:
            Dict containing response, personality context, and metadata
        """
        try:
            logger.info(f"Processing message for user {user_id}")
            
            # Load personality context
            personality_data = await self._load_personality_context(user_id)
            
            # Analyze user message for mood and sentiment
            mood_sentiment = await self._analyze_mood_sentiment(message)
            
            # Create system prompt
            system_prompt = self._create_system_prompt(personality_data)
            
            # Build messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message)
            ]
            
            # Get response from Gemini
            logger.debug(f"Sending to Gemini: {message[:50]}...")
            response = await self.llm.ainvoke(messages)
            
            # Convert personality context to dict for serialization
            personality_context_dict = None
            if personality_data:
                # Create a simple, JSON-serializable summary
                personality_context_dict = {
                    "user_id": personality_data.user_id,
                    "has_assessment": personality_data.has_assessment,
                    "has_llm_context": personality_data.llm_context is not None
                }
                
                # Add personality scores if available
                if personality_data.personality_profile:
                    personality_context_dict["personality_scores"] = {
                        "openness": personality_data.personality_profile.openness,
                        "conscientiousness": personality_data.personality_profile.conscientiousness,
                        "extraversion": personality_data.personality_profile.extraversion,
                        "agreeableness": personality_data.personality_profile.agreeableness,
                        "neuroticism": personality_data.personality_profile.neuroticism
                    }
            
            result = {
                "response": response.content,
                "has_personality_context": personality_data is not None,
                "personality_context": personality_context_dict,
                "mood_detected": mood_sentiment.get("mood"),
                "sentiment_score": mood_sentiment.get("sentiment_score"),
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "model": self.config.gemini.model
            }
            
            logger.info(f"Response generated successfully for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error in send_message: {e}", exc_info=True)
            raise
    
    async def _load_personality_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Load personality context for the user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Personality context dict or None if not available
        """
        try:
            personality_context = await self.personality_service.get_user_personality_context(user_id)
            
            if personality_context and personality_context.has_assessment and personality_context.llm_context:
                logger.info(f"Personality context loaded for user {user_id}")
                return personality_context
            else:
                logger.warning(f"No personality context found for user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading personality context: {e}")
            return None
    
    def _create_system_prompt(self, personality_data: Optional[Any]) -> str:
        """
        Create system prompt based on personality data.
        
        Args:
            personality_data: The user's personality context (PersonalityContextResponse)
            
        Returns:
            System prompt string
        """
        if personality_data:
            # Get system prompt from the PersonalityContextResponse object
            system_prompt = personality_data.get_system_prompt()
            if system_prompt:
                logger.info(f"Using personalized system prompt (length: {len(system_prompt)} chars)")
                logger.debug(f"System prompt preview: {system_prompt[:200]}...")
                return system_prompt
        
        # Default prompt if no personality context
        logger.info("Using default system prompt (no personality context)")
        return """You are Bondhu, an empathetic AI mental health companion.

Your purpose is to:
- Provide emotional support and understanding
- Listen actively and respond with empathy
- Help users reflect on their thoughts and feelings
- Encourage healthy coping mechanisms
- Never provide medical diagnosis or emergency crisis intervention

You are warm, supportive, and genuinely care about the user's wellbeing.
Your responses should be conversational, non-judgmental, and encouraging.

Remember: You're a companion, not a therapist. If someone is in crisis, encourage them to contact emergency services or a crisis hotline."""
    
    async def _analyze_mood_sentiment(self, message: str) -> Dict[str, Any]:
        """
        Analyze mood and sentiment from user message using simple heuristics.
        
        Args:
            message: User's message text
            
        Returns:
            Dict with mood and sentiment_score
        """
        # Simple keyword-based mood detection
        message_lower = message.lower()
        
        # Mood keywords
        positive_moods = {
            "happy": ["happy", "joy", "excited", "great", "wonderful", "amazing", "fantastic", "good", "better"],
            "grateful": ["thank", "grateful", "appreciate", "blessed"],
            "calm": ["calm", "peaceful", "relaxed", "content", "serene"],
            "motivated": ["motivated", "energized", "inspired", "determined"]
        }
        
        negative_moods = {
            "sad": ["sad", "down", "unhappy", "depressed", "blue", "miserable"],
            "anxious": ["anxious", "worried", "nervous", "stressed", "panic", "overwhelmed"],
            "angry": ["angry", "mad", "frustrated", "annoyed", "irritated", "furious"],
            "lonely": ["lonely", "alone", "isolated", "abandoned"],
            "tired": ["tired", "exhausted", "drained", "weary", "fatigue"]
        }
        
        # Check for moods
        detected_mood = "neutral"
        sentiment_score = 0.5  # neutral baseline
        
        for mood, keywords in positive_moods.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_mood = mood
                sentiment_score = 0.7 + (len([k for k in keywords if k in message_lower]) * 0.05)
                break
        
        if detected_mood == "neutral":
            for mood, keywords in negative_moods.items():
                if any(keyword in message_lower for keyword in keywords):
                    detected_mood = mood
                    sentiment_score = 0.3 - (len([k for k in keywords if k in message_lower]) * 0.05)
                    break
        
        # Clamp sentiment score between 0 and 1
        sentiment_score = max(0.0, min(1.0, sentiment_score))
        
        logger.debug(f"Detected mood: {detected_mood}, sentiment: {sentiment_score:.2f}")
        
        return {
            "mood": detected_mood,
            "sentiment_score": round(sentiment_score, 2)
        }
    
    async def get_chat_history(
        self, 
        user_id: str, 
        limit: int = 20
    ) -> list[Dict[str, Any]]:
        """
        Get recent chat history for a user (future feature).
        
        Args:
            user_id: The user's ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of chat messages
        """
        # TODO: Implement chat history retrieval from Supabase
        logger.warning("Chat history retrieval not yet implemented")
        return []


# Singleton instance
_chat_service: Optional[GeminiChatService] = None


def get_chat_service() -> GeminiChatService:
    """Get or create the singleton chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = GeminiChatService()
    return _chat_service
