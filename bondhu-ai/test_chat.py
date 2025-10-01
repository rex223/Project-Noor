"""
Quick test for chat functionality
Tests the complete chat flow with personality context
"""

import asyncio
import sys
from core.chat.gemini_service import get_chat_service

async def test_chat():
    """Test chat with a user who has personality profile."""
    
    print("🧪 Testing Bondhu AI Chat System")
    print("=" * 50)
    
    # Use a real user ID from your database
    test_user_id = "10d8ffac-be0d-4c82-97d0-84d183c2567c"  # From your earlier test
    test_message = "Hi Bondhu, I've been feeling a bit stressed lately. Can you help?"
    
    try:
        # Get chat service
        chat_service = get_chat_service()
        print(f"✅ Chat service initialized")
        print(f"   Model: {chat_service.config.gemini.model}")
        print()
        
        # Send message
        print(f"👤 User message: {test_message}")
        print("⏳ Processing...")
        
        result = await chat_service.send_message(test_user_id, test_message)
        
        print()
        print("=" * 50)
        print("🤖 Bondhu's Response:")
        print(result['response'])
        print("=" * 50)
        print()
        print(f"✅ Has personality context: {result['has_personality_context']}")
        print(f"✅ Timestamp: {result['timestamp']}")
        print(f"✅ Model: {result['model']}")
        
        if result['has_personality_context']:
            print("✅ Personality-aware response generated!")
        else:
            print("⚠️  No personality context (user may not have completed assessment)")
        
        print()
        print("✅ Chat test PASSED!")
        
    except Exception as e:
        print(f"❌ Chat test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_chat())
