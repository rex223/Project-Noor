"""
Quick test script using Supabase Python client directly.
This bypasses asyncpg to test basic connectivity.
"""

import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_supabase_client():
    """Test Supabase client directly."""
    print("🔍 Testing Supabase client...")
    
    try:
        from supabase import create_client
        
        # Get config values
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ Missing SUPABASE_URL or SUPABASE_KEY in environment")
            return False
        
        print(f"✅ URL: {url}")
        print(f"✅ Key: {key[:20]}...")
        
        # Create client
        supabase = create_client(url, key)
        print("✅ Supabase client created")
        
        # Test connection with a simple query
        result = supabase.table('personality_profiles').select('count').execute()
        print(f"✅ Query executed successfully")
        
        # Try to count records
        try:
            count_result = supabase.table('personality_profiles').select('id', count='exact').execute()
            total_count = count_result.count
            print(f"✅ Total users in personality_profiles: {total_count}")
            
            # Get users with assessments
            assessment_result = supabase.table('personality_profiles').select('id', 'full_name', 'has_completed_personality_assessment').eq('has_completed_personality_assessment', True).execute()
            
            if assessment_result.data:
                print(f"✅ Users with assessments: {len(assessment_result.data)}")
                for user in assessment_result.data[:3]:  # Show first 3
                    print(f"   - {user.get('full_name', 'Unknown')} (ID: {user['id'][:8]}...)")
                
                # Return first user ID for testing
                return assessment_result.data[0]['id']
            else:
                print("⚠️  No users with completed assessments found")
                return None
                
        except Exception as e:
            print(f"⚠️  Query error (might be permissions): {e}")
            return None
            
    except Exception as e:
        print(f"❌ Supabase client error: {e}")
        return False

def test_personality_data(user_id):
    """Test fetching personality data for a specific user."""
    print(f"\n🔍 Testing personality data for user: {user_id[:8]}...")
    
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        supabase = create_client(url, key)
        
        # Get user's complete personality data
        result = supabase.table('personality_profiles').select('*').eq('id', user_id).execute()
        
        if result.data:
            user_data = result.data[0]
            print(f"✅ User data retrieved: {user_data.get('full_name', 'Unknown')}")
            print(f"   - Openness: {user_data.get('personality_openness', 'N/A')}")
            print(f"   - Conscientiousness: {user_data.get('personality_conscientiousness', 'N/A')}")
            print(f"   - Extraversion: {user_data.get('personality_extraversion', 'N/A')}")
            print(f"   - Agreeableness: {user_data.get('personality_agreeableness', 'N/A')}")
            print(f"   - Neuroticism: {user_data.get('personality_neuroticism', 'N/A')}")
            
            # Check LLM context
            llm_context = user_data.get('personality_llm_context')
            if llm_context:
                system_prompt = llm_context.get('systemPrompt', '')
                print(f"   - LLM Context: {len(system_prompt)} characters")
                if system_prompt:
                    print(f"   - Preview: {system_prompt[:100]}...")
            
            return True
        else:
            print("❌ No data found for user")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching personality data: {e}")
        return False

def main():
    """Run tests."""
    print("🚀 Quick Supabase Connection Test")
    print("=" * 40)
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test Supabase client
    sample_user_id = test_supabase_client()
    
    if sample_user_id:
        # Test personality data
        if test_personality_data(sample_user_id):
            print(f"\n🎉 Success! Everything is working.")
            print(f"✅ Sample user ID: {sample_user_id}")
            print("\n📝 Next steps:")
            print("1. Try starting the server: python main.py")
            print("2. Visit: http://localhost:8000/docs")
        else:
            print("\n⚠️  Basic connection works, but couldn't fetch personality data.")
    else:
        print("\n❌ Connection test failed. Check your Supabase settings.")

if __name__ == "__main__":
    main()