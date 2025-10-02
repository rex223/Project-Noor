"""
Chat API endpoints for Bondhu AI conversational interface.
Integrates personality context with LLM for personalized responses.
"""

import asyncio
import logging
import uuid
import json
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field

from core.chat.gemini_service import get_chat_service
from core.database.supabase_client import get_supabase_client
from core.cache.redis_client import get_redis

logger = logging.getLogger("bondhu.api.chat")

# Cache TTLs (in seconds)
CHAT_HISTORY_CACHE_TTL = 86400  # 24 hours
CHAT_SEARCH_CACHE_TTL = 3600    # 1 hour

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


class ChatSearchRequest(BaseModel):
    """Request model for searching chat history."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    limit: int = Field(default=20, ge=1, le=100, description="Max results to return")


# Cache Helper Functions
def get_chat_history_cache_key(user_id: str, limit: int, offset: int) -> str:
    """Generate cache key for chat history."""
    return f"chat:history:{user_id}:{limit}:{offset}"


def get_chat_search_cache_key(user_id: str, query: str, limit: int) -> str:
    """Generate cache key for chat search."""
    return f"chat:search:{user_id}:{query}:{limit}"


async def invalidate_user_chat_cache(user_id: str):
    """Invalidate all chat caches for a user."""
    try:
        redis = get_redis()
        # Delete all keys matching pattern
        pattern = f"chat:*:{user_id}:*"
        cursor = 0
        deleted = 0
        
        while True:
            cursor, keys = redis.scan(cursor, match=pattern, count=100)
            if keys:
                deleted += redis.delete(*keys)
            if cursor == 0:
                break
                
        logger.info(f"Invalidated {deleted} cache keys for user {user_id}")
    except Exception as e:
        logger.warning(f"Failed to invalidate cache for user {user_id}: {e}")


# Endpoints
@router.post("/send", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_chat_message(request: ChatRequest):
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
        memory_service = get_memory_service()
        memory_extractor = MemoryExtractor()

        # --- Memory Extraction ---
        extracted_memories = memory_extractor.extract_memories(request.message)
        if extracted_memories:
            memory_service.add_memories_batch(request.user_id, extracted_memories)
        
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
        
        # --- Memory Retrieval ---
        # Generate comprehensive session context with important memories  
        session_memory_context = memory_service.generate_session_context(request.user_id)
        
        # Get user's personality context for LLM
        personality_context = await personality_service.get_llm_system_prompt(request.user_id)
        
        # Combine personality context with session memories
        enriched_personality_context = personality_context
        if session_memory_context:
            enriched_personality_context = f"{personality_context}\n\n{session_memory_context}"

        # Get recent conversation history (last 5 messages)
        conversation_history = await _get_conversation_history(request.user_id, session_id)
        
        # Generate AI response using personality-aware LLM
        ai_response_text, personality_insights = await _generate_ai_response(
            user_message=request.message,
            personality_context=enriched_personality_context,
            conversation_history=conversation_history,
            config=config
        )
        
        # Create AI message record
        ai_message = ChatMessage(
            id=str(uuid.uuid4()),
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
            
            # Invalidate cache after storing new message
            await invalidate_user_chat_cache(request.user_id)
            
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
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get("/history/{user_id}", response_model=APIResponse)
async def get_chat_history(
    user_id: str, 
    session_id: Optional[str] = None,
    limit: int = 50
) -> APIResponse:
    """
    Get chat history for a user with Redis caching.
    
    Args:
        user_id: User ID to get history for
        session_id: Optional session ID to filter by
        limit: Maximum number of messages to return
        
    Returns:
        List of chat messages
    """
    try:
        logger.info(f"Fetching chat history for user {user_id}")
        
        # Try cache first
        redis = get_redis()
        cache_key = get_chat_history_cache_key(user_id, limit, offset)
        
        cached_data = redis.get(cache_key)
        if cached_data:
            logger.info(f"Cache HIT for chat history: {cache_key}")
            data = json.loads(cached_data)
            return ChatHistoryResponse(
                messages=[ChatHistoryItem(**msg) for msg in data['messages']],
                total=data['total'],
                user_id=user_id
            )
        
        logger.info(f"Cache MISS for chat history: {cache_key}")
        
        # Query database
        supabase = get_supabase_client()
        
        # Query chat history from chat_messages table
        try:
            response = supabase.supabase.table('chat_messages') \
                .select('*') \
                .eq('user_id', user_id) \
                .order('timestamp', desc=True) \
                .range(offset, offset + limit * 2 - 1) \
                .execute()
            
            logger.info(f"Supabase query returned {len(response.data) if response.data else 0} messages")
        except Exception as db_error:
            logger.error(f"Supabase query failed: {db_error}")
            # Return empty result if query fails
            return ChatHistoryResponse(
                messages=[],
                total=0,
                user_id=user_id
            )
        
        # Group messages into conversation pairs (user message + AI response)
        # First pass: collect all messages by session_id
        sessions = {}
        for msg in (response.data if response.data else []):
            session_id = msg.get('session_id', msg['id'])
            if session_id not in sessions:
                sessions[session_id] = {'user': None, 'ai': None}
            
            if msg['sender_type'] == 'user':
                sessions[session_id]['user'] = msg
            elif msg['sender_type'] == 'ai':
                sessions[session_id]['ai'] = msg
        
        # Second pass: create ChatHistoryItem for complete pairs
        messages = []
        for session_id, pair in sessions.items():
            if pair['user'] and pair['ai']:
                # Use user message timestamp as the conversation timestamp
                messages.append(ChatHistoryItem(
                    id=pair['ai']['id'],
                    message=pair['user']['message_text'],
                    response=pair['ai']['message_text'],
                    has_personality_context=pair['user'].get('mood_detected') is not None,
                    created_at=pair['user']['timestamp']  # Always use user timestamp
                ))
        
        logger.info(f"Created {len(messages)} conversation pairs from {len(sessions)} sessions")
        
        # Sort by timestamp (oldest first for chronological display - oldest at top, newest at bottom)
        messages.sort(key=lambda x: x.created_at, reverse=False)
        
        logger.info(f"Returning {len(messages)} messages in chronological order")
        
        # Cache the result
        result = ChatHistoryResponse(
            messages=messages,
            total=len(messages),  # TODO: Get actual total count
            user_id=user_id
        )
        
        try:
            cache_data = {
                'messages': [msg.model_dump() for msg in messages],
                'total': len(messages),
                'user_id': user_id
            }
            redis.setex(cache_key, CHAT_HISTORY_CACHE_TTL, json.dumps(cache_data))
            logger.info(f"Cached chat history for {CHAT_HISTORY_CACHE_TTL}s: {cache_key}")
        except Exception as cache_err:
            logger.warning(f"Failed to cache chat history: {cache_err}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat history: {str(e)}"
        )


@router.post("/session/initialize", response_model=APIResponse) 
async def initialize_chat_session(user_id: str) -> APIResponse:
    """
    Initialize a new chat session with important user context.
    This endpoint should be called when starting a new conversation
    to ensure the AI has access to important past information.
    
    Args:
        user_id: User ID to initialize session for
        
    Returns:
        Session context and important memories
    """
    try:
        logger.info(f"Clearing chat history for user {user_id}")
        
        supabase = get_supabase_client()
        
        # Delete all chat messages
        supabase.supabase.table('chat_messages') \
            .delete() \
            .eq('user_id', user_id) \
            .execute()
        
        # Invalidate cache
        await invalidate_user_chat_cache(user_id)
        
        logger.info(f"Chat history cleared for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error initializing chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear chat history: {str(e)}"
        )


@router.get("/search/{user_id}", response_model=ChatHistoryResponse)
async def search_chat_history(
    user_id: str,
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    limit: int = Query(default=20, ge=1, le=100)
):
    """
    Search chat history for a user with Redis caching.
    
    Performs case-insensitive search across message and response text.
    
    Args:
        user_id: User's unique ID
        q: Search query string
        limit: Maximum number of results (default: 20, max: 100)
        
    Returns:
        ChatHistoryResponse with matching messages
        
    Raises:
        HTTPException: If search fails
    """
    try:
        logger.info(f"Searching chat history for user {user_id} with query: '{q}'")
        
        # Try cache first
        redis = get_redis()
        cache_key = get_chat_search_cache_key(user_id, q, limit)
        
        cached_data = redis.get(cache_key)
        if cached_data:
            logger.info(f"Cache HIT for chat search: {cache_key}")
            data = json.loads(cached_data)
            return ChatHistoryResponse(
                messages=[ChatHistoryItem(**msg) for msg in data['messages']],
                total=data['total'],
                user_id=user_id
            )
        
        logger.info(f"Cache MISS for chat search: {cache_key}")
        
        # Query database with text search
        supabase = get_supabase_client()
        
        # Search in message_text field (case-insensitive)
        search_term = f"%{q.lower()}%"
        response = supabase.supabase.table('chat_messages') \
            .select('*') \
            .eq('user_id', user_id) \
            .ilike('message_text', search_term) \
            .order('timestamp', desc=True) \
            .limit(limit) \
            .execute()
        
        # Group messages into conversation pairs
        messages = []
        user_messages = {}
        
        for msg in response.data:
            if msg['sender_type'] == 'user':
                user_messages[msg.get('session_id', msg['id'])] = msg
            elif msg['sender_type'] == 'ai':
                session_id = msg.get('session_id', '')
                user_msg = user_messages.get(session_id)
                if user_msg:
                    messages.append(ChatHistoryItem(
                        id=msg['id'],
                        message=user_msg['message_text'],
                        response=msg['message_text'],
                        has_personality_context=user_msg.get('mood_detected') is not None,
                        created_at=user_msg['timestamp']
                    ))
        
        # Cache the result
        result = ChatHistoryResponse(
            messages=messages,
            total=len(messages),
            user_id=user_id
        )
        
        try:
            cache_data = {
                'messages': [msg.model_dump() for msg in messages],
                'total': len(messages),
                'user_id': user_id
            }
            redis.setex(cache_key, CHAT_SEARCH_CACHE_TTL, json.dumps(cache_data))
            logger.info(f"Cached search results for {CHAT_SEARCH_CACHE_TTL}s: {cache_key}")
        except Exception as cache_err:
            logger.warning(f"Failed to cache search results: {cache_err}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching chat history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search chat history: {str(e)}"
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
    
    # Insert user message (timestamp auto-generated by DB)
    user_message = supabase.supabase.table('chat_messages').insert({
        'user_id': user_id,
        'message_text': message,
        'sender_type': 'user',
        'mood_detected': mood_detected,
        'sentiment_score': sentiment_score,
        'session_id': session_id
    }).execute()
    
    logger.info(f"User message stored: {user_message.data[0]['id']}")
    
    # Insert AI response immediately (timestamp auto-generated by DB)
    ai_message = supabase.supabase.table('chat_messages').insert({
        'user_id': user_id,
        'message_text': response,
        'sender_type': 'ai',
        'mood_detected': None,
        'sentiment_score': None,
        'session_id': session_id
    }).execute()
    
    logger.info(f"AI message stored: {ai_message.data[0]['id']}, session: {session_id}")
    
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
    
    try:
        from core.database.supabase_client import get_supabase_client
        client = get_supabase_client()
        
        # Build query
        query = client.supabase.table("chat_messages").select("*").eq("user_id", user_id)
        
        # Filter by session if provided
        if session_id:
            query = query.eq("session_id", session_id)
        
        # Order by timestamp and limit results
        response = query.order("timestamp", desc=True).limit(limit).execute()
        
        # Convert to ChatMessage objects
        messages = []
        for row in reversed(response.data):  # Reverse to get chronological order
            message = ChatMessage(
                id=row.get("id"),
                user_id=row.get("user_id"),
                sender_type=row.get("sender_type"),
                message_text=row.get("message_text"),
                session_id=row.get("session_id"),
                timestamp=datetime.fromisoformat(row.get("timestamp").replace('Z', '+00:00')) if row.get("timestamp") else datetime.now()
            )
            messages.append(message)
        
        return messages
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        return []


async def _store_chat_messages(messages: list[ChatMessage]) -> None:
    """Store chat messages in database."""
    
    try:
        from core.database.supabase_client import get_supabase_client
        client = get_supabase_client()
        
        # Prepare message data for insertion
        message_data = []
        for msg in messages:
            data = {
                "id": msg.id,
                "user_id": msg.user_id,
                "sender_type": msg.sender_type,
                "message_text": msg.message_text,
                "session_id": msg.session_id,
                "timestamp": msg.timestamp.isoformat(),
            }
            
            # Add optional fields if they exist
            if hasattr(msg, 'mood_detected') and msg.mood_detected:
                data["mood_detected"] = msg.mood_detected
            if hasattr(msg, 'sentiment_score') and msg.sentiment_score:
                data["sentiment_score"] = msg.sentiment_score
                
            message_data.append(data)
        
        # Insert messages
        client.supabase.table("chat_messages").insert(message_data).execute()
        logger.info(f"Successfully stored {len(messages)} chat messages to database")
            
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
