"""
Entertainment API endpoints for music, video, and game recommendations.
Integrates with Spotify, YouTube, and other entertainment APIs.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from core.config import get_config
from core.database.supabase_client import get_supabase_client
from core.rl_orchestrator import get_rl_orchestrator
from api.models.schemas import (
    APIResponse,
    EntertainmentRecommendationDB,
    EntertainmentInteraction,
    EntertainmentPreference
)

# Create router
entertainment_router = APIRouter(prefix="/api/v1/entertainment", tags=["entertainment"])

logger = logging.getLogger(__name__)


# Request/Response Models
class MusicRecommendationResponse(BaseModel):
    """Music recommendation with Spotify data."""
    id: str
    type: str = "song"  # song, artist, playlist, genre
    title: str
    artist: Optional[str] = None
    genre: Optional[str] = None
    mood: str
    energy_level: float = Field(..., ge=0.0, le=100.0)
    reasoning: str
    confidence: float = Field(..., ge=0.0, le=100.0)
    spotify_id: Optional[str] = None
    spotify_url: Optional[str] = None
    preview_url: Optional[str] = None
    album_art: Optional[str] = None
    duration_ms: Optional[int] = None


class PersonalityToMusicMapping(BaseModel):
    """Map personality traits to music preferences."""
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float


# Initialize Spotify client
def get_spotify_client():
    """Get authenticated Spotify client."""
    config = get_config()
    
    if not config.spotify.client_id or not config.spotify.client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Spotify API not configured"
        )
    
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=config.spotify.client_id,
            client_secret=config.spotify.client_secret
        )
        return spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    except Exception as e:
        logger.error(f"Failed to initialize Spotify client: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Spotify API error: {str(e)}"
        )


async def get_user_personality(user_id: str) -> Dict[str, float]:
    """Get user's personality traits from database."""
    try:
        supabase = get_supabase_client()
        
        # Fetch personality traits
        response = supabase.table("personality_traits").select("*").eq("user_id", user_id).execute()
        
        if not response.data:
            # Return default neutral personality
            return {
                "openness": 50.0,
                "conscientiousness": 50.0,
                "extraversion": 50.0,
                "agreeableness": 50.0,
                "neuroticism": 50.0
            }
        
        # Convert to dict
        traits = {trait["trait_name"]: float(trait["trait_value"]) for trait in response.data}
        
        return traits
        
    except Exception as e:
        logger.warning(f"Could not fetch personality traits: {e}")
        return {
            "openness": 50.0,
            "conscientiousness": 50.0,
            "extraversion": 50.0,
            "agreeableness": 50.0,
            "neuroticism": 50.0
        }


def map_personality_to_music_features(personality: Dict[str, float]) -> Dict[str, Any]:
    """Map Big Five personality traits to Spotify audio features and genres."""
    
    # Normalize personality scores (0-100 to 0-1)
    openness = personality.get("openness", 50.0) / 100.0
    conscientiousness = personality.get("conscientiousness", 50.0) / 100.0
    extraversion = personality.get("extraversion", 50.0) / 100.0
    agreeableness = personality.get("agreeableness", 50.0) / 100.0
    neuroticism = personality.get("neuroticism", 50.0) / 100.0
    
    # Map to Spotify audio features (0-1 scale)
    features = {
        # High openness → complex, diverse, experimental music
        "acousticness": 0.3 + (openness * 0.4),
        "instrumentalness": 0.1 + (openness * 0.5),
        
        # High extraversion → energetic, danceable music
        "energy": 0.4 + (extraversion * 0.5),
        "danceability": 0.3 + (extraversion * 0.6),
        "loudness": -15 + (extraversion * 10),
        
        # Low neuroticism (high emotional stability) → positive, upbeat music
        "valence": 0.3 + ((1 - neuroticism) * 0.6),
        
        # Conscientiousness → structured, organized music
        "tempo": 100 + (conscientiousness * 60),
    }
    
    # Genre preferences based on personality
    genre_weights = {}
    
    # Openness → experimental, diverse genres
    if openness > 0.6:
        genre_weights.update({
            "jazz": 0.8, "classical": 0.7, "indie": 0.7, 
            "world": 0.8, "experimental": 0.9
        })
    
    # Extraversion → energetic, social genres
    if extraversion > 0.6:
        genre_weights.update({
            "pop": 0.8, "dance": 0.9, "hip-hop": 0.7, 
            "electronic": 0.6, "party": 0.8
        })
    
    # Agreeableness → harmonious, feel-good genres
    if agreeableness > 0.6:
        genre_weights.update({
            "r-n-b": 0.7, "soul": 0.8, "acoustic": 0.6, 
            "singer-songwriter": 0.7
        })
    
    # Low neuroticism → upbeat, positive genres
    if neuroticism < 0.4:
        genre_weights.update({
            "happy": 0.8, "feel-good": 0.9, "summer": 0.7
        })
    
    # High neuroticism → emotional, introspective genres
    if neuroticism > 0.6:
        genre_weights.update({
            "emo": 0.7, "blues": 0.6, "alternative": 0.7, 
            "indie-rock": 0.6
        })
    
    # Conscientiousness → structured genres
    if conscientiousness > 0.6:
        genre_weights.update({
            "classical": 0.7, "country": 0.6, "folk": 0.6
        })
    
    return {
        "audio_features": features,
        "genre_weights": genre_weights
    }


async def store_music_preferences(user_id: str, genres: List[str], audio_features: Dict[str, float]):
    """Store learned music preferences in database."""
    try:
        supabase = get_supabase_client()
        
        # Store genre preferences
        for genre in genres:
            data = {
                "user_id": user_id,
                "preference_type": "music_genre",
                "preference_key": genre,
                "preference_value": genre,
                "preference_score": 75.0,  # Default score
                "learned_from": "personality_analysis",
                "last_updated": datetime.now().isoformat()
            }
            
            # Upsert to avoid duplicates
            supabase.table("entertainment_preferences").upsert(data).execute()
        
        logger.info(f"Stored music preferences for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to store music preferences: {e}")


@entertainment_router.get("/music/recommendations/{user_id}", response_model=APIResponse[List[MusicRecommendationResponse]])
async def get_music_recommendations(
    user_id: str,
    limit: int = Query(default=12, ge=1, le=50),
    mood: Optional[str] = None,
    refresh: bool = False
) -> APIResponse[List[MusicRecommendationResponse]]:
    """
    Get personalized music recommendations based on user's personality.
    Uses RL-optimized parameters for better engagement.
    
    Args:
        user_id: User ID
        limit: Number of recommendations to return
        mood: Optional mood override
        refresh: Force refresh recommendations
        
    Returns:
        List of music recommendations from Spotify
    """
    try:
        # Get Spotify client
        spotify = get_spotify_client()
        
        # Get user's personality traits
        personality = await get_user_personality(user_id)
        
        # Get RL-optimized recommendation parameters
        rl_orchestrator = get_rl_orchestrator()
        
        # Determine time of day
        current_hour = datetime.now().hour
        if current_hour < 6:
            time_of_day = "night"
        elif current_hour < 12:
            time_of_day = "morning"
        elif current_hour < 18:
            time_of_day = "afternoon"
        else:
            time_of_day = "evening"
        
        try:
            rl_params = rl_orchestrator.get_recommendation_params(
                user_id=user_id,
                personality_profile=personality,
                content_type="music",
                mood=mood or "neutral",
                time_of_day=time_of_day
            )
            logger.info(f"Using RL params for user {user_id}: {rl_params}")
        except Exception as rl_error:
            logger.warning(f"Failed to get RL params, using defaults: {rl_error}")
            rl_params = {
                "min_energy": 0.3,
                "max_energy": 0.7,
                "valence": 0.5,
                "genre_count": 3,
                "exploration_rate": 0.3,
                "popularity_min": 20,
                "popularity_max": 80
            }
        
        # Map personality to music features (baseline)
        music_mapping = map_personality_to_music_features(personality)
        audio_features = music_mapping["audio_features"]
        genre_weights = music_mapping["genre_weights"]
        
        # Apply RL adjustments to audio features
        # RL params override/adjust the personality-based features
        audio_features["energy"] = (rl_params["min_energy"] + rl_params["max_energy"]) / 2
        audio_features["valence"] = rl_params["valence"]
        
        # Get top genres based on weights, limited by RL genre_count
        top_genres = sorted(genre_weights.items(), key=lambda x: x[1], reverse=True)[:rl_params["genre_count"]]
        genre_seeds = [genre for genre, _ in top_genres]
        
        # If exploration rate is high, add random genres
        if rl_params["exploration_rate"] > 0.5 and len(genre_seeds) < 5:
            available_genres = ["pop", "rock", "jazz", "electronic", "indie", "hip-hop", "classical"]
            remaining_genres = [g for g in available_genres if g not in genre_seeds]
            import random
            random.shuffle(remaining_genres)
            genre_seeds.extend(remaining_genres[:5 - len(genre_seeds)])
        
        recommendations = []
        
        # Get recommendations from Spotify
        try:
            # Use Spotify's recommendation engine with RL-optimized parameters
            results = spotify.recommendations(
                seed_genres=genre_seeds[:5] if genre_seeds else ["pop"],  # Spotify max 5 seeds
                limit=limit,
                min_energy=rl_params["min_energy"],
                max_energy=rl_params["max_energy"],
                target_valence=rl_params["valence"],
                target_danceability=audio_features["danceability"],
                target_acousticness=audio_features["acousticness"],
                target_instrumentalness=audio_features["instrumentalness"],
                min_popularity=rl_params["popularity_min"],
                max_popularity=rl_params["popularity_max"]
            )
            
            # Process each track
            for idx, track in enumerate(results.get("tracks", [])):
                # Extract track info
                artists = ", ".join([artist["name"] for artist in track.get("artists", [])])
                album = track.get("album", {})
                images = album.get("images", [])
                album_art = images[0]["url"] if images else None
                
                # Determine mood based on audio features
                track_audio = spotify.audio_features(track["id"])[0] if track.get("id") else {}
                energy = track_audio.get("energy", 0.5) * 100 if track_audio else 50
                valence = track_audio.get("valence", 0.5) * 100 if track_audio else 50
                
                if valence > 70 and energy > 70:
                    track_mood = "energetic"
                elif valence > 70:
                    track_mood = "happy"
                elif energy > 70:
                    track_mood = "intense"
                elif valence < 30:
                    track_mood = "melancholic"
                else:
                    track_mood = "calm"
                
                # Calculate confidence based on personality match
                confidence = 70 + (idx * -2) if idx < 10 else 50  # Higher confidence for top results
                
                recommendation = MusicRecommendationResponse(
                    id=track.get("id", str(uuid4())),
                    type="song",
                    title=track.get("name", "Unknown Track"),
                    artist=artists,
                    genre=genre_seeds[0] if genre_seeds else "pop",
                    mood=mood or track_mood,
                    energy_level=energy,
                    reasoning=f"Based on your personality profile, this {track_mood} track matches your preferences for {genre_seeds[0] if genre_seeds else 'music'} with {int(energy)}% energy",
                    confidence=confidence,
                    spotify_id=track.get("id"),
                    spotify_url=track.get("external_urls", {}).get("spotify"),
                    preview_url=track.get("preview_url"),
                    album_art=album_art,
                    duration_ms=track.get("duration_ms")
                )
                
                recommendations.append(recommendation)
                
                # Store recommendation in database
                try:
                    supabase = get_supabase_client()
                    db_recommendation = {
                        "id": str(uuid4()),
                        "user_id": user_id,
                        "recommendation_type": "music",
                        "content_id": track.get("id", ""),
                        "title": recommendation.title,
                        "description": f"by {artists}",
                        "url": recommendation.spotify_url,
                        "thumbnail_url": album_art,
                        "metadata": {
                            "artist": artists,
                            "genre": recommendation.genre,
                            "energy_level": recommendation.energy_level,
                            "mood": recommendation.mood,
                            "duration_ms": recommendation.duration_ms,
                            "rl_params": rl_params,  # Store RL parameters used
                            "time_of_day": time_of_day
                        },
                        "agent_reasoning": recommendation.reasoning,
                        "confidence_score": recommendation.confidence,
                        "personality_match_score": confidence,
                        "mood_context": recommendation.mood,
                        "category": "music",
                        "created_at": datetime.now().isoformat(),
                        "is_active": True
                    }
                    
                    supabase.table("entertainment_recommendations").insert(db_recommendation).execute()
                except Exception as db_error:
                    logger.warning(f"Failed to store recommendation in DB: {db_error}")
        
        except Exception as spotify_error:
            logger.error(f"Spotify API error: {spotify_error}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Spotify API error: {str(spotify_error)}"
            )
        
        # Store music preferences
        await store_music_preferences(user_id, genre_seeds, audio_features)
        
        return APIResponse[List[MusicRecommendationResponse]](
            success=True,
            data=recommendations,
            message=f"Generated {len(recommendations)} music recommendations based on your personality"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Music recommendations error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate music recommendations: {str(e)}"
        )


# ============================================================================
# VIDEO RECOMMENDATIONS (YouTube Data API v3)
# ============================================================================

class VideoRecommendationResponse(BaseModel):
    """Video recommendation with YouTube data."""
    id: str
    type: str = "youtube"  # youtube, movie, tv_show, documentary
    title: str
    creator: Optional[str] = None
    duration_minutes: Optional[int] = None
    genre: str
    mood_match: str
    reasoning: str
    confidence: float = Field(..., ge=0.0, le=100.0)
    platform: str = "YouTube"
    youtube_url: Optional[str] = None
    thumbnail: Optional[str] = None
    view_count: Optional[int] = None
    channel_name: Optional[str] = None
    published_at: Optional[str] = None


def map_personality_to_video_categories(personality: Dict[str, float]) -> Dict[str, Any]:
    """Map Big Five personality traits to YouTube video categories and search terms."""
    
    # Normalize personality scores (0-100 to 0-1)
    openness = personality.get("openness", 50.0) / 100.0
    conscientiousness = personality.get("conscientiousness", 50.0) / 100.0
    extraversion = personality.get("extraversion", 50.0) / 100.0
    agreeableness = personality.get("agreeableness", 50.0) / 100.0
    neuroticism = personality.get("neuroticism", 50.0) / 100.0
    
    # Category weights based on personality
    category_weights = {}
    search_terms = []
    
    # High openness → Educational, Documentary, Creative content
    if openness > 0.6:
        category_weights.update({
            "Education": 0.9,
            "Science & Technology": 0.8,
            "Film & Animation": 0.7,
            "Travel & Events": 0.7,
            "People & Blogs": 0.6
        })
        search_terms.extend([
            "documentary", "science explained", "art tutorial",
            "philosophy", "creative process", "world cultures"
        ])
    
    # High extraversion → Entertainment, Music, Social content
    if extraversion > 0.6:
        category_weights.update({
            "Entertainment": 0.9,
            "Music": 0.8,
            "Comedy": 0.8,
            "Sports": 0.7,
            "Gaming": 0.6
        })
        search_terms.extend([
            "funny videos", "music videos", "vlogs",
            "party", "social experiments", "pranks"
        ])
    
    # High agreeableness → Inspiring, Wholesome, Helping content
    if agreeableness > 0.6:
        category_weights.update({
            "Nonprofits & Activism": 0.8,
            "Howto & Style": 0.7,
            "People & Blogs": 0.7,
            "Pets & Animals": 0.6
        })
        search_terms.extend([
            "inspiring stories", "helping others", "wholesome",
            "kindness", "motivational", "animal rescue"
        ])
    
    # High conscientiousness → Educational, How-to, Structured content
    if conscientiousness > 0.6:
        category_weights.update({
            "Education": 0.9,
            "Howto & Style": 0.8,
            "Science & Technology": 0.7,
            "News & Politics": 0.6
        })
        search_terms.extend([
            "tutorial", "how to", "step by step",
            "productivity", "organize", "learn"
        ])
    
    # Low neuroticism (emotionally stable) → Positive, Uplifting content
    if neuroticism < 0.4:
        search_terms.extend([
            "positive", "uplifting", "feel good",
            "success stories", "happiness", "good news"
        ])
    
    # High neuroticism → Deep, Emotional, Reflective content
    if neuroticism > 0.6:
        category_weights.update({
            "Film & Animation": 0.7,
            "Music": 0.6,
            "People & Blogs": 0.6
        })
        search_terms.extend([
            "emotional", "deep thoughts", "meaningful",
            "introspective", "personal stories"
        ])
    
    # Default categories if none selected
    if not category_weights:
        category_weights = {
            "Entertainment": 0.7,
            "Education": 0.6,
            "Music": 0.5
        }
        search_terms = ["trending", "popular", "recommended"]
    
    return {
        "category_weights": category_weights,
        "search_terms": search_terms[:10]  # Limit to top 10 search terms
    }


async def search_youtube_videos(
    api_key: str,
    search_terms: List[str],
    max_results: int = 50
) -> List[Dict[str, Any]]:
    """Search YouTube for videos matching personality-based terms."""
    try:
        from googleapiclient.discovery import build
        
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        all_videos = []
        
        # Search for each term (limit to avoid quota issues)
        for term in search_terms[:5]:  # Top 5 terms to save quota
            try:
                search_response = youtube.search().list(
                    q=term,
                    part='id,snippet',
                    maxResults=min(10, max_results),
                    type='video',
                    videoDuration='medium',  # 4-20 minutes
                    relevanceLanguage='en',
                    safeSearch='moderate',
                    order='relevance'
                ).execute()
                
                for item in search_response.get('items', []):
                    if item['id']['kind'] == 'youtube#video':
                        all_videos.append({
                            'video_id': item['id']['videoId'],
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description'],
                            'channel_name': item['snippet']['channelTitle'],
                            'thumbnail': item['snippet']['thumbnails']['high']['url'],
                            'published_at': item['snippet']['publishedAt'],
                            'search_term': term
                        })
                
            except Exception as search_error:
                logger.warning(f"YouTube search failed for term '{term}': {search_error}")
                continue
        
        return all_videos[:max_results]
        
    except ImportError:
        logger.error("google-api-python-client not installed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YouTube API client not available. Install google-api-python-client."
        )
    except Exception as e:
        logger.error(f"YouTube API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"YouTube API error: {str(e)}"
        )


async def store_video_preferences(user_id: str, categories: List[str], search_terms: List[str]):
    """Store learned video preferences in database."""
    try:
        supabase = get_supabase_client()
        
        # Store category preferences
        for category in categories:
            data = {
                "user_id": user_id,
                "preference_type": "video_category",
                "preference_key": category.lower().replace(" ", "_"),
                "preference_value": category,
                "preference_score": 75.0,
                "learned_from": "personality_analysis",
                "last_updated": datetime.now().isoformat()
            }
            
            supabase.table("entertainment_preferences").upsert(data).execute()
        
        logger.info(f"Stored video preferences for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to store video preferences: {e}")


@entertainment_router.get("/video/recommendations/{user_id}", response_model=APIResponse[List[VideoRecommendationResponse]])
async def get_video_recommendations(
    user_id: str,
    limit: int = Query(default=12, ge=1, le=50),
    mood: Optional[str] = None,
    refresh: bool = False
) -> APIResponse[List[VideoRecommendationResponse]]:
    """
    Get personalized video recommendations from YouTube based on user's personality.
    Uses RL-optimized parameters for better engagement.
    
    Args:
        user_id: User ID
        limit: Number of recommendations to return
        mood: Optional mood override
        refresh: Force refresh recommendations
        
    Returns:
        List of video recommendations from YouTube
    """
    try:
        config = get_config()
        
        if not config.youtube.api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="YouTube API not configured"
            )
        
        # Get user's personality traits
        personality = await get_user_personality(user_id)
        
        # Get RL-optimized recommendation parameters
        rl_orchestrator = get_rl_orchestrator()
        
        # Determine time of day
        current_hour = datetime.now().hour
        if current_hour < 6:
            time_of_day = "night"
        elif current_hour < 12:
            time_of_day = "morning"
        elif current_hour < 18:
            time_of_day = "afternoon"
        else:
            time_of_day = "evening"
        
        try:
            rl_params = rl_orchestrator.get_recommendation_params(
                user_id=user_id,
                personality_profile=personality,
                content_type="video",
                mood=mood or "neutral",
                time_of_day=time_of_day
            )
            logger.info(f"Using RL params for user {user_id}: {rl_params}")
        except Exception as rl_error:
            logger.warning(f"Failed to get RL params, using defaults: {rl_error}")
            rl_params = {
                "min_energy": 0.3,
                "max_energy": 0.7,
                "valence": 0.5,
                "genre_count": 3,
                "exploration_rate": 0.3,
                "popularity_min": 20,
                "popularity_max": 80
            }
        
        # Map personality to video categories and search terms (baseline)
        video_mapping = map_personality_to_video_categories(personality)
        category_weights = video_mapping["category_weights"]
        search_terms = video_mapping["search_terms"]
        
        # Apply RL adjustments to search strategy
        # Limit categories based on RL diversity parameter
        top_categories = sorted(category_weights.items(), key=lambda x: x[1], reverse=True)[:rl_params["genre_count"]]
        
        # Adjust search terms based on energy and novelty
        energy_level = (rl_params["min_energy"] + rl_params["max_energy"]) / 2
        
        # Modify search terms based on RL parameters
        adjusted_search_terms = []
        
        # Energy-based adjustments
        if energy_level > 0.7:
            adjusted_search_terms.extend(["exciting", "intense", "high energy"])
        elif energy_level < 0.3:
            adjusted_search_terms.extend(["calm", "relaxing", "peaceful"])
        
        # Valence-based adjustments
        if rl_params["valence"] > 0.7:
            adjusted_search_terms.extend(["uplifting", "positive", "motivational"])
        elif rl_params["valence"] < 0.3:
            adjusted_search_terms.extend(["deep", "meaningful", "thought-provoking"])
        
        # Exploration rate - add diverse terms
        if rl_params["exploration_rate"] > 0.5:
            adjusted_search_terms.extend(["unique", "different", "unusual", "creative"])
        
        # Combine adjusted terms with personality-based terms
        final_search_terms = adjusted_search_terms + search_terms
        
        # Remove duplicates while preserving order
        seen = set()
        final_search_terms = [t for t in final_search_terms if not (t in seen or seen.add(t))]
        
        # Limit to top terms
        final_search_terms = final_search_terms[:10]
        
        # Limit to top terms
        final_search_terms = final_search_terms[:10]
        
        # Search YouTube for videos with RL-optimized search terms
        videos = await search_youtube_videos(
            api_key=config.youtube.api_key,
            search_terms=final_search_terms,
            max_results=limit
        )
        
        recommendations = []
        
        # Process each video
        for idx, video in enumerate(videos):
            # Determine mood based on search term
            search_term = video.get('search_term', '')
            if any(word in search_term.lower() for word in ['funny', 'comedy', 'happy']):
                video_mood = "uplifting"
            elif any(word in search_term.lower() for word in ['calm', 'relax', 'peaceful']):
                video_mood = "calming"
            elif any(word in search_term.lower() for word in ['exciting', 'intense', 'energy']):
                video_mood = "energetic"
            elif any(word in search_term.lower() for word in ['deep', 'meaningful', 'emotional']):
                video_mood = "reflective"
            else:
                video_mood = "engaging"
            
            # Calculate confidence based on personality match
            confidence = 75 + (idx * -1) if idx < 10 else 50
            
            # Determine genre from category
            genre = top_categories[0][0] if top_categories else "Entertainment"
            
            recommendation = VideoRecommendationResponse(
                id=video['video_id'],
                type="youtube",
                title=video['title'][:100],  # Truncate long titles
                creator=video['channel_name'],
                duration_minutes=None,  # Would need additional API call
                genre=genre,
                mood_match=mood or video_mood,
                reasoning=f"Based on your personality profile, this {video_mood} video about '{search_term}' matches your interests in {genre}",
                confidence=confidence,
                platform="YouTube",
                youtube_url=f"https://www.youtube.com/watch?v={video['video_id']}",
                thumbnail=video['thumbnail'],
                channel_name=video['channel_name'],
                published_at=video['published_at']
            )
            
            recommendations.append(recommendation)
            
            # Store recommendation in database
            try:
                supabase = get_supabase_client()
                db_recommendation = {
                    "id": str(uuid4()),
                    "user_id": user_id,
                    "recommendation_type": "video",
                    "content_id": video['video_id'],
                    "title": recommendation.title,
                    "description": video.get('description', '')[:500],
                    "url": recommendation.youtube_url,
                    "thumbnail_url": recommendation.thumbnail,
                    "metadata": {
                        "channel": video['channel_name'],
                        "genre": recommendation.genre,
                        "mood": recommendation.mood_match,
                        "published_at": video['published_at'],
                        "search_term": search_term,
                        "rl_params": rl_params,  # Store RL parameters used
                        "time_of_day": time_of_day
                    },
                    "agent_reasoning": recommendation.reasoning,
                    "confidence_score": recommendation.confidence,
                    "personality_match_score": confidence,
                    "mood_context": recommendation.mood_match,
                    "category": "video",
                    "created_at": datetime.now().isoformat(),
                    "is_active": True
                }
                
                supabase.table("entertainment_recommendations").insert(db_recommendation).execute()
            except Exception as db_error:
                logger.warning(f"Failed to store video recommendation in DB: {db_error}")
        
        # Store video preferences
        await store_video_preferences(
            user_id,
            [cat for cat, _ in top_categories[:5]],
            search_terms
        )
        
        return APIResponse[List[VideoRecommendationResponse]](
            success=True,
            data=recommendations,
            message=f"Generated {len(recommendations)} video recommendations based on your personality"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video recommendations error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate video recommendations: {str(e)}"
        )


# ============================================================================
# INTERACTION TRACKING FOR REINFORCEMENT LEARNING
# ============================================================================

class InteractionRequest(BaseModel):
    """User interaction with entertainment content for RL training."""
    content_type: str = Field(..., pattern="^(music|video|game)$")
    content_id: str
    interaction_type: str = Field(..., pattern="^(view|play|like|dislike|share|complete|skip)$")
    content_title: Optional[str] = None
    duration_seconds: Optional[int] = None
    completion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    mood_before: Optional[str] = None
    mood_after: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    context: Optional[Dict[str, Any]] = None


async def analyze_interaction_for_personality(
    user_id: str,
    interaction: InteractionRequest
) -> Dict[str, float]:
    """
    Analyze user interaction to infer personality trait adjustments.
    Returns suggested personality score adjustments based on behavior.
    """
    adjustments = {
        "openness": 0.0,
        "conscientiousness": 0.0,
        "extraversion": 0.0,
        "agreeableness": 0.0,
        "neuroticism": 0.0
    }
    
    # Like/Dislike patterns reveal preferences
    if interaction.interaction_type == "like":
        # Liking diverse content → Openness
        if interaction.content_type in ["video", "music"]:
            adjustments["openness"] += 0.5
        
        # Liking social content → Extraversion
        if interaction.context and "social" in str(interaction.context).lower():
            adjustments["extraversion"] += 0.5
    
    elif interaction.interaction_type == "dislike":
        # Disliking content provides negative signal
        adjustments["openness"] -= 0.3
    
    # Completion patterns reveal conscientiousness
    if interaction.completion_percentage:
        if interaction.completion_percentage > 90:
            # High completion rate → Conscientiousness
            adjustments["conscientiousness"] += 0.3
        elif interaction.completion_percentage < 20:
            # Low completion (skipping) → Lower conscientiousness
            adjustments["conscientiousness"] -= 0.2
    
    # Skip behavior
    if interaction.interaction_type == "skip":
        adjustments["conscientiousness"] -= 0.2
        adjustments["openness"] -= 0.1
    
    # Mood changes reveal emotional patterns
    if interaction.mood_before and interaction.mood_after:
        if interaction.mood_before == "sad" and interaction.mood_after == "happy":
            # Positive mood change → Lower neuroticism (more stability)
            adjustments["neuroticism"] -= 0.4
        elif interaction.mood_before == "happy" and interaction.mood_after == "sad":
            # Negative mood change → Higher neuroticism
            adjustments["neuroticism"] += 0.3
    
    # Sharing behavior → Agreeableness & Extraversion
    if interaction.interaction_type == "share":
        adjustments["agreeableness"] += 0.4
        adjustments["extraversion"] += 0.3
    
    return adjustments


@entertainment_router.post("/interactions/{user_id}", response_model=APIResponse[dict])
async def record_interaction(
    user_id: str,
    interaction: InteractionRequest
) -> APIResponse[dict]:
    """
    Record user interaction with entertainment content for RL training.
    
    This endpoint stores user feedback (like/dislike/play/skip) which is used to:
    1. Train reinforcement learning models
    2. Improve recommendation algorithms
    3. Update personality profile based on behavior patterns
    
    Args:
        user_id: User ID
        interaction: Interaction details
        
    Returns:
        Confirmation and personality insights
    """
    try:
        supabase = get_supabase_client()
        
        # Store interaction in database
        interaction_data = {
            "id": str(uuid4()),
            "user_id": user_id,
            "recommendation_id": None,  # Can be linked if available
            "interaction_type": interaction.interaction_type,
            "content_type": interaction.content_type,
            "content_id": interaction.content_id,
            "interaction_data": {
                "title": interaction.content_title,
                "rating": interaction.rating,
                "context": interaction.context
            },
            "duration_seconds": interaction.duration_seconds,
            "completion_percentage": interaction.completion_percentage,
            "mood_before": interaction.mood_before,
            "mood_after": interaction.mood_after,
            "created_at": datetime.now().isoformat()
        }
        
        supabase.table("entertainment_interactions").insert(interaction_data).execute()
        
        # Analyze interaction for personality insights
        personality_adjustments = await analyze_interaction_for_personality(user_id, interaction)
        
        # Store personality insights for future processing
        # These will be aggregated and applied by the personality update pipeline
        try:
            insight_data = {
                "user_id": user_id,
                "interaction_id": interaction_data["id"],
                "trait_adjustments": personality_adjustments,
                "confidence": 0.3,  # Individual interactions have moderate confidence
                "source": "entertainment_interaction",
                "created_at": datetime.now().isoformat()
            }
            
            # Store in a temporary insights table for batch processing
            # (You may need to create this table or store in metadata)
            logger.info(f"Personality adjustments for user {user_id}: {personality_adjustments}")
            
        except Exception as insight_error:
            logger.warning(f"Failed to store personality insights: {insight_error}")
        
        return APIResponse[dict](
            success=True,
            data={
                "interaction_id": interaction_data["id"],
                "stored": True,
                "personality_insights": personality_adjustments,
                "message": "Interaction recorded and will be used to improve your recommendations"
            },
            message=f"Recorded {interaction.interaction_type} interaction"
        )
        
    except Exception as e:
        logger.error(f"Failed to record interaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record interaction: {str(e)}"
        )


@entertainment_router.get("/interactions/{user_id}/stats", response_model=APIResponse[dict])
async def get_interaction_stats(user_id: str) -> APIResponse[dict]:
    """
    Get user's interaction statistics for insights.
    
    Args:
        user_id: User ID
        
    Returns:
        Interaction statistics and patterns
    """
    try:
        supabase = get_supabase_client()
        
        # Fetch all interactions
        response = supabase.table("entertainment_interactions").select("*").eq("user_id", user_id).execute()
        
        interactions = response.data
        
        # Calculate statistics
        stats = {
            "total_interactions": len(interactions),
            "by_type": {},
            "by_content": {},
            "completion_rate": 0.0,
            "like_rate": 0.0,
            "most_engaged_content_type": None,
            "average_session_duration": 0.0
        }
        
        if interactions:
            # Count by interaction type
            for interaction in interactions:
                itype = interaction.get("interaction_type", "unknown")
                ctype = interaction.get("content_type", "unknown")
                
                stats["by_type"][itype] = stats["by_type"].get(itype, 0) + 1
                stats["by_content"][ctype] = stats["by_content"].get(ctype, 0) + 1
            
            # Calculate rates
            likes = stats["by_type"].get("like", 0)
            dislikes = stats["by_type"].get("dislike", 0)
            total_feedback = likes + dislikes
            
            if total_feedback > 0:
                stats["like_rate"] = (likes / total_feedback) * 100
            
            # Most engaged content type
            if stats["by_content"]:
                stats["most_engaged_content_type"] = max(stats["by_content"], key=stats["by_content"].get)
            
            # Average completion
            completions = [i.get("completion_percentage", 0) for i in interactions if i.get("completion_percentage")]
            if completions:
                stats["completion_rate"] = sum(completions) / len(completions)
            
            # Average duration
            durations = [i.get("duration_seconds", 0) for i in interactions if i.get("duration_seconds")]
            if durations:
                stats["average_session_duration"] = sum(durations) / len(durations)
        
        return APIResponse[dict](
            success=True,
            data=stats,
            message="Interaction statistics retrieved"
        )
        
    except Exception as e:
        logger.error(f"Failed to get interaction stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )
