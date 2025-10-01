"""
Test script to verify Gemini API key configuration
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test if Gemini API key works for server-side requests"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Create model - use the same model as your app
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        print("✅ Model created successfully")
        
        # Test simple request
        response = model.generate_content("Say hello in one word")
        
        print(f"✅ API call successful!")
        print(f"Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("GEMINI API KEY TEST")
    print("=" * 60)
    
    success = test_gemini_api()
    
    print("=" * 60)
    if success:
        print("🎉 Your Gemini API key is working correctly!")
        print("The issue might be elsewhere in your application.")
    else:
        print("❌ Your Gemini API key has restrictions or other issues.")
        print("Please check your Google Cloud Console settings.")
    print("=" * 60)