"""
Test multilingual system prompt with Gemini
"""

import asyncio
from core.chat.gemini_service import GeminiChatService

async def test_multilingual_chat():
    """Test chat in multiple languages."""
    
    # Initialize service
    service = GeminiChatService()
    
    # Test user ID (replace with actual user who has personality assessment)
    user_id = "8eebd292-186f-4afd-a33f-ef57ae0e1d17"
    
    print("=" * 80)
    print("MULTILINGUAL CHAT TEST")
    print("=" * 80)
    
    # Test 1: English
    print("\n📝 Test 1: English Message")
    print("-" * 80)
    message_en = "I'm feeling a bit stressed today"
    print(f"User: {message_en}")
    
    result = await service.send_message(user_id, message_en)
    print(f"\nBondhu: {result['response']}")
    print(f"Mood: {result.get('mood_detected', 'N/A')}")
    print(f"Sentiment: {result.get('sentiment_score', 'N/A')}")
    
    # Test 2: Bengali
    print("\n\n📝 Test 2: Bengali Message")
    print("-" * 80)
    message_bn = "আজ আমার মন খুব খারাপ"
    print(f"User: {message_bn}")
    
    result = await service.send_message(user_id, message_bn)
    print(f"\nBondhu: {result['response']}")
    print(f"Mood: {result.get('mood_detected', 'N/A')}")
    print(f"Sentiment: {result.get('sentiment_score', 'N/A')}")
    
    # Test 3: Hindi
    print("\n\n📝 Test 3: Hindi Message")
    print("-" * 80)
    message_hi = "मैं बहुत चिंतित हूं"
    print(f"User: {message_hi}")
    
    result = await service.send_message(user_id, message_hi)
    print(f"\nBondhu: {result['response']}")
    print(f"Mood: {result.get('mood_detected', 'N/A')}")
    print(f"Sentiment: {result.get('sentiment_score', 'N/A')}")
    
    # Test 4: Language Switching
    print("\n\n📝 Test 4: Mixed Language (Code-Switching)")
    print("-" * 80)
    message_mixed = "Today was tough, আমি খুব ক্লান্ত"
    print(f"User: {message_mixed}")
    
    result = await service.send_message(user_id, message_mixed)
    print(f"\nBondhu: {result['response']}")
    print(f"Mood: {result.get('mood_detected', 'N/A')}")
    print(f"Sentiment: {result.get('sentiment_score', 'N/A')}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    print("\n✅ Expected Behavior:")
    print("1. English message → Response in English with 'friend' terminology")
    print("2. Bengali message → Response in Bengali with 'বন্ধু' terminology")
    print("3. Hindi message → Response in Hindi with 'दोस्त' terminology")
    print("4. Mixed language → Response naturally mixing both languages")

if __name__ == "__main__":
    asyncio.run(test_multilingual_chat())
