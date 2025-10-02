import re
from typing import Dict, List
from datetime import datetime

class MemoryExtractor:
    """
    Enhanced memory extractor that captures comprehensive user information including
    personal facts, preferences, life details, and personality traits for persistent recall.
    """

    def __init__(self):
        # Define comprehensive patterns to capture different types of user information
        self.patterns = {
            "favorite": [
                re.compile(r"my favorite (\w+) is (.+)", re.IGNORECASE),
                re.compile(r"i like (\w+) (.+)", re.IGNORECASE),
                re.compile(r"i love (\w+) (.+)", re.IGNORECASE),
                re.compile(r"i prefer (\w+) (.+)", re.IGNORECASE),
                re.compile(r"i enjoy (\w+) (.+)", re.IGNORECASE),
            ],
            "personal_fact": [
                re.compile(r"i am a (.+)", re.IGNORECASE),
                re.compile(r"i work as a (.+)", re.IGNORECASE),
                re.compile(r"i study (.+)", re.IGNORECASE),
                re.compile(r"i'm studying (.+)", re.IGNORECASE),
                re.compile(r"my job is (.+)", re.IGNORECASE),
                re.compile(r"my profession is (.+)", re.IGNORECASE),
                re.compile(r"i live in (.+)", re.IGNORECASE),
                re.compile(r"i'm from (.+)", re.IGNORECASE),
                re.compile(r"my age is (\d+)", re.IGNORECASE),
                re.compile(r"i am (\d+) years old", re.IGNORECASE),
            ],
            "character_reference": [
                re.compile(r"my favorite character is (.+)", re.IGNORECASE),
                re.compile(r"i like the character (.+)", re.IGNORECASE),
                re.compile(r"my favorite anime character is (.+)", re.IGNORECASE),
                re.compile(r"i mentioned (.+) character", re.IGNORECASE),
                re.compile(r"the anime character (.+)", re.IGNORECASE),
                re.compile(r"character named (.+)", re.IGNORECASE),
            ],
            "hobby_interest": [
                re.compile(r"i play (.+)", re.IGNORECASE),
                re.compile(r"i watch (.+)", re.IGNORECASE),
                re.compile(r"i read (.+)", re.IGNORECASE),
                re.compile(r"i listen to (.+)", re.IGNORECASE),
                re.compile(r"my hobby is (.+)", re.IGNORECASE),
                re.compile(r"i'm interested in (.+)", re.IGNORECASE),
                re.compile(r"i collect (.+)", re.IGNORECASE),
            ],
            "relationship": [
                re.compile(r"my (brother|sister|mother|father|parent|friend|boyfriend|girlfriend|husband|wife|partner) is (.+)", re.IGNORECASE),
                re.compile(r"i have a (brother|sister|friend|son|daughter|child) named (.+)", re.IGNORECASE),
                re.compile(r"i'm married to (.+)", re.IGNORECASE),
                re.compile(r"my family (.+)", re.IGNORECASE),
            ],
            "goal_aspiration": [
                re.compile(r"i want to (.+)", re.IGNORECASE),
                re.compile(r"my goal is to (.+)", re.IGNORECASE),
                re.compile(r"i plan to (.+)", re.IGNORECASE),
                re.compile(r"i'm working towards (.+)", re.IGNORECASE),
                re.compile(r"i hope to (.+)", re.IGNORECASE),
            ],
            "dislike": [
                re.compile(r"i hate (.+)", re.IGNORECASE),
                re.compile(r"i don't like (.+)", re.IGNORECASE),
                re.compile(r"i dislike (.+)", re.IGNORECASE),
                re.compile(r"i can't stand (.+)", re.IGNORECASE),
            ]
        }
        
        # Define importance levels for different memory types
        self.importance_levels = {
            "character_reference": "high",
            "personal_fact": "high", 
            "favorite": "medium",
            "relationship": "high",
            "goal_aspiration": "medium",
            "hobby_interest": "medium",
            "dislike": "low"
        }

    def extract_memories(self, message: str) -> Dict[str, Dict[str, str]]:
        """
        Analyzes a message and extracts a dictionary of memories with metadata.

        Args:
            message: The user's message.

        Returns:
            A dictionary where keys are memory identifiers and values contain:
            - 'value': the memory content
            - 'category': the type of memory
            - 'importance': importance level (high/medium/low)
            - 'timestamp': when the memory was extracted
        """
        memories = {}
        
        # Process all pattern categories
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                matches = pattern.findall(message)
                for match in matches:
                    if category == "favorite":
                        key = f"favorite_{match[0].lower().replace(' ', '_')}"
                        value = match[1].strip().rstrip('.,!?')
                    elif category == "character_reference":
                        key = "favorite_character"
                        value = match.strip().rstrip('.,!?')
                    elif category == "personal_fact":
                        if "age" in pattern.pattern.lower():
                            key = "age"
                            value = match if isinstance(match, str) else str(match)
                        else:
                            key = "occupation" if "work" in pattern.pattern or "job" in pattern.pattern or "profession" in pattern.pattern else "personal_info"
                            value = match.strip().rstrip('.,!?')
                    elif category == "hobby_interest":
                        activity_type = self._categorize_activity(match)
                        key = f"hobby_{activity_type}"
                        value = match.strip().rstrip('.,!?')
                    elif category == "relationship":
                        if len(match) == 2:  # Tuple match like (brother, John)
                            key = f"relationship_{match[0].lower().replace(' ', '_')}"
                            value = match[1].strip().rstrip('.,!?')
                        else:
                            key = "relationship_info"
                            value = match.strip().rstrip('.,!?')
                    elif category == "goal_aspiration":
                        key = "life_goal"
                        value = match.strip().rstrip('.,!?')
                    elif category == "dislike":
                        key = "dislikes"
                        value = match.strip().rstrip('.,!?')
                    else:
                        key = f"{category}_{len(memories)}"
                        value = match.strip().rstrip('.,!?') if isinstance(match, str) else str(match)
                    
                    # Store memory with metadata
                    memories[key] = {
                        'value': value,
                        'category': category,
                        'importance': self.importance_levels.get(category, "low"),
                        'timestamp': datetime.now().isoformat()
                    }

        return memories

    def _categorize_activity(self, activity: str) -> str:
        """Categorize an activity into a more specific type."""
        activity_lower = activity.lower()
        
        if any(word in activity_lower for word in ['game', 'gaming', 'play']):
            return 'gaming'
        elif any(word in activity_lower for word in ['music', 'song', 'band', 'artist']):
            return 'music'
        elif any(word in activity_lower for word in ['anime', 'movie', 'series', 'show']):
            return 'entertainment'
        elif any(word in activity_lower for word in ['book', 'read', 'novel']):
            return 'reading'
        elif any(word in activity_lower for word in ['sport', 'run', 'gym', 'exercise']):
            return 'fitness'
        else:
            return 'general'

# Example usage:
if __name__ == '__main__':
    extractor = MemoryExtractor()
    
    # Test case from the user request - anime character reference
    test_message_1 = "i like rezero anime. my favorite character is natsuki."
    extracted_memories_1 = extractor.extract_memories(test_message_1)
    print(f"Message: '{test_message_1}'")
    print(f"Extracted: {extracted_memories_1}")
    print()
    # Expected output with metadata for each memory
    
    # Test case for personal information
    test_message_2 = "I am a software engineer and my favorite food is pizza."
    extracted_memories_2 = extractor.extract_memories(test_message_2)
    print(f"Message: '{test_message_2}'")
    print(f"Extracted: {extracted_memories_2}")
    print()
    
    # Test case for anime character mentioned in previous session
    test_message_3 = "I meant the name of the Anime character I mentioned in the last session"
    extracted_memories_3 = extractor.extract_memories(test_message_3)
    print(f"Message: '{test_message_3}'")
    print(f"Extracted: {extracted_memories_3}")
    print()
    
    # Test case for various personal details
    test_message_4 = "I'm 25 years old, I work as a data scientist, and I love playing video games. My goal is to learn machine learning."
    extracted_memories_4 = extractor.extract_memories(test_message_4)
    print(f"Message: '{test_message_4}'")
    print(f"Extracted: {extracted_memories_4}")
    print()
