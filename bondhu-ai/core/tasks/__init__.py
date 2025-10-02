"""
Background tasks module for Bondhu AI
Handles async processing of music, video, personality analysis, etc.
"""

from core.tasks.personality import (
    analyze_chat_sentiment_batch,
    analyze_all_users_sentiment,
    update_personality_from_activity
)

__all__ = [
    'analyze_chat_sentiment_batch',
    'analyze_all_users_sentiment',
    'update_personality_from_activity'
]
