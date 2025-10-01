"""
Supabase database connection and client setup for Bondhu AI.
"""

from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from datetime import datetime
import json
import logging

from ..config.settings import get_config

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Supabase client for database operations using REST API."""
    
    def __init__(self):
        config = get_config()
        self.supabase: Client = create_client(
            config.database.url,
            config.database.key
        )
    
    async def close(self):
        """Close database connections (no-op for REST API)."""
        pass
    
    async def get_user_personality(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch user's personality assessment data from the personality_profiles view.
        
        Args:
            user_id: User's UUID
            
        Returns:
            Dictionary containing personality scores and LLM context, or None if not found
        """
        try:
            # Use Supabase REST API instead of direct PostgreSQL connection
            response = self.supabase.table('personality_profiles').select(
                'id, full_name, avatar_url, personality_openness, personality_conscientiousness, '
                'personality_extraversion, personality_agreeableness, personality_neuroticism, '
                'personality_llm_context, personality_completed_at, onboarding_completed, '
                'has_completed_personality_assessment, profile_completion_percentage, '
                'created_at, updated_at'
            ).eq('id', user_id).eq('has_completed_personality_assessment', True).execute()
            
            if response.data and len(response.data) > 0:
                row = response.data[0]
                return {
                    'user_id': str(row['id']),
                    'full_name': row.get('full_name'),
                    'avatar_url': row.get('avatar_url'),
                    'scores': {
                        'openness': row.get('personality_openness'),
                        'conscientiousness': row.get('personality_conscientiousness'),
                        'extraversion': row.get('personality_extraversion'),
                        'agreeableness': row.get('personality_agreeableness'),
                        'neuroticism': row.get('personality_neuroticism')
                    },
                    'llm_context': row.get('personality_llm_context'),
                    'completed_at': row.get('personality_completed_at'),
                    'onboarding_completed': row.get('onboarding_completed'),
                    'has_assessment': row.get('has_completed_personality_assessment'),
                    'profile_completion_percentage': row.get('profile_completion_percentage'),
                    'created_at': row.get('created_at'),
                    'updated_at': row.get('updated_at')
                }
                
            return None
                
        except Exception as e:
            logger.error(f"Error fetching personality data for user {user_id}: {e}")
            return None
    
    async def get_personality_llm_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the LLM context specifically for a user from personality_profiles view.
        
        Args:
            user_id: User's UUID
            
        Returns:
            LLM context dictionary or None
        """
        try:
            response = self.supabase.table('personality_profiles').select(
                'personality_llm_context'
            ).eq('id', user_id).eq('has_completed_personality_assessment', True).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0].get('personality_llm_context')
                
            return None
                
        except Exception as e:
            logger.error(f"Error fetching LLM context for user {user_id}: {e}")
            return None
    
    async def check_user_onboarding_status(self, user_id: str) -> Dict[str, Any]:
        """
        Check if user has completed onboarding and personality assessment using personality_profiles view.
        
        Args:
            user_id: User's UUID
            
        Returns:
            Dictionary with onboarding status information
        """
        try:
            response = self.supabase.table('personality_profiles').select(
                'id, full_name, avatar_url, onboarding_completed, personality_completed_at, '
                'has_completed_personality_assessment, profile_completion_percentage, '
                'created_at, updated_at'
            ).eq('id', user_id).execute()
            
            if response.data and len(response.data) > 0:
                row = response.data[0]
                return {
                    'user_id': str(row['id']),
                    'full_name': row.get('full_name'),
                    'avatar_url': row.get('avatar_url'),
                    'onboarding_completed': row.get('onboarding_completed', False),
                    'has_personality_assessment': row.get('has_completed_personality_assessment', False),
                    'personality_completed_at': row.get('personality_completed_at'),
                    'profile_completion_percentage': row.get('profile_completion_percentage', 0),
                    'user_exists': True,
                    'created_at': row.get('created_at'),
                    'updated_at': row.get('updated_at')
                }
            
            return {
                'user_id': user_id,
                'user_exists': False,
                'onboarding_completed': False,
                'has_personality_assessment': False
            }
                
        except Exception as e:
            logger.error(f"Error checking onboarding status for user {user_id}: {e}")
            return {
                'user_id': user_id,
                'user_exists': False,
                'onboarding_completed': False,
                'has_personality_assessment': False,
                'error': str(e)
            }
    
    async def store_agent_analysis(
        self, 
        user_id: str, 
        agent_type: str, 
        analysis_data: Dict[str, Any]
    ) -> bool:
        """
        Store agent analysis results for future reference.
        
        Args:
            user_id: User's UUID
            agent_type: Type of agent (music, video, gaming, personality)
            analysis_data: Analysis results
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use Supabase client for this operation
            result = self.supabase.table('agent_analyses').upsert({
                'user_id': user_id,
                'agent_type': agent_type,
                'analysis_data': analysis_data,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error storing agent analysis for user {user_id}, agent {agent_type}: {e}")
            return False
    
    async def get_agent_analysis_history(
        self, 
        user_id: str, 
        agent_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical agent analysis data for a user.
        
        Args:
            user_id: User's UUID
            agent_type: Optional specific agent type to filter by
            
        Returns:
            List of analysis records
        """
        try:
            query = self.supabase.table('agent_analyses').select('*').eq('user_id', user_id)
            
            if agent_type:
                query = query.eq('agent_type', agent_type)
            
            result = query.order('created_at', desc=True).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error fetching agent analysis history for user {user_id}: {e}")
            return []


# Global client instance
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """Get the global Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client


async def cleanup_database():
    """Cleanup database connections."""
    global _supabase_client
    if _supabase_client:
        await _supabase_client.close()
        _supabase_client = None