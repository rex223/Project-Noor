"""
Simple test script for Bondhu AI database integration.
Tests only the database and personality service components.
"""

import asyncio
import os
import sys
from typing import Dict, Any

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from core.config.settings import get_config
        print("✅ Config module imported")
        
        from core.database.supabase_client import get_supabase_client
        print("✅ Supabase client imported")
        
        from core.database.personality_service import get_personality_service
        print("✅ Personality service imported")
        
        from core.database.models import PersonalityProfile, OnboardingStatus
        print("✅ Database models imported")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

async def test_config():
    """Test configuration loading."""
    print("\n🔍 Testing configuration...")
    
    try:
        from core.config.settings import get_config
        config = get_config()
        
        print(f"✅ API Host: {config.api_host}")
        print(f"✅ API Port: {config.api_port}")
        print(f"✅ Database URL configured: {'Yes' if config.database.url else 'No'}")
        print(f"✅ Database key configured: {'Yes' if config.database.key else 'No'}")
        print(f"✅ OpenAI key configured: {'Yes' if config.openai.api_key else 'No'}")
        
        if not config.database.url or not config.database.key:
            print("❌ Missing Supabase configuration")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def test_database_connection():
    """Test basic database connection."""
    print("\n🔍 Testing database connection...")
    
    try:
        from core.database.supabase_client import get_supabase_client
        
        db_client = get_supabase_client()
        
        # Try to create connection pool
        pool = await db_client.get_connection_pool()
        
        # Test basic query
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
        print("💡 Check your SUPABASE_URL and SUPABASE_KEY in .env file")
        return False

async def test_personality_view():
    """Test the personality_profiles view."""
    print("\n🔍 Testing personality_profiles view...")
    
    try:
        from core.database.supabase_client import get_supabase_client
        
        db_client = get_supabase_client()
        pool = await db_client.get_connection_pool()
        
        async with pool.acquire() as conn:
            # Check if view exists and count users
            query = """
            SELECT COUNT(*) as total_users,
                   COUNT(CASE WHEN has_completed_personality_assessment THEN 1 END) as completed_assessments
            FROM personality_profiles
            """
            result = await conn.fetchrow(query)
            
            print(f"✅ Total users in view: {result['total_users']}")
            print(f"✅ Users with completed assessments: {result['completed_assessments']}")
            
            if result['completed_assessments'] > 0:
                # Get sample user
                sample_query = """
                SELECT id, full_name, personality_openness, personality_conscientiousness
                FROM personality_profiles 
                WHERE has_completed_personality_assessment = true
                LIMIT 1
                """
                sample_user = await conn.fetchrow(sample_query)
                
                if sample_user:
                    print(f"✅ Sample user found: {sample_user['full_name']}")
                    print(f"   - User ID: {sample_user['id']}")
                    print(f"   - Openness: {sample_user['personality_openness']}")
                    print(f"   - Conscientiousness: {sample_user['personality_conscientiousness']}")
                    return str(sample_user['id'])
            else:
                print("⚠️  No users with completed personality assessments found")
                return None
                
    except Exception as e:
        print(f"❌ Error testing personality view: {e}")
        return None

async def test_personality_service(user_id: str):
    """Test the personality service."""
    print(f"\n🔍 Testing personality service with user: {user_id[:8]}...")
    
    try:
        from core.database.personality_service import get_personality_service
        
        service = get_personality_service()
        
        # Test getting personality context
        context = await service.get_user_personality_context(user_id)
        
        if context.has_assessment:
            print("✅ Personality context retrieved!")
            print(f"   - User: {context.personality_profile.full_name}")
            print(f"   - Onboarding completed: {context.onboarding_status.onboarding_completed}")
            
            scores = context.personality_profile.scores
            print("   - Personality scores:")
            for trait, score in scores.items():
                print(f"     {trait}: {score}/100")
            
            # Test LLM context
            if context.llm_context:
                print(f"   - LLM context available: {len(context.llm_context.system_prompt)} chars")
            
            return True
        else:
            print("❌ No personality assessment found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing personality service: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Bondhu AI Simple Database Test")
    print("=" * 50)
    
    # Test 1: Imports
    if not test_imports():
        print("❌ Import test failed. Please check your installation.")
        return
    
    # Test 2: Configuration
    if not await test_config():
        print("❌ Configuration test failed. Please check your .env file.")
        return
    
    # Test 3: Database connection
    if not await test_database_connection():
        print("❌ Database connection failed. Please check your Supabase settings.")
        return
    
    # Test 4: Personality view
    sample_user_id = await test_personality_view()
    if not sample_user_id:
        print("⚠️  No sample user found. The database connection works, but no personality data is available.")
        print("💡 Make sure you have users who completed the personality assessment.")
        return
    
    # Test 5: Personality service
    if await test_personality_service(sample_user_id):
        print("\n🎉 All tests passed!")
        print(f"✅ Sample user ID for API testing: {sample_user_id}")
        print("\n📝 Next steps:")
        print("1. Start the server: python main.py")
        print("2. Test API at: http://localhost:8000/docs")
        print(f"3. Try: /personality-context/user-context/{sample_user_id}")
    else:
        print("❌ Personality service test failed.")

if __name__ == "__main__":
    asyncio.run(main())