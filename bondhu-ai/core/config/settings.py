"""
Core configuration management for Bondhu AI system.
Handles environment variables, API keys, and agent-specific settings.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    url: str = field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    key: str = field(default_factory=lambda: os.getenv("SUPABASE_KEY", ""))
    service_role_key: str = field(default_factory=lambda: os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""))
    
    def __post_init__(self):
        if not self.url or not self.key:
            raise ValueError("Supabase URL and KEY must be provided")

@dataclass
class OpenAIConfig:
    """OpenAI API configuration."""
    api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4"))
    temperature: float = field(default_factory=lambda: float(os.getenv("OPENAI_TEMPERATURE", "0.7")))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("OPENAI_MAX_TOKENS", "2000")))
    
    # OpenAI is now optional since we're using Gemini as primary

@dataclass
class AnthropicConfig:
    """Anthropic Claude API configuration."""
    api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("ANTHROPIC_MAX_TOKENS", "2000")))

@dataclass
class GeminiConfig:
    """Google Gemini API configuration."""
    api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    temperature: float = field(default_factory=lambda: float(os.getenv("GEMINI_TEMPERATURE", "0.7")))
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("Gemini API key must be provided")

@dataclass
class SpotifyConfig:
    """Spotify API configuration."""
    client_id: str = field(default_factory=lambda: os.getenv("SPOTIFY_CLIENT_ID", ""))
    client_secret: str = field(default_factory=lambda: os.getenv("SPOTIFY_CLIENT_SECRET", ""))
    redirect_uri: str = field(default_factory=lambda: os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8000/api/v1/auth/spotify/callback"))
    scope: str = field(default_factory=lambda: os.getenv("SPOTIFY_SCOPE", "user-read-recently-played user-library-read user-top-read user-read-playback-state"))
    
    def __post_init__(self):
        if not self.client_id or not self.client_secret:
            raise ValueError("Spotify Client ID and Secret must be provided")

@dataclass
class YouTubeConfig:
    """YouTube Data API configuration."""
    api_key: str = field(default_factory=lambda: os.getenv("YOUTUBE_API_KEY", ""))
    quota_limit: int = field(default_factory=lambda: int(os.getenv("YOUTUBE_QUOTA_LIMIT", "10000")))
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("YouTube API key must be provided")

@dataclass
class SteamConfig:
    """Steam API configuration."""
    api_key: str = field(default_factory=lambda: os.getenv("STEAM_API_KEY", ""))
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("Steam API key must be provided")

@dataclass
class AgentConfig:
    """Agent-specific configuration."""
    timeout: int = field(default_factory=lambda: int(os.getenv("AGENT_TIMEOUT", "30")))
    max_retries: int = field(default_factory=lambda: int(os.getenv("AGENT_MAX_RETRIES", "3")))
    concurrent_agents: int = field(default_factory=lambda: int(os.getenv("CONCURRENT_AGENTS", "3")))
    memory_limit: int = field(default_factory=lambda: int(os.getenv("AGENT_MEMORY_LIMIT", "1000")))

@dataclass
class RateLimitConfig:
    """Rate limiting configuration for external APIs."""
    spotify_requests_per_minute: int = field(default_factory=lambda: int(os.getenv("SPOTIFY_RPM", "100")))
    youtube_requests_per_minute: int = field(default_factory=lambda: int(os.getenv("YOUTUBE_RPM", "100")))
    steam_requests_per_minute: int = field(default_factory=lambda: int(os.getenv("STEAM_RPM", "200")))
    openai_requests_per_minute: int = field(default_factory=lambda: int(os.getenv("OPENAI_RPM", "3000")))

@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    format: str = field(default_factory=lambda: os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    file_path: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE_PATH"))
    max_file_size: int = field(default_factory=lambda: int(os.getenv("LOG_MAX_FILE_SIZE", "10485760")))  # 10MB
    backup_count: int = field(default_factory=lambda: int(os.getenv("LOG_BACKUP_COUNT", "5")))

@dataclass
class PersonalityConfig:
    """Personality analysis configuration."""
    traits: list = field(default_factory=lambda: ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"])
    confidence_threshold: float = field(default_factory=lambda: float(os.getenv("PERSONALITY_CONFIDENCE_THRESHOLD", "0.6")))
    update_frequency_days: int = field(default_factory=lambda: int(os.getenv("PERSONALITY_UPDATE_FREQUENCY", "7")))
    cross_modal_weight: float = field(default_factory=lambda: float(os.getenv("CROSS_MODAL_WEIGHT", "0.3")))

@dataclass
class BondhuConfig:
    """Main configuration class that aggregates all settings."""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    anthropic: AnthropicConfig = field(default_factory=AnthropicConfig)
    gemini: GeminiConfig = field(default_factory=GeminiConfig)
    spotify: SpotifyConfig = field(default_factory=SpotifyConfig)
    youtube: YouTubeConfig = field(default_factory=YouTubeConfig)
    steam: SteamConfig = field(default_factory=SteamConfig)
    agents: AgentConfig = field(default_factory=AgentConfig)
    rate_limits: RateLimitConfig = field(default_factory=RateLimitConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    personality: PersonalityConfig = field(default_factory=PersonalityConfig)
    
    # API Configuration
    api_host: str = field(default_factory=lambda: os.getenv("API_HOST", "localhost"))
    api_port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    api_debug: bool = field(default_factory=lambda: os.getenv("API_DEBUG", "false").lower() == "true")
    
    # Security
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", ""))
    algorithm: str = field(default_factory=lambda: os.getenv("ALGORITHM", "HS256"))
    access_token_expire_minutes: int = field(default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")))
    
    def __post_init__(self):
        if not self.secret_key:
            import secrets
            self.secret_key = secrets.token_urlsafe(32)
            print("Warning: No SECRET_KEY provided, generated temporary key")

# Global configuration instance
config = BondhuConfig()

def get_config() -> BondhuConfig:
    """Get the global configuration instance."""
    return config

def reload_config() -> BondhuConfig:
    """Reload configuration from environment variables."""
    global config
    config = BondhuConfig()
    return config