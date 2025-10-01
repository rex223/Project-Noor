# RL Integration with Recommendation Systems

## Overview

The RL (Reinforcement Learning) system is now fully integrated with the Spotify music and YouTube video recommendation engines. The Q-learning agent optimizes recommendation parameters in real-time based on user feedback.

## How It Works

### 1. User Requests Recommendations

When a user requests music or video recommendations:

```python
GET /api/v1/entertainment/music/recommendations/{user_id}
GET /api/v1/entertainment/video/recommendations/{user_id}
```

### 2. System Gathers Context

The system collects:
- **User's personality profile** (Big Five traits)
- **Content type** (music, video, game)
- **Current mood** (neutral, happy, sad, energetic, etc.)
- **Time of day** (morning, afternoon, evening, night)

### 3. RL Agent Selects Optimal Action

The trained Q-learning agent selects the best action (recommendation strategy) for the current state:

```python
rl_orchestrator = get_rl_orchestrator()

rl_params = rl_orchestrator.get_recommendation_params(
    user_id=user_id,
    personality_profile={
        "openness": 75,
        "conscientiousness": 60,
        "extraversion": 40,
        "agreeableness": 80,
        "neuroticism": 30
    },
    content_type="music",
    mood="relaxed",
    time_of_day="evening"
)

# Returns optimized parameters:
# {
#   "min_energy": 0.2,
#   "max_energy": 0.5,
#   "valence": 0.6,
#   "genre_count": 4,
#   "exploration_rate": 0.3,
#   "popularity_min": 10,
#   "popularity_max": 60
# }
```

### 4. Parameters Applied to APIs

#### Music Recommendations (Spotify)

```python
spotify.recommendations(
    seed_genres=genre_seeds[:5],
    limit=limit,
    min_energy=rl_params["min_energy"],      # RL-optimized
    max_energy=rl_params["max_energy"],      # RL-optimized
    target_valence=rl_params["valence"],     # RL-optimized
    target_danceability=audio_features["danceability"],  # Personality-based
    target_acousticness=audio_features["acousticness"],  # Personality-based
    target_instrumentalness=audio_features["instrumentalness"],  # Personality-based
    min_popularity=rl_params["popularity_min"],  # RL-optimized
    max_popularity=rl_params["popularity_max"]   # RL-optimized
)
```

#### Video Recommendations (YouTube)

```python
# RL adjusts search terms based on energy and valence
if energy_level > 0.7:
    search_terms.extend(["exciting", "intense", "high energy"])
elif energy_level < 0.3:
    search_terms.extend(["calm", "relaxing", "peaceful"])

if rl_params["valence"] > 0.7:
    search_terms.extend(["uplifting", "positive", "motivational"])
elif rl_params["valence"] < 0.3:
    search_terms.extend(["deep", "meaningful", "thought-provoking"])

# Exploration rate determines novelty
if rl_params["exploration_rate"] > 0.5:
    search_terms.extend(["unique", "different", "unusual", "creative"])

# Search YouTube with optimized terms
youtube.search().list(
    q=search_term,
    maxResults=limit,
    type='video',
    order='relevance'
)
```

### 5. Recommendations Returned with Metadata

Each recommendation includes:
- Content details (title, artist/channel, URL, thumbnail)
- RL parameters used (stored in metadata)
- Personality match score
- Confidence score
- Reasoning

Example:
```json
{
  "id": "track-123",
  "title": "Moonlight Sonata",
  "artist": "Beethoven",
  "genre": "classical",
  "mood": "calm",
  "energy_level": 30,
  "reasoning": "Based on your personality profile, this calm track matches your preferences for classical with 30% energy",
  "confidence": 82,
  "spotify_url": "https://open.spotify.com/track/...",
  "metadata": {
    "rl_params": {
      "min_energy": 0.2,
      "max_energy": 0.5,
      "valence": 0.6,
      "genre_count": 4,
      "exploration_rate": 0.3,
      "popularity_min": 10,
      "popularity_max": 60
    },
    "time_of_day": "evening"
  }
}
```

### 6. User Provides Feedback

User interacts with recommendations:

```python
POST /api/v1/entertainment/interactions/{user_id}
{
  "content_type": "music",
  "content_id": "track-123",
  "interaction_type": "like",  # like, dislike, skip, complete, share
  "completion_percentage": 95,
  "mood_before": "neutral",
  "mood_after": "relaxed"
}
```

### 7. Interaction Stored with Context

The system stores:
- User feedback (like/dislike/skip/complete)
- Content details
- **RL parameters that were used** (from metadata)
- Personality profile at time of recommendation
- Mood before/after
- Completion percentage

This creates a complete feedback loop: `State → Action → Reward`

### 8. Weekly Training Updates Model

Every Monday at 1 AM:

```python
# Fetch last 7 days of interactions
interactions = get_interactions(days_back=7)

# Group by user
for user_id, user_interactions in interactions.items():
    for interaction in user_interactions:
        # Reconstruct state
        state = RecommendationState(
            openness=interaction.personality["openness"],
            conscientiousness=interaction.personality["conscientiousness"],
            extraversion=interaction.personality["extraversion"],
            agreeableness=interaction.personality["agreeableness"],
            neuroticism=interaction.personality["neuroticism"],
            content_type=interaction.content_type,
            mood=interaction.mood,
            time_of_day=interaction.time_of_day
        )
        
        # Infer action from stored RL params
        action = RecommendationAction.from_params(
            interaction.metadata["rl_params"]
        )
        
        # Calculate reward
        reward = reward_function.calculate_reward(
            interaction_type=interaction.interaction_type,  # like/dislike/skip
            completion_percentage=interaction.completion_percentage,
            mood_before=interaction.mood_before,
            mood_after=interaction.mood_after
        )
        
        # Update Q-value
        agent.update(state, action, reward)

# Save updated Q-table
agent.save_model("models/q_table.json")
```

## RL Parameter Mappings

### Energy Level

Maps to Spotify's `energy` and `valence` features:

| RL Energy | Spotify min_energy | Spotify max_energy | Description |
|-----------|-------------------|-------------------|-------------|
| Low (0.0-0.33) | 0.0 | 0.4 | Calm, relaxing tracks |
| Medium (0.34-0.66) | 0.3 | 0.7 | Moderate energy |
| High (0.67-1.0) | 0.6 | 1.0 | Energetic, intense tracks |

Maps to YouTube search terms:
- **Low energy**: "calm", "relaxing", "peaceful", "ambient"
- **High energy**: "exciting", "intense", "high energy", "upbeat"

### Diversity

Controls genre/category variety:

| RL Diversity | Genre Count | Exploration Rate | Description |
|--------------|-------------|------------------|-------------|
| Focused | 2 | 0.1 | Narrow genre focus, familiar content |
| Balanced | 3-4 | 0.3-0.4 | Mix of known and new |
| Diverse | 5+ | 0.5+ | Wide variety, experimental |

### Novelty

Controls content popularity and familiarity:

| RL Novelty | Spotify Popularity | YouTube Terms | Description |
|------------|-------------------|---------------|-------------|
| Familiar | 60-100 | "popular", "trending" | Well-known, mainstream |
| Mixed | 30-70 | "recommended", "featured" | Mix of popular and obscure |
| Exploratory | 0-40 | "unique", "hidden gem", "undiscovered" | Niche, underground |

## Example: Complete Flow

### Initial State

```python
User: introverted (extraversion=35), emotionally stable (neuroticism=25), 
      high openness (85), evening, relaxed mood
```

### RL Action Selection

```python
State = (openness=high, extraversion=low, neuroticism=low, 
         content_type=music, mood=relaxed, time=evening)

Q-table lookup:
  Q(state, low_diverse_exploratory) = 0.82  ← Highest Q-value
  Q(state, low_focused_familiar) = 0.65
  Q(state, medium_balanced_mixed) = 0.71

Selected Action: energy=low, diversity=diverse, novelty=exploratory
```

### API Parameters

```python
Spotify Parameters:
  min_energy=0.1, max_energy=0.4  (low energy)
  valence=0.6  (positive but calm)
  genre_count=5  (diverse)
  popularity_min=0, popularity_max=40  (exploratory)
  
Genres: ["classical", "ambient", "jazz", "world", "experimental"]
```

### User Feedback

```python
User likes track, completes 100%, mood improves to "peaceful"

Reward = like(+1.0) + complete(+0.5) + completion(+0.5) + mood_improve(+0.3)
       = +2.3
```

### Q-Value Update

```python
Q(state, action) = 0.82 + 0.1 * [2.3 + 0.95 * 0 - 0.82]
                 = 0.82 + 0.1 * 1.48
                 = 0.968

New Q-value stored for future recommendations
```

### Next Time

When user requests recommendations in similar context (evening, relaxed, music):
- System will favor `low_diverse_exploratory` action (Q=0.968)
- User gets similar style recommendations
- Continuous improvement through feedback loop

## Fallback Behavior

If RL agent fails or model not trained:

```python
try:
    rl_params = rl_orchestrator.get_recommendation_params(...)
except Exception as e:
    logger.warning(f"RL failed, using defaults: {e}")
    # Fallback to personality-based defaults
    rl_params = {
        "min_energy": 0.3,
        "max_energy": 0.7,
        "valence": 0.5,
        "genre_count": 3,
        "exploration_rate": 0.3,
        "popularity_min": 20,
        "popularity_max": 80
    }
```

System gracefully degrades to personality-only recommendations.

## Monitoring RL Performance

### Check Last Training Run

```bash
curl -X GET http://localhost:8000/api/v1/admin/tasks/history \
  -H "X-Admin-Key: admin-dev-key-change-in-production"
```

Look for `rl_training` tasks:
```json
{
  "task_name": "rl_training",
  "status": "completed",
  "executed_at": "2025-10-06T01:00:00",
  "users_processed": 45,
  "records_processed": 523,
  "metadata": {
    "training": {
      "average_reward": 0.67,
      "users_trained": 45,
      "total_interactions": 523,
      "agent_stats": {
        "total_states": 186,
        "total_state_actions": 892,
        "avg_q_value": 0.45,
        "max_q_value": 0.97
      }
    }
  }
}
```

### Track Engagement Improvements

Compare metrics before/after RL deployment:

```sql
-- Before RL (using personality-only)
SELECT 
  AVG(CASE WHEN interaction_type = 'like' THEN 1 ELSE 0 END) as like_rate,
  AVG(completion_percentage) as avg_completion,
  COUNT(*) as total_interactions
FROM entertainment_interactions
WHERE created_at < '2025-10-01';  -- Before RL deployment

-- After RL
SELECT 
  AVG(CASE WHEN interaction_type = 'like' THEN 1 ELSE 0 END) as like_rate,
  AVG(completion_percentage) as avg_completion,
  COUNT(*) as total_interactions
FROM entertainment_interactions
WHERE created_at >= '2025-10-01';  -- After RL deployment
```

Expected improvements:
- **Like rate**: +15-25% increase
- **Completion rate**: +10-20% increase
- **Skip rate**: -20-30% decrease

## Debugging RL Integration

### Check RL Logs

```bash
# Backend logs show RL parameter usage
grep "Using RL params" bondhu-ai/logs/app.log

# Output:
# 2025-10-01 14:23:15 INFO: Using RL params for user user-123: {'min_energy': 0.2, 'max_energy': 0.5, ...}
```

### Verify Parameters in Database

```sql
SELECT 
  content_id,
  title,
  metadata->'rl_params' as rl_params,
  metadata->'time_of_day' as time_context
FROM entertainment_recommendations
WHERE user_id = 'user-123'
ORDER BY created_at DESC
LIMIT 5;
```

### Test RL Directly

```python
from core.rl_orchestrator import get_rl_orchestrator

orchestrator = get_rl_orchestrator()

# Test parameter generation
params = orchestrator.get_recommendation_params(
    user_id="test-user",
    personality_profile={
        "openness": 80,
        "conscientiousness": 60,
        "extraversion": 40,
        "agreeableness": 75,
        "neuroticism": 30
    },
    content_type="music",
    mood="relaxed",
    time_of_day="evening"
)

print(f"RL Parameters: {params}")

# Check agent stats
stats = orchestrator.agent.get_stats()
print(f"Agent explored {stats['total_states']} states")
print(f"Average Q-value: {stats['avg_q_value']:.3f}")
```

## Next Steps

1. **Monitor initial RL performance** - Track engagement metrics for first month
2. **Tune hyperparameters** - Adjust learning rate, exploration rate based on results
3. **Add more actions** - Expand action space (e.g., add "tempo" dimension)
4. **Implement A/B testing** - Compare RL vs baseline recommendations
5. **Add contextual features** - Consider day of week, weather, user activity
6. **Scale to more content types** - Apply to gaming, podcasts, articles

## Conclusion

The RL system creates a continuous improvement loop:

1. **Personality** provides baseline preferences
2. **RL** optimizes specific recommendation parameters
3. **User feedback** trains the model
4. **Better recommendations** emerge over time

This hybrid approach combines the interpretability of personality-based recommendations with the adaptability of reinforcement learning.
