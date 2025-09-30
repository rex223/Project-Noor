"""
API routes module.
"""

from .personality import personality_router
from .agents import agents_router
from .chat import chat_router

__all__ = ["personality_router", "agents_router", "chat_router"]