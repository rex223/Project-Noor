"""
Test the exact same flow as the chat endpoint
"""
import logging
from datetime import datetime
import google.generativeai as genai
from core.config import get_config

# Configure logging like the chat endpoint
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_chat_endpoint_flow():
    """Test the exact same steps as the chat endpoint"""
    
    print("=" * 60)
    print("TESTING CHAT ENDPOINT FLOW")
    print("=" * 60)
    
    try:
        # Step 1: Get config (same as chat endpoint)
        print("1. Loading configuration...")
        config = get_config()
        print(f"   ✓ Config loaded")
        print(f"   ✓ API Key: {config.gemini.api_key[:10]}...{config.gemini.api_key[-4:]}")
        print(f"   ✓ Model: {config.gemini.model}")
        print(f"   ✓ Temperature: {config.gemini.temperature}")
        
        # Step 2: Check API key
        if not config.gemini.api_key:
            print("   ❌ No API key found!")
            return False
        
        # Step 3: Configure Gemini (same as get_gemini_model)
        print("2. Configuring Gemini...")
        genai.configure(api_key=config.gemini.api_key)
        print("   ✓ Gemini configured")
        
        # Step 4: Create generation config (same as chat endpoint)
        print("3. Creating generation config...")
        generation_config = {
            "temperature": config.gemini.temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        print("   ✓ Generation config created")
        
        # Step 5: Create model (same as get_gemini_model)
        print("4. Creating model...")
        model = genai.GenerativeModel(
            model_name=config.gemini.model,
            generation_config=generation_config
        )
        print("   ✓ Model created")
        
        # Step 6: Test system prompt (similar to chat endpoint)
        print("5. Testing with system prompt...")
        system_prompt = """You are Bondhu, a caring and empathetic AI companion focused on mental wellness and personal growth.

Your communication style:
- Warm, friendly, and supportive
- Use emojis naturally but not excessively
- Ask thoughtful follow-up questions

Respond to the user's message in a way that makes them feel heard, understood, and supported."""

        # Step 7: Create chat and send message (same as chat endpoint)
        print("6. Creating chat session...")
        chat = model.start_chat(history=[])
        print("   ✓ Chat session created")
        
        print("7. Sending test message...")
        full_prompt = f"{system_prompt}\n\nUser: Hello, how are you?"
        response = chat.send_message(full_prompt)
        
        print("   ✓ Message sent successfully!")
        print(f"   Response: {response.text[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        logger.error(f"Chat flow test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_chat_endpoint_flow()
    
    print("=" * 60)
    if success:
        print("🎉 Chat endpoint flow works perfectly!")
        print("The issue might be in the HTTP request handling or FastAPI setup.")
    else:
        print("❌ Found the issue in the chat flow!")
    print("=" * 60)