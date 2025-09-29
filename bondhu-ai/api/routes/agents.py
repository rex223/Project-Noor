"""
FastAPI routes for agent management and external API integrations.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse, RedirectResponse

from core import get_config
from agents import MusicIntelligenceAgent, VideoIntelligenceAgent, GamingIntelligenceAgent
from api.models.schemas import APIIntegrationStatus, HealthCheckResponse

# Create router
agents_router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

@agents_router.get("/status", response_model=HealthCheckResponse)
async def get_agents_status() -> HealthCheckResponse:
    """
    Get health status of all agents and their integrations.
    
    Returns:
        Health check response with agent and integration status
    """
    try:
        config = get_config()
        
        # Check agent availability
        agents_status = {
            "music": True,  # Agents are always available if properly configured
            "video": True,
            "gaming": True,
            "personality": True
        }
        
        # Check API integrations
        api_integrations = {
            "spotify": bool(config.spotify.client_id and config.spotify.client_secret),
            "youtube": bool(config.youtube.api_key),
            "steam": bool(config.steam.api_key),
            "openai": bool(config.openai.api_key)
        }
        
        # Check database connection (placeholder)
        database_connected = bool(config.database.url and config.database.key)
        
        # Calculate memory usage (placeholder)
        memory_usage = {
            "total": 0.0,
            "agents": 0.0,
            "orchestrator": 0.0
        }
        
        return HealthCheckResponse(
            status="healthy" if all(agents_status.values()) else "degraded",
            agents=agents_status,
            database_connected=database_connected,
            api_integrations=api_integrations,
            memory_usage=memory_usage
        )
        
    except Exception as e:
        logging.error(f"Error getting agents status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )

@agents_router.get("/music/connect")
async def get_spotify_auth_url(user_id: str) -> JSONResponse:
    """
    Get Spotify OAuth authorization URL for music agent integration.
    
    Args:
        user_id: User ID for the integration
        
    Returns:
        Spotify authorization URL
    """
    try:
        # Create temporary music agent to get auth URL
        music_agent = MusicIntelligenceAgent(user_id=user_id)
        auth_url = music_agent.get_spotify_auth_url()
        
        if not auth_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate Spotify authorization URL"
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "auth_url": auth_url,
                "user_id": user_id,
                "service": "spotify"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting Spotify auth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get auth URL: {str(e)}"
        )

@agents_router.get("/music/callback")
async def handle_spotify_callback(
    code: str,
    state: Optional[str] = None,
    user_id: Optional[str] = None
) -> RedirectResponse:
    """
    Handle Spotify OAuth callback and complete authentication.
    
    Args:
        code: Authorization code from Spotify
        state: Optional state parameter
        user_id: User ID for the integration
        
    Returns:
        Redirect to frontend with success/error status
    """
    try:
        if not user_id:
            # Try to extract user_id from state parameter
            # In a real implementation, state would encode the user_id
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID required for callback"
            )
        
        # Create music agent and handle callback
        music_agent = MusicIntelligenceAgent(user_id=user_id)
        success = await music_agent.handle_spotify_callback(code)
        
        if success:
            # Store integration status in database (placeholder)
            # await update_integration_status(user_id, "spotify", True)
            
            # Redirect to frontend success page
            return RedirectResponse(
                url=f"http://localhost:3000/dashboard?spotify_connected=true",
                status_code=status.HTTP_302_FOUND
            )
        else:
            # Redirect to frontend error page
            return RedirectResponse(
                url=f"http://localhost:3000/dashboard?spotify_error=auth_failed",
                status_code=status.HTTP_302_FOUND
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error handling Spotify callback: {e}")
        return RedirectResponse(
            url=f"http://localhost:3000/dashboard?spotify_error=callback_failed",
            status_code=status.HTTP_302_FOUND
        )

@agents_router.post("/music/disconnect/{user_id}")
async def disconnect_spotify(user_id: str) -> JSONResponse:
    """
    Disconnect Spotify integration for a user.
    
    Args:
        user_id: User ID to disconnect
        
    Returns:
        Disconnection confirmation
    """
    try:
        # Remove stored Spotify tokens (placeholder)
        # await remove_spotify_tokens(user_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Spotify disconnected successfully",
                "user_id": user_id,
                "service": "spotify",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logging.error(f"Error disconnecting Spotify: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect: {str(e)}"
        )

@agents_router.post("/video/data/{user_id}")
async def submit_video_data(
    user_id: str,
    video_data: Dict[str, Any]
) -> JSONResponse:
    """
    Submit manual video consumption data for analysis.
    
    Args:
        user_id: User ID submitting data
        video_data: Video consumption data
        
    Returns:
        Submission confirmation
    """
    try:
        # Validate video data
        if not video_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty video data"
            )
        
        # Store video data (placeholder)
        # await store_video_data(user_id, video_data)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Video data submitted successfully",
                "user_id": user_id,
                "data_points": len(video_data.get("favorite_channels", [])),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error submitting video data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit data: {str(e)}"
        )

@agents_router.post("/gaming/data/{user_id}")
async def submit_gaming_data(
    user_id: str,
    gaming_data: Dict[str, Any]
) -> JSONResponse:
    """
    Submit manual gaming data for analysis.
    
    Args:
        user_id: User ID submitting data
        gaming_data: Gaming behavior and preference data
        
    Returns:
        Submission confirmation
    """
    try:
        # Validate gaming data
        if not gaming_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty gaming data"
            )
        
        # Store gaming data (placeholder)
        # await store_gaming_data(user_id, gaming_data)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Gaming data submitted successfully",
                "user_id": user_id,
                "games_count": len(gaming_data.get("favorite_games", [])),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error submitting gaming data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit data: {str(e)}"
        )

@agents_router.get("/{user_id}/integrations", response_model=APIIntegrationStatus)
async def get_user_integrations(user_id: str) -> APIIntegrationStatus:
    """
    Get the current API integration status for a user.
    
    Args:
        user_id: User ID to check integrations for
        
    Returns:
        User's API integration status
    """
    try:
        # Note: In a real implementation, this would fetch from database
        # For now, returning default status
        
        return APIIntegrationStatus(
            user_id=user_id,
            spotify_connected=False,
            youtube_connected=False,
            steam_connected=False
        )
        
    except Exception as e:
        logging.error(f"Error getting user integrations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integrations: {str(e)}"
        )

@agents_router.post("/{agent_type}/{user_id}/reset")
async def reset_agent_data(
    agent_type: str,
    user_id: str
) -> JSONResponse:
    """
    Reset collected data for a specific agent.
    
    Args:
        agent_type: Type of agent (music, video, gaming)
        user_id: User ID to reset data for
        
    Returns:
        Reset confirmation
    """
    try:
        valid_agents = ["music", "video", "gaming"]
        if agent_type not in valid_agents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid agent type. Must be one of: {valid_agents}"
            )
        
        # Reset agent data (placeholder)
        # await reset_agent_data_for_user(user_id, agent_type)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": f"{agent_type.title()} agent data reset successfully",
                "user_id": user_id,
                "agent_type": agent_type,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error resetting agent data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset data: {str(e)}"
        )