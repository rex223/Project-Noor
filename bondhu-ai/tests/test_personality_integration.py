"""
Test script to verify integration with existing Supabase personality data.
Run this script to test the complete personality context system.
"""

import asyncio
import os
import sys
from typing import Dict, Any
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import our modules
try:
    from core.database.personality_service import get_personality_service
    from core.database.supabase_client import get_supabase_client
    from core.config.settings import get_config
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the bondhu-ai directory")
    sys.exit(1)


async def test_database_connection():
    """Test basic database connection."""
    print("🔍 Testing database connection...")
    
    try:
        db_client = get_supabase_client()
        pool = await db_client.get_connection_pool()
        
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            if result == 1:
                print("✅ Database connection successful!")
                return True
            else:
                print("❌ Database connection failed!")
                return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


async def test_personality_profiles_view():
    """Test the personality_profiles view."""
    print("\n🔍 Testing personality_profiles view...")
    
    try:
        db_client = get_supabase_client()
        pool = await db_client.get_connection_pool()
        
        async with pool.acquire() as conn:
            # Check if view exists and has data
            query = """
            SELECT COUNT(*) as total_users,
                   COUNT(CASE WHEN has_completed_personality_assessment THEN 1 END) as completed_assessments
            FROM personality_profiles
            """
            result = await conn.fetchrow(query)
            
            print(f"✅ Total users in view: {result['total_users']}")
            print(f"✅ Users with completed assessments: {result['completed_assessments']}")
            
            # Get sample user data
            sample_query = """
            SELECT id, full_name, personality_openness, personality_conscientiousness,
                   has_completed_personality_assessment, profile_completion_percentage
            FROM personality_profiles 
            WHERE has_completed_personality_assessment = true
            LIMIT 3
            """
            sample_users = await conn.fetch(sample_query)
            
            print(f"✅ Sample users with assessments:")
            for user in sample_users:
                print(f"  - {user['full_name']} (ID: {user['id'][:8]}...)")
                print(f"    Openness: {user['personality_openness']}, Conscientiousness: {user['personality_conscientiousness']}")
                print(f"    Profile completion: {user['profile_completion_percentage']}%")
            
            return sample_users[0]['id'] if sample_users else None
            
    except Exception as e:
        print(f"❌ Error testing personality_profiles view: {e}")
        return None


async def test_personality_service(user_id: str):
    """Test the personality service with a real user ID."""
    print(f"\n🔍 Testing personality service with user ID: {user_id[:8]}...")
    
    try:
        personality_service = get_personality_service()
        
        # Test getting personality context
        context = await personality_service.get_user_personality_context(user_id)
        
        if context.has_assessment:
            print("✅ Personality context retrieved successfully!")
            print(f"  - User: {context.personality_profile.full_name}")
            print(f"  - Avatar URL: {context.personality_profile.avatar_url}")
            print(f"  - Onboarding completed: {context.onboarding_status.onboarding_completed}")
            print(f"  - Profile completion: {context.onboarding_status.profile_completion_percentage}%")
            
            # Print personality scores
            scores = context.personality_profile.scores
            print(f"  - Personality scores:")
            for trait, score in scores.items():
                level = context.personality_profile.get_trait_level(trait)
                print(f"    {trait.capitalize()}: {score}/100 ({level})")
            
            # Test LLM context
            if context.llm_context:
                print(f"  - LLM system prompt length: {len(context.llm_context.system_prompt)} characters")
                print(f"  - Topic preferences: {context.llm_context.topic_preferences}")
                print(f"  - Conversation style: {context.llm_context.conversation_style[:100]}...")
            
            # Test personality guidelines
            guidelines = personality_service.get_agent_guidelines(context.personality_profile)
            print(f"  - Music guidelines: {guidelines['music_preferences']['genres']}")
            print(f"  - Video guidelines: {guidelines['video_preferences']['content']}")
            
            return True
        else:
            print("❌ No personality assessment found for user")
            return False
            
    except Exception as e:
        print(f"❌ Error testing personality service: {e}")
        return False


async def test_llm_system_prompt(user_id: str):
    """Test LLM system prompt retrieval."""
    print(f"\n🔍 Testing LLM system prompt for user: {user_id[:8]}...")
    
    try:
        personality_service = get_personality_service()
        system_prompt = await personality_service.get_llm_system_prompt(user_id)
        
        if system_prompt:
            print("✅ LLM system prompt retrieved successfully!")
            print(f"  - Length: {len(system_prompt)} characters")
            print(f"  - Preview: {system_prompt[:200]}...")
            
            # Check for key elements in the prompt
            if "Bondhu" in system_prompt:
                print("  ✅ Contains 'Bondhu' identifier")
            if "personality" in system_prompt.lower():
                print("  ✅ Contains personality context")
            if "OCEAN" in system_prompt or "Big Five" in system_prompt:
                print("  ✅ Contains personality model reference")
            
            return True
        else:
            print("❌ No system prompt found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing LLM system prompt: {e}")
        return False


async def test_onboarding_status(user_id: str):
    """Test onboarding status check."""
    print(f"\n🔍 Testing onboarding status for user: {user_id[:8]}...")
    
    try:
        db_client = get_supabase_client()
        status_data = await db_client.check_user_onboarding_status(user_id)
        
        print("✅ Onboarding status retrieved successfully!")
        print(f"  - User exists: {status_data['user_exists']}")
        print(f"  - Onboarding completed: {status_data['onboarding_completed']}")
        print(f"  - Has personality assessment: {status_data['has_personality_assessment']}")
        print(f"  - Profile completion: {status_data.get('profile_completion_percentage', 'N/A')}%")
        
        if status_data.get('personality_completed_at'):
            completed_date = status_data['personality_completed_at']
            print(f"  - Assessment completed on: {completed_date}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing onboarding status: {e}")
        return False


async def test_agent_analysis_storage(user_id: str):
    """Test storing and retrieving agent analysis results."""
    print(f"\n🔍 Testing agent analysis storage for user: {user_id[:8]}...")
    
    try:
        personality_service = get_personality_service()
        
        # Test storing an analysis result
        test_analysis = {
            "agent_type": "music",
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "confidence": "high",
            "insights": {
                "summary": "User shows high openness through diverse music preferences",
                "traits_detected": ["openness", "extraversion"],
                "recommendations": ["Explore world music", "Attend live concerts"]
            },
            "data_sources": ["spotify_listening_history", "manual_preferences"],
            "processing_time": 2.5
        }
        
        success = await personality_service.store_agent_result(
            user_id, "music", test_analysis
        )
        
        if success:
            print("✅ Agent analysis stored successfully!")
            
            # Test retrieving analysis history
            history = await personality_service.db_client.get_agent_analysis_history(user_id, "music")
            
            if history:
                print(f"✅ Retrieved {len(history)} analysis records")
                latest = history[0]
                print(f"  - Latest analysis: {latest['analysis_data']['insights']['summary']}")
            else:
                print("ℹ️ No analysis history found (expected for new data)")
            
            return True
        else:
            print("❌ Failed to store agent analysis")
            return False
            
    except Exception as e:
        print(f"❌ Error testing agent analysis storage: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting Bondhu AI Personality Integration Tests")
    print("=" * 60)
    
    # Test 1: Database connection
    db_ok = await test_database_connection()
    if not db_ok:
        print("❌ Database connection failed. Check your SUPABASE_URL and SUPABASE_KEY in .env")
        return
    
    # Test 2: Personality profiles view
    sample_user_id = await test_personality_profiles_view()
    if not sample_user_id:
        print("❌ No users with personality assessments found. Make sure you have test data.")
        return
    
    # Test 3: Personality service
    service_ok = await test_personality_service(sample_user_id)
    if not service_ok:
        return
    
    # Test 4: LLM system prompt
    await test_llm_system_prompt(sample_user_id)
    
    # Test 5: Onboarding status
    await test_onboarding_status(sample_user_id)
    
    # Test 6: Agent analysis storage (optional - creates test data)
    await test_agent_analysis_storage(sample_user_id)
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed! Check the results above.")
    print(f"✅ Test user ID for further testing: {sample_user_id}")
    print("\n📝 Next steps:")
    print("1. Start the FastAPI server: python main.py")
    print("2. Test API endpoints at: http://localhost:8000/docs")
    print(f"3. Try personality context API: /personality-context/user-context/{sample_user_id}")


if __name__ == "__main__":
    # Check environment variables
    config = get_config()
    if not config.database.url or not config.database.key:
        print("❌ Missing SUPABASE_URL or SUPABASE_KEY in environment variables")
        print("Please check your .env file")
        sys.exit(1)
    
    # Run tests
    asyncio.run(main())