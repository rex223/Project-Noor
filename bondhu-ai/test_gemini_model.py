"""
Quick test to verify Gemini model configuration works
"""

import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from core.config import get_config

async def test_gemini():
    config = get_config()
    
    print(f"Testing Gemini with model: {config.gemini.model}")
    print(f"API Key present: {'Yes' if config.gemini.api_key else 'No'}")
    print(f"Temperature: {config.gemini.temperature}")
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=config.gemini.model,
            temperature=config.gemini.temperature,
            google_api_key=config.gemini.api_key
        )
        
        message = HumanMessage(content="Say hello in one sentence.")
        response = await llm.ainvoke([message])
        
        print(f"\n✅ SUCCESS!")
        print(f"Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_gemini())
