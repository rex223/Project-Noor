"""
FastAPI routes for personality analysis endpoints.
Exposes agent functionality to the Next.js frontend.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse

from core import PersonalityOrchestrator, get_config
from api.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    PersonalityProfile,
    HealthCheckResponse,
    APIIntegrationStatus
)

# Create router
personality_router = APIRouter(prefix="/api/v1/personality", tags=["personality"])

# Global orchestrator instance
orchestrator = None

def get_orchestrator() -> PersonalityOrchestrator:
    """Get or create the global orchestrator instance."""
    global orchestrator
    if orchestrator is None:
        orchestrator = PersonalityOrchestrator()
    return orchestrator

@personality_router.post("/analyze", response_model=AnalysisResponse)
async def trigger_personality_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    survey_responses: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    orchestrator: PersonalityOrchestrator = Depends(get_orchestrator)
) -> AnalysisResponse:
    """
    Trigger comprehensive personality analysis for a user.
    
    Args:
        request: Analysis request with user ID and parameters
        background_tasks: FastAPI background tasks
        survey_responses: Optional survey response data
        conversation_history: Optional conversation history
        orchestrator: Orchestrator dependency
        
    Returns:
        Analysis response with personality profile or status
    """
    try:
        logging.info(f"Starting personality analysis for user {request.user_id}")
        
        # Prepare additional data
        kwargs = {}
        if survey_responses:
            kwargs["survey_data"] = survey_responses
        if conversation_history:
            kwargs["conversation_data"] = conversation_history
        
        # Run analysis
        response = await orchestrator.analyze_personality(request, **kwargs)
        
        # Log completion
        logging.info(f"Personality analysis completed for user {request.user_id} in {response.processing_time:.2f}s")
        
        return response
        
    except Exception as e:
        logging.error(f"Error in personality analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@personality_router.get("/{user_id}", response_model=PersonalityProfile)
async def get_personality_insights(
    user_id: str,
    include_history: bool = False
) -> PersonalityProfile:
    """
    Get personality insights for a specific user.
    
    Args:
        user_id: User ID to get insights for
        include_history: Whether to include historical data
        
    Returns:
        User's personality profile
    """
    try:
        # Note: In a real implementation, this would fetch from database
        # For now, returning a placeholder response
        
        logging.info(f"Fetching personality insights for user {user_id}")
        
        # This would typically query the database for the user's latest personality profile
        # For demonstration, we'll return an error indicating no data
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No personality profile found for user {user_id}. Run analysis first."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching personality insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch insights: {str(e)}"
        )

@personality_router.get("/{user_id}/history")
async def get_personality_history(
    user_id: str,
    limit: int = 10
) -> List[PersonalityProfile]:
    """
    Get personality analysis history for a user.
    
    Args:
        user_id: User ID to get history for
        limit: Maximum number of historical profiles to return
        
    Returns:
        List of historical personality profiles
    """
    try:
        logging.info(f"Fetching personality history for user {user_id}")
        
        # Note: In a real implementation, this would fetch from database
        # For now, returning empty list
        return []
        
    except Exception as e:
        logging.error(f"Error fetching personality history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}"
        )

@personality_router.post("/{user_id}/survey")
async def submit_survey_responses(
    user_id: str,
    survey_responses: Dict[str, Any]
) -> JSONResponse:
    """
    Submit survey responses for personality analysis.
    
    Args:
        user_id: User ID submitting responses
        survey_responses: Survey question responses
        
    Returns:
        Success confirmation
    """
    try:
        logging.info(f"Received survey responses for user {user_id}")
        
        # Note: In a real implementation, this would store in database
        # and potentially trigger automatic analysis
        
        # Validate survey responses
        if not survey_responses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty survey responses"
            )
        
        # Store survey responses (placeholder)
        # await store_survey_responses(user_id, survey_responses)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Survey responses submitted successfully",
                "user_id": user_id,
                "responses_count": len(survey_responses),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error submitting survey responses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit survey: {str(e)}"
        )

@personality_router.get("/{user_id}/status/{thread_id}")
async def get_analysis_status(
    user_id: str,
    thread_id: str,
    orchestrator: PersonalityOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """
    Get the status of a running personality analysis.
    
    Args:
        user_id: User ID for the analysis
        thread_id: Thread ID of the analysis workflow
        orchestrator: Orchestrator dependency
        
    Returns:
        Current status of the analysis
    """
    try:
        status_info = await orchestrator.get_workflow_status(user_id, thread_id)
        return status_info
        
    except Exception as e:
        logging.error(f"Error getting analysis status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )

@personality_router.delete("/{user_id}")
async def delete_personality_data(
    user_id: str,
    confirm: bool = False
) -> JSONResponse:
    """
    Delete all personality data for a user.
    
    Args:
        user_id: User ID to delete data for
        confirm: Confirmation flag to prevent accidental deletion
        
    Returns:
        Deletion confirmation
    """
    try:
        if not confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Deletion must be confirmed with confirm=true parameter"
            )
        
        logging.info(f"Deleting personality data for user {user_id}")
        
        # Note: In a real implementation, this would delete from database
        # await delete_user_personality_data(user_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Personality data deleted successfully",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting personality data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete data: {str(e)}"
        )