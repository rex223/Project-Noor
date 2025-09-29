from datetime import datetime
from typing import Any, Dict, List

from crewai_tools import tool


# ---------- Data Collection Tools ----------

@tool
def music_ingest_tool() -> Dict[str, Any]:
    """Fetches the latest music listening signals for the active user."""
    return {
        "source": "mock_music_service",
        "tracks": [
            {"title": "Skyline Reverie", "artist": "Noorwave", "mood": "uplifting"},
            {"title": "Low Tide", "artist": "Aurora Drift", "mood": "calm"},
        ],
        "ingested_at": datetime.utcnow().isoformat(),
    }


@tool
def video_ingest_tool() -> Dict[str, Any]:
    """Retrieves recent video interactions, with engagement metadata."""
    return {
        "source": "mock_video_service",
        "videos": [
            {"title": "Generative Beats", "duration": 312, "sentiment": "positive"},
            {"title": "Immersive Worlds", "duration": 645, "sentiment": "curious"},
        ],
        "ingested_at": datetime.utcnow().isoformat(),
    }


@tool
def gaming_ingest_tool() -> Dict[str, Any]:
    """Returns recent gameplay sessions and mood signals."""
    return {
        "source": "mock_game_service",
        "sessions": [
            {"game": "Echo Realms", "minutes_played": 48, "affect": "energised"},
            {"game": "Drift Patrol", "minutes_played": 27, "affect": "focused"},
        ],
        "ingested_at": datetime.utcnow().isoformat(),
    }


@tool
def survey_ingest_tool() -> Dict[str, Any]:
    """Collects structured survey / check-in responses."""
    return {
        "source": "in_app_survey",
        "responses": [
            {"question": "Current mood?", "answer": "Optimistic", "confidence": 0.7},
            {"question": "Stress level?", "answer": "Medium", "confidence": 0.5},
        ],
        "ingested_at": datetime.utcnow().isoformat(),
    }


# ---------- Personality Analysis Tools ----------

@tool
def github_profile_tool() -> Dict[str, Any]:
    """Parses GitHub activity for traits and interests."""
    return {
        "username": "mock-user",
        "languages": ["Python", "TypeScript"],
        "recent_projects": ["persona-model", "music-recommender"],
    }


@tool
def email_parser_tool() -> List[Dict[str, Any]]:
    """Extracts salient statements from user-provided emails."""
    return [
        {"subject": "Weekly goals", "tone": "motivated", "key_points": ["Ship demo", "Refine RL loop"]},
        {"subject": "Feedback", "tone": "reflective", "key_points": ["Prefers ambient playlists"]},
    ]


@tool
def persona_vector_store_tool(action: str = "get") -> Dict[str, Any]:
    """
    Retrieves or updates the persona embedding stub.
    action='get' returns the current vector; action='update' simulates a write.
    """
    if action == "update":
        return {"status": "updated", "embedding_id": "persona-v1"}
    return {"embedding_id": "persona-v1", "vector_preview": [0.12, -0.04, 0.33]}


# ---------- Interaction / Memory Tools ----------

@tool
def conversation_memory_tool() -> Dict[str, Any]:
    """Provides the latest conversation state snapshot."""
    return {
        "recent_messages": [
            {"speaker": "user", "text": "Need a chill playlist for deep focus."},
            {"speaker": "bondhu", "text": "On it! Any genre you’re leaning toward?"},
        ]
    }


@tool
def safety_monitor_tool(message: str = "") -> Dict[str, Any]:
    """Runs a placeholder safety screen on the provided message."""
    flagged = any(term in message.lower() for term in ["self-harm", "violence"])
    return {"flagged": flagged, "notes": ["Contains sensitive language"] if flagged else []}


@tool
def sentiment_classifier_tool(text: str) -> Dict[str, Any]:
    """Returns a coarse sentiment score for a message."""
    score = 0.7 if "love" in text.lower() else 0.2 if "hate" in text.lower() else 0.5
    return {"sentiment": score, "label": "positive" if score > 0.6 else "negative" if score < 0.4 else "neutral"}


# ---------- Recommendation Tools ----------

@tool
def rec_catalog_tool() -> Dict[str, Any]:
    """Fetches candidate catalog items for ranking."""
    return {
        "music_candidates": [
            {"id": "track_101", "title": "Midnight Glide", "mood": "focus"},
            {"id": "track_205", "title": "Solar Winds", "mood": "uplift"},
        ],
        "video_candidates": [
            {"id": "vid_33", "title": "Synthwave Voyages", "length": 540},
            {"id": "vid_44", "title": "Mindful Motion", "length": 300},
        ],
    }


@tool
def reinforcement_feedback_tool(feedback: Dict[str, Any]) -> Dict[str, Any]:
    """Placeholder for logging engagement or reward signals."""
    return {"status": "logged", "received": feedback}


@tool
def explanation_builder_tool(recommendation: Dict[str, Any]) -> str:
    """Produces a human-readable rationale for a recommendation card."""
    title = recommendation.get("title", "this item")
    mood = recommendation.get("mood", "your current mood")
    return f"{title} matches {mood} based on your recent activity."