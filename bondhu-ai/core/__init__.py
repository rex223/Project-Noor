"""
Core modules for Bondhu AI system.
"""

# Import only config to avoid circular imports during testing
from .config import *

# Lazy import function for PersonalityOrchestrator to avoid circular imports
def get_orchestrator():
    """Lazy import and return PersonalityOrchestrator to avoid circular imports."""
    from .orchestrator import PersonalityOrchestrator
    return PersonalityOrchestrator

__all__ = [
    # Config exports
    "BondhuConfig",
    "DatabaseConfig", 
    "OpenAIConfig",
    "AnthropicConfig",
    "SpotifyConfig",
    "YouTubeConfig",
    "SteamConfig",
    "AgentConfig",
    "RateLimitConfig",
    "LoggingConfig",
    "PersonalityConfig",
    "get_config",
    "reload_config",
    "config",
    # Orchestrator exports
    "get_orchestrator",
]
