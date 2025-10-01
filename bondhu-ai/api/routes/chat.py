"""
Chat API endpoints for Bondhu AI
Handles real-time chat interactions with personality-aware responses
"""

import logging
import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

from core.chat.gemini_service import get_chat_service
from core.database.supabase_client import get_supabase_client

logger = logging.getLogger("bondhu.api.chat")

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for sending a chat message."""
    message: str = Field(..., min_length=1, max_length=5000, description="User's message")
    user_id: str = Field(..., description="User's unique ID")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")


class ChatResponse(BaseModel):
    """Response model for chat messages."""
    response: str = Field(..., description="AI's response message")
    has_personality_context: bool = Field(..., description="Whether personality context was used")
    timestamp: str = Field(..., description="Response timestamp")
    message_id: Optional[str] = Field(None, description="Stored message ID (if saved)")


class ChatHistoryItem(BaseModel):
    """Single chat history item."""
    id: str
    message: str
    response: str
    has_personality_context: bool
    created_at: str


class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    messages: list[ChatHistoryItem]
    total: int
    user_id: str


# Endpoints
@router.post("/send", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_chat_message(request: ChatRequest):
    """
    Send a chat message and receive personality-aware response.
    
    This endpoint:
    1. Loads the user's personality profile
    2. Generates context-aware system prompt
    3. Sends message to Gemini Pro
    4. Returns empathetic response
    5. Optionally stores in chat history (MVP: disabled)
    
    Args:
        request: ChatRequest with message and user_id
        
    Returns:
        ChatResponse with AI's response and metadata
        
    Raises:
        HTTPException: If message processing fails
    """
    try:
        logger.info(f"Received chat message from user {request.user_id}")
        
        # Generate or use existing session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get chat service
        chat_service = get_chat_service()
        
        # Send message and get response
        result = await chat_service.send_message(
            user_id=request.user_id,
            message=request.message,
            session_id=session_id
        )
        
        # Store in database (optional for MVP)
        message_id = None
        try:
            message_id = await _store_chat_message(
                user_id=request.user_id,
                message=request.message,
                response=result['response'],
                mood_detected=result.get('mood_detected'),
                sentiment_score=result.get('sentiment_score'),
                session_id=result.get('session_id')
            )
            logger.info(f"Chat message stored with ID: {message_id}")
        except Exception as e:
            logger.warning(f"Failed to store chat message: {e}")
            # Continue even if storage fails
        
        return ChatResponse(
            response=result['response'],
            has_personality_context=result['has_personality_context'],
            timestamp=result['timestamp'],
            message_id=message_id
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/history/{user_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: str,
    limit: int = 20,
    offset: int = 0
):
    """
    Get chat history for a user.
    
    Args:
        user_id: User's unique ID
        limit: Maximum number of messages to retrieve (default: 20)
        offset: Number of messages to skip (default: 0)
        
    Returns:
        ChatHistoryResponse with messages and metadata
        
    Raises:
        HTTPException: If history retrieval fails
    """
    try:
        logger.info(f"Fetching chat history for user {user_id}")
        
        supabase = await get_supabase_client()
        
        # Query chat history
        response = supabase.table('chat_history') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('created_at', desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        messages = [
            ChatHistoryItem(
                id=msg['id'],
                message=msg['message'],
                response=msg['response'],
                has_personality_context=msg.get('has_personality_context', False),
                created_at=msg['created_at']
            )
            for msg in response.data
        ]
        
        return ChatHistoryResponse(
            messages=messages,
            total=len(messages),  # TODO: Get actual total count
            user_id=user_id
        )
        
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch chat history: {str(e)}"
        )


@router.delete("/history/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_chat_history(user_id: str):
    """
    Clear all chat history for a user.
    
    Args:
        user_id: User's unique ID
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        logger.info(f"Clearing chat history for user {user_id}")
        
        supabase = await get_supabase_client()
        
        # Delete all chat history
        supabase.table('chat_history') \
            .delete() \
            .eq('user_id', user_id) \
            .execute()
        
        logger.info(f"Chat history cleared for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear chat history: {str(e)}"
        )


# Helper Functions
async def _store_chat_message(
    user_id: str,
    message: str,
    response: str,
    mood_detected: Optional[str],
    sentiment_score: Optional[float],
    session_id: Optional[str]
) -> str:
    """
    Store chat message in database.
    
    Args:
        user_id: User's ID
        message: User's message
        response: AI's response
        mood_detected: Detected mood from user message
        sentiment_score: Sentiment score (0-1)
        session_id: Session ID for conversation tracking
        
    Returns:
        Stored message ID
    """
    supabase = get_supabase_client()
    
    # Insert user message
    user_message = supabase.supabase.table('chat_messages').insert({
        'user_id': user_id,
        'message_text': message,
        'sender_type': 'user',
        'mood_detected': mood_detected,
        'sentiment_score': sentiment_score,
        'session_id': session_id
    }).execute()
    
    # Insert AI response
    ai_message = supabase.supabase.table('chat_messages').insert({
        'user_id': user_id,
        'message_text': response,
        'sender_type': 'ai',
        'mood_detected': None,
        'sentiment_score': None,
        'session_id': session_id
    }).execute()
    
    return ai_message.data[0]['id']


@router.get("/health")
async def chat_health_check():
    """Health check endpoint for chat service."""
    try:
        chat_service = get_chat_service()
        return {
            "status": "healthy",
            "service": "chat",
            "model": chat_service.config.gemini.model,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "chat",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
