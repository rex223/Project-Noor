"""
Test script for enhanced memory persistence system
Tests the complete flow of memory extraction, storage, and session initialization
"""

import asyncio
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory_extractor import MemoryExtractor
from core.database.memory_service import get_memory_service
from api.models.schemas import ChatMessageRequest

async def test_enhanced_memory_system():
    """Test the enhanced memory system with session persistence."""
    
    print("🧠 ENHANCED MEMORY SYSTEM TEST")
    print("=" * 50)
    
    # Initialize components
    extractor = MemoryExtractor()
    memory_service = get_memory_service()
    test_user_id = "test-user-123"
    
    # Test messages simulating the user's scenario
    test_messages = [
        "Hi, I'm 25 years old and I work as a software engineer.",
        "I love anime, especially Re:Zero. My favorite character is Natsuki Subaru.",
        "I also enjoy playing video games, particularly RPGs.",
        "My goal is to learn machine learning and become a data scientist.",
        "I have a brother named John who lives in Tokyo.",
    ]
    
    print("📝 PHASE 1: Memory Extraction and Storage")
    print("-" * 30)
    
    # Process each message and extract memories
    all_extracted_memories = {}
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Processing: '{message}'")
        
        memories = extractor.extract_memories(message)
        if memories:
            print(f"   Extracted {len(memories)} memories:")
            for key, memory_data in memories.items():
                print(f"   - {key}: {memory_data['value']} [{memory_data['importance']}]")
            
            # Store memories
            success = memory_service.add_memories_batch(test_user_id, memories)
            print(f"   Storage: {'✅ Success' if success else '❌ Failed'}")
            
            all_extracted_memories.update(memories)
        else:
            print("   No memories extracted")
    
    print(f"\n📊 Total memories extracted: {len(all_extracted_memories)}")
    
    print("\n" + "=" * 50)
    print("🔄 PHASE 2: Session Initialization Test")
    print("-" * 30)
    
    # Test session context generation (simulating new session start)
    print("Generating session context for new conversation...")
    session_context = memory_service.generate_session_context(test_user_id)
    
    if session_context:
        print("✅ Session context generated successfully!")
        print("\n📋 SESSION CONTEXT:")
        print("-" * 20)
        print(session_context)
    else:
        print("❌ No session context generated")
    
    print("\n" + "=" * 50)
    print("🔍 PHASE 3: Memory Retrieval Test")
    print("-" * 30)
    
    # Test important memories retrieval
    important_memories = memory_service.get_important_memories(test_user_id)
    
    print(f"Retrieved {len(important_memories)} important memories:")
    for memory in important_memories:
        importance = memory.get('importance', 'unknown')
        category = memory.get('category', 'unknown')
        print(f"- {memory['key']}: {memory['value']} [{importance}/{category}]")
    
    print("\n" + "=" * 50)
    print("🎯 PHASE 4: Character Reference Scenario")
    print("-" * 30)
    
    # Simulate the user's actual problem - asking about anime character from previous session
    user_query = "I meant the name of the Anime character I mentioned in the last session or previous chat"
    print(f"User query: '{user_query}'")
    
    # Check if we can find character information in stored memories
    character_memories = []
    for memory in important_memories:
        if 'character' in memory['key'].lower() or 'anime' in memory['key'].lower():
            character_memories.append(memory)
    
    if character_memories:
        print("\n✅ Character references found in memory:")
        for mem in character_memories:
            print(f"- {mem['key']}: {mem['value']}")
        
        print(f"\n🤖 AI Response Context:")
        print(f"Based on your stored memories, you mentioned '{character_memories[0]['value']}' as your favorite anime character.")
    else:
        print("\n❌ No character references found in memory")
    
    print("\n" + "=" * 50)
    print("✅ MEMORY PERSISTENCE TEST COMPLETED")
    print("-" * 30)
    
    # Summary
    print(f"📈 Summary:")
    print(f"- Messages processed: {len(test_messages)}")
    print(f"- Memories extracted: {len(all_extracted_memories)}")
    print(f"- Important memories stored: {len(important_memories)}")
    print(f"- Character references: {len(character_memories)}")
    print(f"- Session persistence: {'✅ Working' if session_context else '❌ Failed'}")
    
    return {
        'memories_extracted': len(all_extracted_memories),
        'important_memories': len(important_memories),
        'character_references': len(character_memories),
        'session_context_generated': bool(session_context)
    }

if __name__ == "__main__":
    asyncio.run(test_enhanced_memory_system())