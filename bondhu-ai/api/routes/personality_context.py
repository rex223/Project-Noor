"""
Personality context API endpoints for fetching user personality data and LLM context.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from api.models.schemas import APIResponse
from core.database.personality_service import get_personality_service
from core.database.models import (
    PersonalityContextResponse,
    UserPersonalityRequest,
    OnboardingStatus
)

router = APIRouter(prefix="/personality-context", tags=["Personality Context"])


class PersonalityContextRequest(BaseModel):
    """Request for personality context."""
    user_id: str = Field(..., description="User's UUID")
    include_analysis_history: bool = Field(default=False, description="Include agent analysis history")


class LLMContextRequest(BaseModel):
    """Request for LLM context only."""
    user_id: str = Field(..., description="User's UUID")


@router.post("/user-context", response_model=APIResponse)
async def get_user_personality_context(
    request: PersonalityContextRequest,
    personality_service = Depends(get_personality_service)
):
    """
    Get comprehensive personality context for a user.
    
    This endpoint fetches:
    - User's Big Five personality scores
    - Generated LLM context and conversation guidelines
    - Onboarding status
    - Optional agent analysis history
    
    Returns:
        Complete personality context for use by agents and frontend
    """
    try:
        context = await personality_service.get_user_personality_context(
            request.user_id,
            request.include_analysis_history
        )
        
        return APIResponse(
            success=True,
            data=context,
            message="Personality context retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving personality context: {str(e)}"
        )


@router.get("/user-context/{user_id}", response_model=APIResponse)
async def get_user_context_by_id(
    user_id: str,
    include_history: bool = Query(default=False, description="Include analysis history"),
    personality_service = Depends(get_personality_service)
):
    """
    Get user personality context by user ID (GET endpoint).
    
    Args:
        user_id: User's UUID
        include_history: Whether to include agent analysis history
        
    Returns:
        Personality context response
    """
    try:
        context = await personality_service.get_user_personality_context(
            user_id,
            include_history
        )
        
        return APIResponse(
            success=True,
            data=context,
            message="Personality context retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving personality context: {str(e)}"
        )


@router.post("/llm-context", response_model=APIResponse)
async def get_llm_system_prompt(
    request: LLMContextRequest,
    personality_service = Depends(get_personality_service)
):
    """
    Get the LLM system prompt for a specific user.
    
    This endpoint is optimized for quick retrieval of just the system prompt
    for LLM interactions without fetching the full personality context.
    
    Args:
        request: LLM context request with user_id
        
    Returns:
        System prompt string or null if not available
    """
    try:
        system_prompt = await personality_service.get_llm_system_prompt(request.user_id)
        
        return APIResponse[Optional[str]](
            success=True,
            data=system_prompt,
            message="LLM system prompt retrieved successfully" if system_prompt else "No system prompt available"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving LLM system prompt: {str(e)}"
        )


@router.get("/llm-context/{user_id}", response_model=APIResponse)
async def get_llm_prompt_by_id(
    user_id: str,
    personality_service = Depends(get_personality_service)
):
    """
    Get LLM system prompt by user ID (GET endpoint).
    
    Args:
        user_id: User's UUID
        
    Returns:
        System prompt string or null
    """
    try:
        system_prompt = await personality_service.get_llm_system_prompt(user_id)
        
        return APIResponse[Optional[str]](
            success=True,
            data=system_prompt,
            message="LLM system prompt retrieved successfully" if system_prompt else "No system prompt available"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving LLM system prompt: {str(e)}"
        )


@router.get("/onboarding-status/{user_id}", response_model=APIResponse)
async def check_onboarding_status(
    user_id: str,
    personality_service = Depends(get_personality_service)
):
    """
    Check user's onboarding and personality assessment status.
    
    This is useful for determining if a user needs to complete
    personality assessment before using the system.
    
    Args:
        user_id: User's UUID
        
    Returns:
        Onboarding status information
    """
    try:
        # Get the database client from the service
        db_client = personality_service.db_client
        status_data = await db_client.check_user_onboarding_status(user_id)
        status = OnboardingStatus(**status_data)
        
        return APIResponse(
            success=True,
            data=status,
            message="Onboarding status retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking onboarding status: {str(e)}"
        )


class PersonalityGuidelinesResponse(BaseModel):
    """Response for personality guidelines."""
    user_id: str
    has_assessment: bool
    guidelines: Optional[dict] = None
    trait_insights: Optional[dict] = None


@router.get("/guidelines/{user_id}", response_model=APIResponse)
async def get_personality_guidelines(
    user_id: str,
    personality_service = Depends(get_personality_service)
):
    """
    Get personality-based guidelines for agents.
    
    This endpoint provides specific guidance for how agents should
    interact with a user based on their personality assessment.
    
    Args:
        user_id: User's UUID
        
    Returns:
        Personality guidelines and trait insights
    """
    try:
        context = await personality_service.get_user_personality_context(user_id)
        
        if context.has_assessment and context.personality_profile:
            guidelines = personality_service.get_agent_guidelines(context.personality_profile)
            trait_insights = personality_service.get_trait_insights(context.personality_profile)
            
            response_data = PersonalityGuidelinesResponse(
                user_id=user_id,
                has_assessment=True,
                guidelines=guidelines,
                trait_insights=trait_insights
            )
        else:
            response_data = PersonalityGuidelinesResponse(
                user_id=user_id,
                has_assessment=False
            )
        
        return APIResponse(
            success=True,
            data=response_data,
            message="Personality guidelines retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving personality guidelines: {str(e)}"
        )


@router.get("/health")
async def personality_context_health():
    """Health check for personality context service."""
    try:
        personality_service = get_personality_service()
        
        # Test database connection
        test_context = await personality_service.get_user_personality_context("test-user-id")
        
        return {
            "status": "healthy",
            "service": "personality-context",
            "database_accessible": True,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "personality-context",
            "database_accessible": False,
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }
