"""
Diagnostic script to identify startup issues
"""
import sys
import traceback

print("=" * 60)
print("BONDHU AI STARTUP DIAGNOSTICS")
print("=" * 60)

# Test 1: Basic imports
print("\n1. Testing basic imports...")
try:
    import os
    print("   ✓ os")
    import logging
    print("   ✓ logging")
    from dotenv import load_dotenv
    print("   ✓ dotenv")
    load_dotenv()
    print("   ✓ .env loaded")
except Exception as e:
    print(f"   ✗ Basic imports failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Check for .env file
print("\n2. Checking for .env file...")
if os.path.exists(".env"):
    print("   ✓ .env file exists")
else:
    print("   ✗ .env file NOT found - this is likely the problem!")
    print("   → Copy .env.example to .env and fill in your API keys")

# Test 3: Check critical environment variables
print("\n3. Checking critical environment variables...")
critical_vars = {
    "SUPABASE_URL": os.getenv("SUPABASE_URL"),
    "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "SPOTIFY_CLIENT_ID": os.getenv("SPOTIFY_CLIENT_ID"),
    "SPOTIFY_CLIENT_SECRET": os.getenv("SPOTIFY_CLIENT_SECRET"),
    "YOUTUBE_API_KEY": os.getenv("YOUTUBE_API_KEY"),
}

missing_vars = []
for var, value in critical_vars.items():
    if value:
        print(f"   ✓ {var}: {'*' * 10}...{value[-4:]}")
    else:
        print(f"   ✗ {var}: NOT SET")
        missing_vars.append(var)

# Test 4: Try loading individual configs
print("\n4. Testing configuration classes...")
try:
    from core.config.settings import DatabaseConfig
    print("   Testing DatabaseConfig...")
    db_config = DatabaseConfig()
    print("   ✓ DatabaseConfig loaded")
except Exception as e:
    print(f"   ✗ DatabaseConfig failed: {e}")
    traceback.print_exc()

try:
    from core.config.settings import GeminiConfig
    print("   Testing GeminiConfig...")
    gemini_config = GeminiConfig()
    print("   ✓ GeminiConfig loaded")
except Exception as e:
    print(f"   ✗ GeminiConfig failed: {e}")
    traceback.print_exc()

try:
    from core.config.settings import SpotifyConfig
    print("   Testing SpotifyConfig...")
    spotify_config = SpotifyConfig()
    print("   ✓ SpotifyConfig loaded")
except Exception as e:
    print(f"   ✗ SpotifyConfig failed: {e}")
    traceback.print_exc()

try:
    from core.config.settings import YouTubeConfig
    print("   Testing YouTubeConfig...")
    youtube_config = YouTubeConfig()
    print("   ✓ YouTubeConfig loaded")
except Exception as e:
    print(f"   ✗ YouTubeConfig failed: {e}")
    traceback.print_exc()

try:
    from core.config.settings import SteamConfig
    print("   Testing SteamConfig...")
    steam_config = SteamConfig()
    print("   ✓ SteamConfig loaded")
except Exception as e:
    print(f"   ✗ SteamConfig failed: {e}")
    traceback.print_exc()

# Test 5: Try loading full config
print("\n5. Testing full BondhuConfig...")
try:
    from core.config.settings import BondhuConfig
    config = BondhuConfig()
    print("   ✓ BondhuConfig loaded successfully")
except Exception as e:
    print(f"   ✗ BondhuConfig failed: {e}")
    traceback.print_exc()

# Test 6: Try importing orchestrator
print("\n6. Testing orchestrator import...")
try:
    from core.orchestrator import PersonalityOrchestrator
    print("   ✓ PersonalityOrchestrator imported")
except Exception as e:
    print(f"   ✗ PersonalityOrchestrator import failed: {e}")
    traceback.print_exc()

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
if missing_vars:
    print(f"\n⚠ MISSING ENVIRONMENT VARIABLES ({len(missing_vars)}):")
    for var in missing_vars:
        print(f"   - {var}")
    print("\n📝 ACTION REQUIRED:")
    print("   1. Create .env file from .env.example")
    print("   2. Fill in the missing API keys")
    print("   3. Run this diagnostic again")
else:
    print("\n✓ All critical environment variables are set")
    print("  If startup still fails, check the detailed errors above")

print("=" * 60)
