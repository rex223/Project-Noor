"""
Simple test for memory extractor functionality
Tests just the memory extraction without database dependencies
"""

import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory_extractor import MemoryExtractor

def test_memory_extraction():
    """Test memory extraction for the user's scenario."""
    
    print("🧠 MEMORY EXTRACTION TEST")
    print("=" * 50)
    
    extractor = MemoryExtractor()
    
    # Test the user's specific scenario
    test_messages = [
        "Hi, I'm 25 years old and I work as a software engineer.",
        "I love anime, especially Re:Zero. My favorite character is Natsuki Subaru.",
        "I also enjoy playing video games, particularly RPGs.",
        "My goal is to learn machine learning and become a data scientist.",
        "I have a brother named John who lives in Tokyo.",
        "I meant the name of the Anime character I mentioned in the last session"
    ]
    
    all_memories = {}
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Message: '{message}'")
        memories = extractor.extract_memories(message)
        
        if memories:
            print(f"   Extracted {len(memories)} memories:")
            for key, data in memories.items():
                print(f"   ✓ {key}: '{data['value']}' [{data['category']}/{data['importance']}]")
                all_memories[key] = data
        else:
            print("   No memories extracted")
    
    print(f"\n📊 SUMMARY")
    print("-" * 20)
    print(f"Total messages: {len(test_messages)}")
    print(f"Total memories extracted: {len(all_memories)}")
    
    # Categorize memories
    high_importance = [k for k, v in all_memories.items() if v['importance'] == 'high']
    medium_importance = [k for k, v in all_memories.items() if v['importance'] == 'medium']
    low_importance = [k for k, v in all_memories.items() if v['importance'] == 'low']
    
    print(f"\nHigh importance memories ({len(high_importance)}):")
    for key in high_importance:
        print(f"  - {key}: {all_memories[key]['value']}")
    
    print(f"\nMedium importance memories ({len(medium_importance)}):")
    for key in medium_importance:
        print(f"  - {key}: {all_memories[key]['value']}")
    
    # Check for character references specifically
    character_refs = [k for k, v in all_memories.items() if 'character' in k.lower()]
    print(f"\n🎯 CHARACTER REFERENCES ({len(character_refs)}):")
    for key in character_refs:
        print(f"  ✓ {key}: {all_memories[key]['value']}")
    
    if character_refs:
        print(f"\n🤖 AI COULD RESPOND:")
        print(f"Based on your previous messages, you mentioned '{all_memories[character_refs[0]]['value']}' as your favorite anime character.")
    else:
        print("\n❌ No character references found - this would be the problem!")
    
    print(f"\n✅ Test completed. Character persistence: {'WORKING' if character_refs else 'NEEDS FIX'}")
    
    return len(character_refs) > 0

if __name__ == "__main__":
    test_memory_extraction()