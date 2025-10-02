import logging
from typing import List, Dict, Any, Optional
from core.database.supabase_client import SupabaseClient

class MemoryService:
    """
    Service for managing user memories in the database.
    """

    def __init__(self, supabase_client: SupabaseClient):
        self._client = supabase_client
        self.logger = logging.getLogger("bondhu.memory_service")

    def add_memory(self, user_id: str, key: str, value: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Adds or updates a memory for a user with optional metadata.

        Args:
            user_id: The user's ID.
            key: The memory's key (e.g., 'favorite_anime').
            value: The memory's value (e.g., 'Re:Zero').
            metadata: Optional metadata about the memory (importance, category, etc.)

        Returns:
            True if the memory was added/updated successfully, False otherwise.
        """
        try:
            memory_data = {
                "user_id": user_id,
                "key": key,
                "value": value
            }
            
            # Add metadata if provided
            if metadata:
                # Store metadata in a JSON column if available, or append to value
                if 'importance' in metadata:
                    memory_data['importance'] = metadata['importance']
                if 'category' in metadata:
                    memory_data['category'] = metadata['category']
            
            # Upsert the memory
            self._client.supabase.table("user_memories").upsert(
                memory_data, 
                on_conflict="user_id, key"
            ).execute()
            self.logger.info(f"Successfully saved memory '{key}' for user {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving memory for user {user_id}: {e}")
            return False

    def add_memories_batch(self, user_id: str, memories: Dict[str, Dict[str, str]]) -> bool:
        """
        Add multiple memories at once with their metadata.
        
        Args:
            user_id: The user's ID
            memories: Dictionary of memories with metadata from MemoryExtractor
            
        Returns:
            True if all memories were saved successfully
        """
        try:
            success_count = 0
            for key, memory_data in memories.items():
                success = self.add_memory(
                    user_id=user_id,
                    key=key,
                    value=memory_data['value'],
                    metadata={
                        'importance': memory_data.get('importance', 'low'),
                        'category': memory_data.get('category', 'general'),
                        'timestamp': memory_data.get('timestamp')
                    }
                )
                if success:
                    success_count += 1
            
            self.logger.info(f"Successfully saved {success_count}/{len(memories)} memories for user {user_id}")
            return success_count == len(memories)
        except Exception as e:
            self.logger.error(f"Error saving batch memories for user {user_id}: {e}")
            return False

    def get_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all memories for a user.

        Args:
            user_id: The user's ID.

        Returns:
            A list of memory dictionaries.
        """
        try:
            response = self._client.supabase.table("user_memories").select("*").eq("user_id", user_id).execute()
            return response.data
        except Exception as e:
            self.logger.error(f"Error retrieving memories for user {user_id}: {e}")
            return []

    def search_memories(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """
        Searches for memories for a user based on a query.
        This is a simple search for now, matching keys.

        Args:
            user_id: The user's ID.
            query: The search query.

        Returns:
            A list of matching memory dictionaries.
        """
        try:
            # This is a very basic search. A more advanced implementation could use full-text search or embeddings.
            response = self._client.supabase.table("user_memories").select("*").eq("user_id", user_id).ilike("key", f"%{query}%").execute()
            return response.data
        except Exception as e:
            self.logger.error(f"Error searching memories for user {user_id}: {e}")
            return []

    def get_important_memories(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get the most important memories for session initialization.
        Prioritizes high-importance memories and recent entries.

        Args:
            user_id: The user's ID.
            limit: Maximum number of memories to return.

        Returns:
            A list of important memory dictionaries sorted by importance.
        """
        try:
            # Get all memories for the user, ordered by importance and recency
            response = self._client.supabase.table("user_memories").select("*").eq("user_id", user_id).order("updated_at", desc=True).limit(limit * 2).execute()
            
            memories = response.data
            if not memories:
                return []
            
            # Categorize memories by importance (if we have importance metadata)
            high_importance = []
            medium_importance = []
            low_importance = []
            
            # Define high-importance keywords for prioritization
            high_importance_keys = [
                'favorite_character', 'occupation', 'age', 'personal_info', 
                'relationship_', 'life_goal', 'favorite_anime', 'favorite_game',
                'favorite_music', 'hobby_'
            ]
            
            for memory in memories:
                key = memory.get('key', '')
                is_high_importance = any(hi_key in key for hi_key in high_importance_keys)
                
                if is_high_importance or memory.get('importance') == 'high':
                    high_importance.append(memory)
                elif memory.get('importance') == 'medium':
                    medium_importance.append(memory)
                else:
                    low_importance.append(memory)
            
            # Return prioritized memories up to the limit
            important_memories = high_importance + medium_importance + low_importance
            return important_memories[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting important memories for user {user_id}: {e}")
            return []

    def generate_session_context(self, user_id: str) -> str:
        """
        Generate a comprehensive context string for session initialization.
        This includes the most important user information for the AI to remember.

        Args:
            user_id: The user's ID.

        Returns:
            A formatted string with important user context.
        """
        try:
            important_memories = self.get_important_memories(user_id, limit=15)
            
            if not important_memories:
                return ""
            
            context_parts = []
            context_parts.append("Important things to remember about this user:")
            
            # Group memories by category for better organization
            personal_info = []
            favorites = []
            relationships = []
            hobbies = []
            other = []
            
            for memory in important_memories:
                key = memory.get('key', '')
                value = memory.get('value', '')
                
                if any(term in key for term in ['occupation', 'age', 'personal_info']):
                    personal_info.append(f"- {key.replace('_', ' ').title()}: {value}")
                elif 'favorite' in key:
                    favorites.append(f"- {key.replace('_', ' ').title()}: {value}")
                elif 'relationship' in key:
                    relationships.append(f"- {key.replace('_', ' ').title()}: {value}")
                elif 'hobby' in key:
                    hobbies.append(f"- {key.replace('_', ' ').title()}: {value}")
                else:
                    other.append(f"- {key.replace('_', ' ').title()}: {value}")
            
            # Add sections that have content
            if personal_info:
                context_parts.append("\nPersonal Information:")
                context_parts.extend(personal_info)
            
            if favorites:
                context_parts.append("\nFavorites & Preferences:")
                context_parts.extend(favorites)
                
            if relationships:
                context_parts.append("\nRelationships:")
                context_parts.extend(relationships)
                
            if hobbies:
                context_parts.append("\nHobbies & Interests:")
                context_parts.extend(hobbies)
                
            if other:
                context_parts.append("\nOther Details:")
                context_parts.extend(other)
            
            return "\n".join(context_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating session context for user {user_id}: {e}")
            return ""

# Global instance
_memory_service_instance: Optional[MemoryService] = None

def get_memory_service() -> MemoryService:
    """
    Returns a singleton instance of the MemoryService.
    """
    global _memory_service_instance
    if _memory_service_instance is None:
        # This assumes the Supabase client is initialized elsewhere and available
        # This is a simplified approach for dependency injection
        from core.database.supabase_client import get_supabase_client
        supabase_client = get_supabase_client()
        _memory_service_instance = MemoryService(supabase_client)
    return _memory_service_instance
