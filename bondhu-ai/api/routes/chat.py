"""
Chat API endpoints for real-time conversation with Gemini AI.
"""

import logging
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
import google.generativeai as genai

from core.config import get_config
from core.database.supabase_client import get_supabase_client
from api.models.schemas import APIResponse

# Create router
chat_router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

logger = logging.getLogger(__name__)


# Request/Response Models
class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Request for chat completion."""
    user_id: str
    message: str
    conversation_history: List[ChatMessage] = []
    session_id: Optional[str] = None
    personality_context: bool = True


class ChatResponse(BaseModel):
    """Response from chat completion."""
    message: str
    session_id: str
    timestamp: datetime
    mood_detected: Optional[str] = None
    sentiment_score: Optional[float] = None


# Initialize Gemini
def get_gemini_model():
    """Get configured Gemini model."""
    config = get_config()
    
    if not config.gemini.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API key not configured"
        )
    
    genai.configure(api_key=config.gemini.api_key)
    
    generation_config = {
        "temperature": config.gemini.temperature,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,
    }
    
    return genai.GenerativeModel(
        model_name=config.gemini.model,
        generation_config=generation_config
    )


async def get_personality_context(user_id: str) -> str:
    """
    Get user's personality context for personalized responses.
    Falls back to survey data if no personality traits are available.
    """
    try:
        supabase_wrapper = get_supabase_client()
        supabase = supabase_wrapper.supabase  # Access the raw client
        
        # Method 1: Try to get processed personality traits
        traits_response = supabase.table("personality_traits").select("*").eq("user_id", user_id).execute()
        
        if traits_response.data:
            # Build context from processed traits
            traits = {trait["trait_name"]: trait["trait_value"] for trait in traits_response.data}
            
            context = f"""
User Personality Profile (Processed):
- Openness: {traits.get('openness', 'Unknown')}
- Conscientiousness: {traits.get('conscientiousness', 'Unknown')}
- Extraversion: {traits.get('extraversion', 'Unknown')}
- Agreeableness: {traits.get('agreeableness', 'Unknown')}
- Emotional Stability: {traits.get('emotional_stability', 'Unknown')}

Adapt your communication style based on these personality traits.
"""
            return context.strip()
        
        # Method 2: Fallback to user profile/survey data
        profile_response = supabase.table("personality_profiles").select("*").eq("id", user_id).execute()
        
        if profile_response.data:
            profile = profile_response.data[0]
            
            # Check if user has completed personality assessment
            if profile.get('has_completed_personality_assessment'):
                context = f"""
User Personality Profile (From Assessment):
- Openness: {profile.get('personality_openness', 'Unknown')}
- Conscientiousness: {profile.get('personality_conscientiousness', 'Unknown')}
- Extraversion: {profile.get('personality_extraversion', 'Unknown')}
- Agreeableness: {profile.get('personality_agreeableness', 'Unknown')}
- Neuroticism: {profile.get('personality_neuroticism', 'Unknown')}

Additional Context:
- Full Name: {profile.get('full_name', 'Unknown')}
- Onboarding Status: {'Completed' if profile.get('onboarding_completed') else 'In Progress'}

LLM Context: {profile.get('personality_llm_context', 'No additional context')}

Adapt your communication style based on these personality traits and user information.
"""
                return context.strip()
            
            # Method 3: Basic profile information for new users
            context = f"""
New User Profile:
- Full Name: {profile.get('full_name', 'Unknown')}
- Profile Completion: {profile.get('profile_completion_percentage', 0)}%
- Onboarding Status: {'Completed' if profile.get('onboarding_completed') else 'In Progress'}

Note: This user hasn't completed a personality assessment yet. Use a friendly, welcoming tone 
and consider asking engaging questions to understand their preferences and personality over time.
Be supportive and help them explore the platform features.
"""
            return context.strip()
        
        # Method 4: Complete fallback for truly new users
        return """
New User - No Profile Data:
This appears to be a completely new user with no profile information. 
Use a warm, welcoming tone and introduce yourself as Bondhu, their AI companion.
Focus on helping them get started, understanding their needs, and encouraging 
them to complete their personality assessment for more personalized interactions.
"""
        
    except Exception as e:
        logger.warning(f"Failed to get personality context for user {user_id}: {e}")
        return """
Default Interaction Mode:
Unable to retrieve user personality data. Use a balanced, friendly communication style.
Be helpful, supportive, and adaptable to the user's apparent preferences during the conversation.
"""
        
    except Exception as e:
        logger.warning(f"Could not fetch personality context: {e}")
        return ""


async def store_chat_message(
    user_id: str,
    message: str,
    sender_type: str,
    session_id: str,
    mood: Optional[str] = None,
    sentiment: Optional[float] = None
):
    """Store chat message in database."""
    try:
        supabase_wrapper = get_supabase_client()
        supabase = supabase_wrapper.supabase  # Access the raw client
        
        data = {
            "user_id": user_id,
            "message_text": message,
            "sender_type": sender_type,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "mood_detected": mood,
            "sentiment_score": sentiment
        }
        
        supabase.table("chat_messages").insert(data).execute()
        
    except Exception as e:
        logger.error(f"Failed to store chat message: {e}")


async def analyze_chat_for_personality(user_message: str, ai_response: str) -> Dict[str, float]:
    """
    Analyze chat conversation patterns to infer personality traits.
    Returns personality score adjustments based on communication style.
    """
    adjustments = {
        "openness": 0.0,
        "conscientiousness": 0.0,
        "extraversion": 0.0,
        "agreeableness": 0.0,
        "neuroticism": 0.0
    }
    
    user_lower = user_message.lower()
    
    # Openness indicators
    openness_keywords = ["creative", "imagine", "curious", "wonder", "explore", "learn", "new", "different", "art", "philosophy"]
    if any(keyword in user_lower for keyword in openness_keywords):
        adjustments["openness"] += 0.3
    
    # Conscientiousness indicators
    conscientiousness_keywords = ["plan", "organize", "schedule", "goal", "task", "complete", "finish", "achieve", "work", "productive"]
    if any(keyword in user_lower for keyword in conscientiousness_keywords):
        adjustments["conscientiousness"] += 0.3
    
    # Extraversion indicators
    extraversion_keywords = ["party", "friends", "social", "meet", "talk", "people", "fun", "exciting", "adventure", "energy"]
    if any(keyword in user_lower for keyword in extraversion_keywords):
        adjustments["extraversion"] += 0.3
    
    introversion_keywords = ["alone", "quiet", "peace", "solitude", "recharge", "introspect", "private"]
    if any(keyword in user_lower for keyword in introversion_keywords):
        adjustments["extraversion"] -= 0.3
    
    # Agreeableness indicators
    agreeableness_keywords = ["help", "kind", "care", "support", "friend", "love", "appreciate", "thanks", "grateful", "understand"]
    if any(keyword in user_lower for keyword in agreeableness_keywords):
        adjustments["agreeableness"] += 0.3
    
    # Neuroticism indicators (emotional language)
    negative_emotion_keywords = ["anxious", "worry", "stress", "fear", "nervous", "upset", "sad", "depressed", "overwhelmed"]
    if any(keyword in user_lower for keyword in negative_emotion_keywords):
        adjustments["neuroticism"] += 0.4
    
    positive_emotion_keywords = ["happy", "joy", "excited", "great", "wonderful", "awesome", "calm", "peaceful", "relaxed"]
    if any(keyword in user_lower for keyword in positive_emotion_keywords):
        adjustments["neuroticism"] -= 0.3
    
    # Message length and complexity (Openness)
    word_count = len(user_message.split())
    if word_count > 50:  # Longer, more elaborate messages
        adjustments["openness"] += 0.2
        adjustments["conscientiousness"] += 0.1
    
    # Question-asking behavior (Openness & Agreeableness)
    if "?" in user_message:
        adjustments["openness"] += 0.1
        adjustments["agreeableness"] += 0.1
    
    return adjustments



@chat_router.post("/send", response_model=APIResponse[ChatResponse])
async def send_chat_message(request: ChatRequest) -> APIResponse[ChatResponse]:
    """
    Send a chat message and get AI response using Gemini.
    
    Args:
        request: Chat request with user message and context
        
    Returns:
        AI-generated response with metadata
    """
    try:
        # Generate or use existing session ID
        session_id = request.session_id or str(uuid4())
        
        # Get Gemini model
        model = get_gemini_model()
        
        # Build conversation history for Gemini
        chat_history = []
        for msg in request.conversation_history[-10:]:  # Last 10 messages for context
            # Map roles: frontend sends "assistant" but Gemini expects "model"
            gemini_role = "model" if msg.role == "assistant" else "user"
            chat_history.append({
                "role": gemini_role,
                "parts": [msg.content]
            })
        
        # Get personality context if requested
        system_context = ""
        if request.personality_context:
            personality_ctx = await get_personality_context(request.user_id)
            if personality_ctx:
                system_context = f"\n\n{personality_ctx}\n\n"
                logger.info(f"Using personality context for user {request.user_id}")
            else:
                logger.info(f"No personality context available for user {request.user_id}")
        else:
            logger.info(f"Personality context disabled for user {request.user_id}")
        
        # Build system prompt
        system_prompt = f"""You are Bondhu, a caring and empathetic AI companion focused on mental wellness and personal growth.

Your communication style:
- Warm, friendly, and supportive
- Use emojis naturally but not excessively
- Ask thoughtful follow-up questions
- Provide actionable advice when appropriate
- Be genuine and authentic in your responses
- Adapt to the user's emotional state

{system_context}

Respond to the user's message in a way that makes them feel heard, understood, and supported."""

        # Create chat session
        chat = model.start_chat(history=chat_history)
        
        # Get response from Gemini
        full_prompt = f"{system_prompt}\n\nUser: {request.message}"
        response = chat.send_message(full_prompt)
        
        ai_message = response.text
        
        # Store both messages in database
        await store_chat_message(
            user_id=request.user_id,
            message=request.message,
            sender_type="user",
            session_id=session_id
        )
        
        await store_chat_message(
            user_id=request.user_id,
            message=ai_message,
            sender_type="ai",
            session_id=session_id
        )
        
        # Analyze conversation for personality insights
        personality_adjustments = await analyze_chat_for_personality(request.message, ai_message)
        
        # Store personality insights if there are significant adjustments
        if any(abs(adj) > 0.1 for adj in personality_adjustments.values()):
            try:
                supabase_wrapper = get_supabase_client()
                supabase = supabase_wrapper.supabase  # Access the raw client
                supabase.table("chat_personality_insights").insert({
                    "user_id": request.user_id,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "adjustments": personality_adjustments,
                    "message_context": request.message[:200]  # Store snippet for context
                }).execute()
            except Exception as e:
                logger.error(f"Failed to store personality insights: {e}")
        
        # Create response
        chat_response = ChatResponse(
            message=ai_message,
            session_id=session_id,
            timestamp=datetime.now()
        )
        
        return APIResponse[ChatResponse](
            success=True,
            data=chat_response,
            message="Message sent successfully"
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )


@chat_router.get("/history/{user_id}", response_model=APIResponse[List[ChatMessage]])
async def get_chat_history(
    user_id: str,
    session_id: Optional[str] = None,
    limit: int = 50
) -> APIResponse[List[ChatMessage]]:
    """
    Get chat history for a user.
    
    Args:
        user_id: User ID
        session_id: Optional session ID to filter by
        limit: Maximum number of messages to return
        
    Returns:
        List of chat messages
    """
    try:
        supabase_wrapper = get_supabase_client()
        supabase = supabase_wrapper.supabase  # Access the raw client
        
        query = supabase.table("chat_messages").select("*").eq("user_id", user_id)
        
        if session_id:
            query = query.eq("session_id", session_id)
        
        response = query.order("timestamp", desc=True).limit(limit).execute()
        
        messages = [
            ChatMessage(
                role="assistant" if msg["sender_type"] == "ai" else "user",
                content=msg["message_text"],
                timestamp=msg["timestamp"]
            )
            for msg in reversed(response.data)
        ]
        
        # If no messages found, provide a helpful response for new users
        if not messages:
            return APIResponse[List[ChatMessage]](
                success=True,
                data=[],
                message="No chat history found. This user is ready to start their first conversation!"
            )
        
        return APIResponse[List[ChatMessage]](
            success=True,
            data=messages,
            message=f"Retrieved {len(messages)} messages"
        )
        
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat history: {str(e)}"
        )


@chat_router.delete("/history/{user_id}/{session_id}")
async def delete_chat_session(user_id: str, session_id: str) -> APIResponse[dict]:
    """
    Delete a chat session.
    
    Args:
        user_id: User ID
        session_id: Session ID to delete
        
    Returns:
        Deletion confirmation
    """
    try:
        supabase_wrapper = get_supabase_client()
        supabase = supabase_wrapper.supabase  # Access the raw client
        
        supabase.table("chat_messages").delete().eq("user_id", user_id).eq("session_id", session_id).execute()
        
        return APIResponse[dict](
            success=True,
            data={"deleted": True},
            message="Chat session deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to delete chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chat session: {str(e)}"
        )


@chat_router.post("/personality/update/{user_id}")
async def update_personality_from_insights(user_id: str) -> APIResponse[dict]:
    """
    Aggregate personality insights from chat and entertainment interactions
    and update the user's personality profile.
    
    This endpoint should be called periodically (e.g., daily) to apply
    accumulated personality insights to the user's profile.
    """
    try:
        supabase_wrapper = get_supabase_client()
        supabase = supabase_wrapper.supabase  # Access the raw client
        
        # Get chat personality insights (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        chat_insights = supabase.table("chat_personality_insights")\
            .select("adjustments")\
            .eq("user_id", user_id)\
            .gte("timestamp", thirty_days_ago)\
            .execute()
        
        # Get entertainment interaction insights (last 30 days)
        entertainment_insights = supabase.table("entertainment_interactions")\
            .select("personality_insights")\
            .eq("user_id", user_id)\
            .gte("timestamp", thirty_days_ago)\
            .is_("personality_insights", "not.null")\
            .execute()
        
        # Aggregate all adjustments
        total_adjustments = {
            "openness": 0.0,
            "conscientiousness": 0.0,
            "extraversion": 0.0,
            "agreeableness": 0.0,
            "neuroticism": 0.0
        }
        
        insight_count = 0
        
        # Process chat insights
        for insight in chat_insights.data:
            adjustments = insight.get("adjustments", {})
            for trait, value in adjustments.items():
                if trait in total_adjustments:
                    total_adjustments[trait] += value
                    insight_count += 1
        
        # Process entertainment insights
        for insight in entertainment_insights.data:
            adjustments = insight.get("personality_insights", {})
            for trait, value in adjustments.items():
                if trait in total_adjustments:
                    total_adjustments[trait] += value
                    insight_count += 1
        
        if insight_count == 0:
            return APIResponse(
                success=True,
                data={"updated": False},
                message="No personality insights to process"
            )
        
        # Get current personality scores
        current_profile = supabase.table("user_personality_profiles")\
            .select("*")\
            .eq("user_id", user_id)\
            .single()\
            .execute()
        
        if not current_profile.data:
            return APIResponse(
                success=False,
                data={"updated": False},
                message="User personality profile not found"
            )
        
        # Apply adjustments with dampening factor (to prevent drastic changes)
        dampening_factor = 0.1  # Only apply 10% of accumulated changes
        
        updated_traits = {}
        for trait in total_adjustments.keys():
            current_value = current_profile.data.get(trait, 50.0)
            adjustment = total_adjustments[trait] * dampening_factor
            
            # Clamp between 0 and 100
            new_value = max(0.0, min(100.0, current_value + adjustment))
            updated_traits[trait] = new_value
        
        # Update personality profile
        supabase.table("user_personality_profiles")\
            .update(updated_traits)\
            .eq("user_id", user_id)\
            .execute()
        
        return APIResponse(
            success=True,
            data={
                "updated": True,
                "insights_processed": insight_count,
                "trait_changes": {
                    trait: updated_traits[trait] - current_profile.data.get(trait, 50.0)
                    for trait in updated_traits.keys()
                }
            },
            message=f"Personality profile updated based on {insight_count} insights"
        )
        
    except Exception as e:
        logger.error(f"Error updating personality: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update personality: {str(e)}"
        )


@chat_router.get("/personality-context/{user_id}")
async def get_user_personality_context(user_id: str) -> APIResponse[dict]:
    """
    Test endpoint to check personality context for a user.
    Useful for debugging and verifying personality data retrieval.
    """
    try:
        personality_context = await get_personality_context(user_id)
        
        return APIResponse[dict](
            success=True,
            data={
                "user_id": user_id,
                "personality_context": personality_context,
                "context_length": len(personality_context),
                "has_context": bool(personality_context and personality_context.strip())
            },
            message="Personality context retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting personality context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get personality context: {str(e)}"
        )

