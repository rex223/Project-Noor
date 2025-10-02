"""
Bondhu AI Setup Helper
This script helps you configure your environment variables interactively.
"""

import os
import sys
from pathlib import Path

def get_env_file_path():
    """Get the path to the .env file."""
    return Path(__file__).parent / ".env"

def read_current_env():
    """Read current .env file content."""
    env_file = get_env_file_path()
    if env_file.exists():
        with open(env_file, 'r') as f:
            return f.read()
    return ""

def update_env_value(content: str, key: str, value: str) -> str:
    """Update or add an environment variable in the content."""
    lines = content.split('\n')
    updated = False
    
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            updated = True
            break
    
    if not updated:
        lines.append(f"{key}={value}")
    
    return '\n'.join(lines)

def main():
    print("🚀 Bondhu AI Environment Setup Helper")
    print("=" * 50)
    print()
    
    # Read current environment
    current_content = read_current_env()
    
    print("I'll help you configure the essential environment variables.")
    print("Press Enter to skip any field you don't want to set right now.")
    print()
    
    # Essential configurations
    essential_configs = [
        {
            "key": "SUPABASE_URL",
            "prompt": "🗄️  Enter your Supabase URL (e.g., https://your-project.supabase.co):",
            "example": "https://abcdefghijk.supabase.co"
        },
        {
            "key": "SUPABASE_KEY",
            "prompt": "🔑 Enter your Supabase anon key:",
            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        },
        {
            "key": "GEMINI_API_KEY",
            "prompt": "🤖 Enter your Google Gemini API key:",
            "example": "AIzaSyABC123def456..."
        }
    ]
    
    # Optional configurations
    optional_configs = [
        {
            "key": "OPENAI_API_KEY",
            "prompt": "🤖 Enter your OpenAI API key (optional - fallback):",
            "example": "sk-proj-abc123..."
        },
        {
            "key": "ANTHROPIC_API_KEY",
            "prompt": "🧠 Enter your Anthropic API key (optional):",
            "example": "sk-ant-api03-abc123..."
        },
        {
            "key": "SPOTIFY_CLIENT_ID",
            "prompt": "🎵 Enter your Spotify Client ID (optional):",
            "example": "1234567890abcdef1234567890abcdef"
        },
        {
            "key": "SPOTIFY_CLIENT_SECRET",
            "prompt": "🎵 Enter your Spotify Client Secret (optional):",
            "example": "1234567890abcdef1234567890abcdef"
        },
        {
            "key": "YOUTUBE_API_KEY",
            "prompt": "📺 Enter your YouTube Data API key (optional):",
            "example": "AIzaSyABC123def456..."
        },
        {
            "key": "STEAM_API_KEY",
            "prompt": "🎮 Enter your Steam API key (optional):",
            "example": "1234567890ABCDEF1234567890ABCDEF"
        }
    ]
    
    updated_content = current_content
    
    # Configure essential settings
    print("📋 ESSENTIAL CONFIGURATION:")
    print("-" * 30)
    
    for config in essential_configs:
        print(f"\n{config['prompt']}")
        print(f"   Example: {config['example']}")
        value = input("   Value: ").strip()
        
        if value:
            updated_content = update_env_value(updated_content, config['key'], value)
            print(f"   ✅ {config['key']} configured")
        else:
            print(f"   ⏭️  {config['key']} skipped")
    
    # Configure optional settings
    print(f"\n📋 OPTIONAL CONFIGURATION:")
    print("-" * 30)
    print("These are for additional features. You can set them up later.")
    
    setup_optional = input("\nWould you like to configure optional integrations now? (y/N): ").strip().lower()
    
    if setup_optional in ['y', 'yes']:
        for config in optional_configs:
            print(f"\n{config['prompt']}")
            print(f"   Example: {config['example']}")
            value = input("   Value: ").strip()
            
            if value:
                updated_content = update_env_value(updated_content, config['key'], value)
                print(f"   ✅ {config['key']} configured")
            else:
                print(f"   ⏭️  {config['key']} skipped")
    
    # Set some defaults
    updated_content = update_env_value(updated_content, "ENVIRONMENT", "development")
    updated_content = update_env_value(updated_content, "API_DEBUG", "true")
    updated_content = update_env_value(updated_content, "LOG_LEVEL", "INFO")
    updated_content = update_env_value(updated_content, "SECRET_KEY", "your-development-secret-key-change-in-production")
    
    # Save the updated content
    env_file = get_env_file_path()
    with open(env_file, 'w') as f:
        f.write(updated_content)
    
    print(f"\n🎉 Configuration saved to {env_file}")
    print("\n📋 NEXT STEPS:")
    print("1. Review your .env file and make any additional changes")
    print("2. Run the integration test: python test_personality_integration.py")
    print("3. Start the server: python main.py")
    print("4. Visit: http://localhost:8000/docs for API documentation")
    
    print(f"\n💡 TIP: You can run this setup script again anytime to update your configuration.")

if __name__ == "__main__":
    main()