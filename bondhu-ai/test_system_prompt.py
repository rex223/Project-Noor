"""
Test to verify system prompt is being fetched and used correctly.
"""

import asyncio
import sys
from core.database.personality_service import get_personality_service

async def test_system_prompt():
    """Test if system prompt is fetched correctly."""
    
    # Your user ID
    user_id = "8eebd292-186f-4afd-a33f-ef57ae0e1d17"
    
    print(f"Testing system prompt fetch for user: {user_id}\n")
    
    # Get personality service
    service = get_personality_service()
    
    # Get personality context
    print("Fetching personality context...")
    context = await service.get_user_personality_context(user_id)
    
    print(f"\n✅ Has assessment: {context.has_assessment}")
    print(f"✅ Has LLM context: {context.llm_context is not None}")
    
    if context.llm_context:
        system_prompt = context.get_system_prompt()
        if system_prompt:
            print(f"\n✅ System prompt fetched!")
            print(f"Length: {len(system_prompt)} characters")
            print(f"\nFirst 500 characters:")
            print("-" * 80)
            print(system_prompt[:500])
            print("-" * 80)
            
            # Check if it contains personality-specific content
            if "Openness:" in system_prompt:
                print("\n✅ Contains personality scores")
            if "CONVERSATION GUIDELINES" in system_prompt:
                print("✅ Contains conversation guidelines")
            if "topicPreferences" in system_prompt or "Creative projects" in system_prompt:
                print("✅ Contains topic preferences")
                
            return True
        else:
            print("\n❌ System prompt is None")
            return False
    else:
        print("\n❌ No LLM context available")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_system_prompt())
    sys.exit(0 if result else 1)
