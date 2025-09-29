# Bondhu AI Personality Integration Guide

## Overview

This guide demonstrates how to integrate the existing Supabase personality assessment data with the Bondhu AI multi-agent system. The system now fetches personality data and LLM context directly from your database.

## Database Integration

### Current Database Schema
Your Supabase database contains:
- `profiles` table with personality scores (0-100 for each Big Five trait)
- `personality_llm_context` JSONB field with generated conversation guidelines
- Onboarding status tracking

### New Components Added

1. **Database Client** (`core/database/supabase_client.py`)
   - Direct connection to your Supabase database
   - Async methods for fetching personality data
   - Connection pooling for performance

2. **Data Models** (`core/database/models.py`)
   - Pydantic models matching your database schema
   - Type-safe personality profile handling
   - LLM context parsing

3. **Personality Service** (`core/database/personality_service.py`)
   - High-level service for personality operations
   - Context fetching and caching
   - Agent guidelines generation

## Usage Examples

### 1. Basic Personality Context Fetching

```python
from core.database.personality_service import get_personality_service

# Initialize service
personality_service = get_personality_service()

# Get comprehensive personality context
user_id = "d98ffb65-4d8c-9f62-a4f8-2bf47e6b8927"
context = await personality_service.get_user_personality_context(user_id)

if context.has_assessment:
    print(f"Openness: {context.personality_profile.openness}/100")
    print(f"System Prompt: {context.get_system_prompt()}")
    print(f"Conversation Style: {context.llm_context.conversation_style}")
```

### 2. Agent Integration Example

```python
from agents.music.music_agent import MusicIntelligenceAgent
from core.database.personality_service import get_personality_service

# Create agent with personality awareness
music_agent = MusicIntelligenceAgent(user_id="user123")

# Get personality guidelines
guidelines = await music_agent.get_personality_guidelines()
music_prefs = guidelines["music_preferences"]

# Use guidelines in analysis
if music_prefs["discovery"] == "Explore diverse, experimental genres":
    # Recommend experimental music for high openness users
    pass
```

### 3. LLM Context Integration

```python
# Get system prompt for LLM interactions
system_prompt = await personality_service.get_llm_system_prompt(user_id)

# Example system prompt format (from your existing data):
"""
You are Bondhu, an empathetic AI mental health companion. Adapt your conversation style based on this user's personality assessment:

PERSONALITY PROFILE:
- Openness: 83/100 (High)
- Conscientiousness: 67/100 (Moderate)
- Extraversion: 58/100 (Moderate)
- Agreeableness: 67/100 (Moderate)
- Emotional Sensitivity: 58/100 (Moderate)

CONVERSATION GUIDELINES:
Adapt conversation style based on: Balanced energy, adapt to user's current social mood. Explore abstract concepts, encourage creativity, discuss possibilities.
...
"""
```

## API Endpoints

### New Personality Context Endpoints

1. **Get User Context**
   ```http
   GET /personality-context/user-context/{user_id}
   ```
   Returns complete personality profile, LLM context, and onboarding status.

2. **Get LLM System Prompt**
   ```http
   GET /personality-context/llm-context/{user_id}
   ```
   Returns just the system prompt for quick LLM setup.

3. **Check Onboarding Status**
   ```http
   GET /personality-context/onboarding-status/{user_id}
   ```
   Verifies if user has completed personality assessment.

4. **Get Personality Guidelines**
   ```http
   GET /personality-context/guidelines/{user_id}
   ```
   Returns agent-specific guidelines based on personality.

### Example API Responses

#### User Context Response
```json
{
  "success": true,
  "data": {
    "user_id": "d98ffb65-4d8c-9f62-a4f8-2bf47e6b8927",
    "has_assessment": true,
    "personality_profile": {
      "scores": {
        "openness": 83,
        "conscientiousness": 67,
        "extraversion": 58,
        "agreeableness": 67,
        "neuroticism": 58
      },
      "completed_at": "2025-09-23T21:48:04+00:00"
    },
    "llm_context": {
      "system_prompt": "You are Bondhu, an empathetic AI...",
      "conversation_style": "Balanced energy, adapt to user's current social mood...",
      "topic_preferences": ["Creative projects", "Philosophy", "Future possibilities"]
    },
    "onboarding_status": {
      "onboarding_completed": true,
      "has_personality_assessment": true
    }
  }
}
```

## Integration with Existing System

### 1. Frontend Integration
Your Next.js frontend can now:
- Check onboarding status before showing personality-dependent features
- Fetch LLM context for chat interactions
- Get personality guidelines for UI personalization

```typescript
// Check if user needs personality assessment
const response = await fetch(`/api/personality-context/onboarding-status/${userId}`);
const { data } = await response.json();

if (!data.has_personality_assessment) {
  // Redirect to personality assessment
  router.push('/onboarding/personality');
}
```

### 2. Agent Workflow Integration
Agents automatically fetch personality context:

```python
# In any agent's analyze method
async def analyze(self, user_data: Dict[str, Any]) -> AgentResult:
    # Get personality context automatically
    context = await self.get_personality_context()
    
    if context and context.has_assessment:
        # Use personality-aware analysis
        guidelines = await self.get_personality_guidelines()
        # Apply guidelines to analysis logic
    else:
        # Use default analysis for users without assessment
        guidelines = self._get_default_guidelines()
    
    # Continue with analysis...
```

### 3. LLM Chat Integration
Use the generated system prompts in your chat interface:

```python
from openai import AsyncOpenAI

# Get personalized system prompt
system_prompt = await personality_service.get_llm_system_prompt(user_id)

# Use in OpenAI chat
client = AsyncOpenAI()
response = await client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
)
```

## Testing the Integration

### 1. Quick Test Script
```bash
# Run the comprehensive integration test
python test_personality_integration.py
```

This script will:
- ✅ Test database connection to Supabase
- ✅ Verify personality_profiles view access  
- ✅ Fetch real user personality data
- ✅ Test LLM context retrieval
- ✅ Validate onboarding status checking
- ✅ Test agent analysis storage

### 2. Test with Your Existing Data
Using the user IDs from your screenshot:
```python
# Test with actual user from your database
user_ids = [
    "d98ffb65-4d8c-9f62-a4f8-2bf47e6b8927",  # User with complete assessment
    # Add other user IDs from your table
]

for user_id in user_ids:
    context = await personality_service.get_user_personality_context(user_id)
    print(f"User: {context.personality_profile.full_name}")
    print(f"Completion: {context.onboarding_status.profile_completion_percentage}%")
```

### 2. Test API Endpoints
```bash
# Start the server
python main.py

# Test personality context endpoint
curl http://localhost:8000/personality-context/user-context/d98ffb65-4d8c-9f62-a4f8-2bf47e6b8927

# Test LLM context endpoint
curl http://localhost:8000/personality-context/llm-context/d98ffb65-4d8c-9f62-a4f8-2bf47e6b8927
```

## Environment Configuration

Update your `.env` file:
```env
# Database (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# AI Models
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional external APIs
SPOTIFY_CLIENT_ID=your-spotify-id
SPOTIFY_CLIENT_SECRET=your-spotify-secret
YOUTUBE_API_KEY=your-youtube-key
STEAM_API_KEY=your-steam-key
```

## Key Benefits

1. **Seamless Integration**: Uses your existing personality assessment data
2. **Personalized Responses**: LLM conversations adapt to user personality
3. **Agent Intelligence**: Multi-agent analysis considers personality traits
4. **Performance**: Cached personality context for efficient access
5. **Scalability**: Async database operations for high concurrency
6. **Type Safety**: Pydantic models ensure data consistency

## Next Steps

1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Configure Environment**: Set up Supabase credentials in `.env`
3. **Test Integration**: Use existing user data to verify functionality
4. **Frontend Updates**: Integrate personality context API calls
5. **Agent Customization**: Enhance agents with personality-specific logic

The system is now ready to provide personality-aware AI interactions using your existing assessment data!