"""
Chat API endpoints for Bondhu AI conversational interface.
Integrates personality context with LLM for personalized responses.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from core import get_config
from core.database.personality_service import get_personality_service
from api.models.schemas import (
    ChatMessageRequest,
    ChatMessage,
    ChatResponse,
    APIResponse
)

# Create router
chat_router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# Configure logging
logger = logging.getLogger(__name__)

@chat_router.post("/message", response_model=APIResponse[ChatResponse])
async def send_chat_message(request: ChatMessageRequest) -> APIResponse[ChatResponse]:
    """
    Send a chat message and get AI response with personality context.
    
    Args:
        request: Chat message request with user message and context
        
    Returns:
        Chat response with AI reply and personality insights
    """
    start_time = asyncio.get_event_loop().time()
    
    try:
        config = get_config()
        personality_service = get_personality_service()
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Create user message record
        user_message = ChatMessage(
            id=str(uuid.uuid4()),
            user_id=request.user_id,
            sender_type="user",
            message_text=request.message,
            session_id=session_id,
            timestamp=datetime.now()
        )
        
        # Get user's personality context for LLM
        personality_context = await personality_service.get_llm_system_prompt(request.user_id)
        
        # Get recent conversation history (last 5 messages)
        conversation_history = await _get_conversation_history(request.user_id, session_id)
        
        # Generate AI response using personality-aware LLM
        ai_response_text, personality_insights = await _generate_ai_response(
            user_message=request.message,
            personality_context=personality_context,
            conversation_history=conversation_history,
            config=config
        )
        
        # Create AI message record
        ai_message = ChatMessage(
            id=str(uuid.uuid4()),
            user_id=request.user_id,
            sender_type="ai",
            message_text=ai_response_text,
            session_id=session_id,
            timestamp=datetime.now(),
            personality_context=personality_insights
        )
        
        # Store both messages in database
        await _store_chat_messages([user_message, ai_message])
        
        # Extract conversation context keywords
        conversation_context = _extract_conversation_context(
            request.message, 
            ai_response_text, 
            personality_insights
        )
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        chat_response = ChatResponse(
            user_message=user_message,
            ai_response=ai_message,
            personality_insights=personality_insights,
            conversation_context=conversation_context,
            processing_time=processing_time
        )
        
        return APIResponse[ChatResponse](
            success=True,
            data=chat_response,
            message="Chat message processed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )


@chat_router.get("/history/{user_id}", response_model=APIResponse[list[ChatMessage]])
async def get_chat_history(
    user_id: str, 
    session_id: Optional[str] = None,
    limit: int = 50
) -> APIResponse[list[ChatMessage]]:
    """
    Get chat message history for a user.
    
    Args:
        user_id: User ID to get history for
        session_id: Optional session ID to filter by
        limit: Maximum number of messages to return
        
    Returns:
        List of chat messages
    """
    try:
        messages = await _get_conversation_history(user_id, session_id, limit)
        
        return APIResponse[list[ChatMessage]](
            success=True,
            data=messages,
            message=f"Retrieved {len(messages)} chat messages"
        )
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat history: {str(e)}"
        )


async def _generate_ai_response(
    user_message: str,
    personality_context: Optional[str],
    conversation_history: list[ChatMessage],
    config: Any
) -> tuple[str, Dict[str, Any]]:
    """Generate AI response using personality context and LLM."""
    
    try:
        # Import Google Generative AI
        import google.generativeai as genai
        
        # Configure Gemini
        genai.configure(api_key=config.gemini.api_key)
        model = genai.GenerativeModel(config.gemini.model or 'gemini-2.5-pro')
        
        # Build conversation context
        conversation_context = ""
        if conversation_history:
            recent_messages = conversation_history[-6:]  # Last 3 exchanges
            for msg in recent_messages:
                role = "User" if msg.sender_type == "user" else "Bondhu"
                conversation_context += f"{role}: {msg.message_text}\n"
        
        # Build system prompt with personality context
        system_prompt = f"""You are Bondhu, an empathetic AI mental health companion. 

{personality_context or "Use a caring, supportive tone appropriate for mental wellness conversations."}

CONVERSATION HISTORY:
{conversation_context}

GUIDELINES:
- Respond naturally and conversationally
- Show empathy and understanding
- Ask thoughtful follow-up questions when appropriate
- Provide gentle guidance and support
- Keep responses concise but meaningful (2-3 sentences typically)
- Adapt your tone to the user's emotional state

Current user message: "{user_message}"

Respond as Bondhu with care and personality awareness:"""
        
        # Generate response
        response = await asyncio.to_thread(
            model.generate_content,
            system_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=float(config.gemini.temperature or 0.7),
                max_output_tokens=300,
                top_p=0.8,
                top_k=40
            )
        )
        
        ai_response = response.text.strip()
        
        # Extract personality insights (simplified)
        personality_insights = {
            "response_tone": "empathetic",
            "personality_adapted": bool(personality_context),
            "conversation_length": len(conversation_history),
            "user_sentiment": _analyze_sentiment(user_message)
        }
        
        return ai_response, personality_insights
        
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        # Fallback response
        fallback_responses = [
            "I'm here to listen and support you. Tell me more about what's on your mind.",
            "Thank you for sharing that with me. How are you feeling about this situation?",
            "I appreciate you opening up to me. What would be most helpful for you right now?",
            "That sounds meaningful to you. Can you help me understand more about your experience?",
            "I'm glad you feel comfortable sharing with me. What's been weighing on your heart lately?"
        ]
        
        import random
        fallback_response = random.choice(fallback_responses)
        
        return fallback_response, {
            "response_tone": "supportive",
            "fallback_used": True,
            "error": str(e)
        }


async def _get_conversation_history(
    user_id: str, 
    session_id: Optional[str] = None, 
    limit: int = 10
) -> list[ChatMessage]:
    """Get recent conversation history from database."""
    
    # TODO: Implement actual database query
    # For now, return empty list - you can implement this based on your chat_messages table
    
    return []


async def _store_chat_messages(messages: list[ChatMessage]) -> None:
    """Store chat messages in database."""
    
    try:
        # TODO: Implement actual database storage
        # This should store messages in your chat_messages table
        
        logger.info(f"Would store {len(messages)} chat messages to database")
        
        # For now, just log the messages
        for msg in messages:
            logger.info(f"Chat message: {msg.sender_type} - {msg.message_text[:50]}...")
            
    except Exception as e:
        logger.error(f"Error storing chat messages: {e}")
        # Don't raise exception - chat should work even if storage fails


def _analyze_sentiment(message: str) -> str:
    """Simple sentiment analysis of user message."""
    
    positive_words = ['good', 'great', 'happy', 'excited', 'love', 'wonderful', 'amazing', 'better']
    negative_words = ['sad', 'angry', 'upset', 'worried', 'anxious', 'depressed', 'frustrated', 'terrible']
    
    message_lower = message.lower()
    
    positive_count = sum(1 for word in positive_words if word in message_lower)
    negative_count = sum(1 for word in negative_words if word in message_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


def _extract_conversation_context(
    user_message: str, 
    ai_response: str, 
    personality_insights: Dict[str, Any]
) -> list[str]:
    """Extract conversation context keywords."""
    
    # Simple keyword extraction
    keywords = []
    
    # Check for common themes
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ['stress', 'anxiety', 'worried', 'anxious']):
        keywords.append("stress management")
    
    if any(word in message_lower for word in ['goal', 'goals', 'achieve', 'accomplish']):
        keywords.append("goal setting")
    
    if any(word in message_lower for word in ['relationship', 'friends', 'family', 'social']):
        keywords.append("relationships")
    
    if any(word in message_lower for word in ['work', 'job', 'career', 'workplace']):
        keywords.append("work life")
    
    if any(word in message_lower for word in ['sleep', 'tired', 'energy', 'rest']):
        keywords.append("wellness")
    
    # Add default contexts if none found
    if not keywords:
        keywords = ["mental wellness", "personal growth"]
    
    return keywords[:5]  # Limit to 5 keywords