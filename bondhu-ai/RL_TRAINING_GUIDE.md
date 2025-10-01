# Reinforcement Learning Training System

## Overview

The RL training system uses Q-learning to optimize entertainment recommendation parameters based on user feedback and personality traits. It learns which recommendation strategies (energy level, diversity, novelty) work best for different personality profiles and contexts.

## Architecture

### Components

1. **State Space** (`RecommendationState`)
   - Personality traits (Big Five, discretized into 5 bins each)
   - Content type (music, video, game)
   - User mood (neutral, happy, sad, anxious, etc.)
   - Time of day (morning, afternoon, evening, night)

2. **Action Space** (`RecommendationAction`)
   - Energy level: low, medium, high
   - Diversity: focused, balanced, diverse
   - Novelty: familiar, mixed, exploratory
   - Total: 27 possible actions (3×3×3)

3. **Reward Function** (`RewardFunction`)
   - Like: +1.0
   - Dislike: -1.0
   - Complete: +0.5
   - Skip: -0.3
   - Share: +0.8
   - Completion rate: 0 to +0.5
   - Mood improvement: -0.5 to +0.5

4. **Q-Learning Agent** (`QLearningAgent`)
   - Learning rate: 0.1
   - Discount factor: 0.95
   - Exploration rate: 0.3 → 0.05 (with decay)
   - Q-table: {state: {action: Q-value}}

5. **Training Orchestrator** (`RLTrainingOrchestrator`)
   - Coordinates training loop
   - Manages model persistence
   - Provides optimized recommendations

## How It Works

### Training Process

**Automated Weekly Training** (Monday 1 AM):
```
1. Fetch interactions from last 7 days
2. Group by user (minimum 5 interactions)
3. For each user:
   a. Get personality profile
   b. For each interaction:
      - Construct state (personality + context)
      - Infer action (recommendation params)
      - Calculate reward (feedback score)
      - Update Q-value: Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') - Q(s,a)]
4. Save updated Q-table to models/q_table.json
5. Log training statistics
```

### Q-Learning Update Rule

```
Q(s,a) = Q(s,a) + α[r + γ·max_a' Q(s',a') - Q(s,a)]

Where:
- Q(s,a) = Quality of taking action a in state s
- α = Learning rate (0.1) - how much to update
- r = Reward received
- γ = Discount factor (0.95) - value of future rewards
- max_a' Q(s',a') = Best expected future value
```

### Action Selection

**During Training (Exploration)**:
- 30% probability: Random action (explore)
- 70% probability: Best Q-value action (exploit)
- Exploration rate decays to 5% minimum

**In Production (Exploitation)**:
- Always select action with highest Q-value
- No exploration (use learned policy)

### Recommendation Generation

```python
# User requests music recommendations
user_personality = {
    "openness": 75,        # High
    "conscientiousness": 60,
    "extraversion": 40,    # Low (introvert)
    "agreeableness": 80,
    "neuroticism": 30      # Low (emotionally stable)
}

# RL agent selects optimal action
state = RecommendationState(
    **user_personality,
    content_type="music",
    mood="calm",
    time_of_day="evening"
)

action = agent.get_action(state, explore=False)
# Result: RecommendationAction(energy="low", diversity="diverse", novelty="exploratory")

# Convert to API parameters
params = action.to_recommendation_params()
# Result: {
#   "min_energy": 0.0, "max_energy": 0.4,
#   "valence": 0.3,
#   "genre_count": 5,
#   "exploration_rate": 0.5,
#   "popularity_min": 0, "popularity_max": 50
# }

# Use params with Spotify/YouTube APIs
recommendations = get_spotify_recommendations(user_id, **params)
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd bondhu-ai
pip install -r requirements.txt
```

New dependencies:
- `numpy==1.26.4` - For Q-value calculations

### 2. Create Models Directory

```bash
mkdir -p bondhu-ai/models
```

The Q-table will be saved to `models/q_table.json`.

### 3. Initial Training

Trigger first training manually:

```bash
curl -X POST http://localhost:8000/api/v1/admin/tasks/rl-training/trigger \
  -H "X-Admin-Key: admin-dev-key-change-in-production"
```

### 4. Verify Scheduler

Check that RL training is scheduled:

```bash
curl http://localhost:8000/api/v1/admin/system/health \
  -H "X-Admin-Key: admin-dev-key-change-in-production"
```

Should show:
```json
{
  "scheduled_jobs": [
    {
      "id": "rl_training",
      "name": "Train RL recommendation model",
      "next_run_time": "2025-10-06T01:00:00",
      "trigger": "cron[day_of_week='mon', hour='1']"
    }
  ]
}
```

## Usage

### Automatic Training

The scheduler trains the model weekly (Monday 1 AM):
- Uses last 7 days of interaction data
- Requires minimum 5 interactions per user
- Updates Q-table incrementally (doesn't reset)
- Logs results to `system_tasks` table

### Manual Training

```bash
curl -X POST http://localhost:8000/api/v1/admin/tasks/rl-training/trigger \
  -H "X-Admin-Key: admin-dev-key-change-in-production"
```

### Get Optimized Recommendations

The RL agent is used automatically when generating recommendations:

```python
from core.rl_orchestrator import get_rl_orchestrator

orchestrator = get_rl_orchestrator()

# Get optimal parameters for user
params = orchestrator.get_recommendation_params(
    user_id="user-123",
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

# Use params with recommendation APIs
spotify_results = get_spotify_tracks(**params)
```

### Model Evaluation

```python
orchestrator = get_rl_orchestrator()

# Evaluate on last 3 days
evaluation = await orchestrator.evaluate_model(test_days=3)

print(f"Average reward: {evaluation['average_reward']}")
print(f"Like rate: {evaluation['like_rate']}")
```

## Monitoring

### Training Statistics

Check recent training runs:

```sql
SELECT 
  executed_at,
  users_processed,
  records_processed,
  metadata->'training'->>'average_reward' as avg_reward,
  metadata->'training'->>'agent_stats' as agent_stats
FROM system_tasks
WHERE task_name = 'rl_training'
ORDER BY executed_at DESC
LIMIT 5;
```

### Q-Table Growth

Monitor state-action coverage:

```python
agent_stats = orchestrator.agent.get_stats()

print(f"States explored: {agent_stats['total_states']}")
print(f"State-actions: {agent_stats['total_state_actions']}")
print(f"Avg Q-value: {agent_stats['avg_q_value']:.3f}")
print(f"Max Q-value: {agent_stats['max_q_value']:.3f}")
```

### Training Progress

Track average reward over time:

```sql
SELECT 
  DATE(executed_at) as training_date,
  AVG((metadata->'training'->>'average_reward')::float) as avg_reward,
  SUM((metadata->'training'->>'users_trained')::int) as total_users
FROM system_tasks
WHERE task_name = 'rl_training'
  AND status = 'completed'
GROUP BY DATE(executed_at)
ORDER BY training_date DESC;
```

## Performance Tuning

### Hyperparameters

Adjust in `core/rl_orchestrator.py`:

```python
agent = QLearningAgent(
    learning_rate=0.1,        # ↑ = faster learning, ↓ = more stable
    discount_factor=0.95,     # ↑ = value future rewards more
    exploration_rate=0.3,     # ↑ = more exploration
    exploration_decay=0.995,  # ↓ = slower decay
    min_exploration_rate=0.05 # Floor for exploration
)
```

### State Space Discretization

Reduce state space size by adjusting bins:

```python
@staticmethod
def _discretize(value: float, bins: int = 5) -> int:
    # bins=5: 0-20, 20-40, 40-60, 60-80, 80-100
    # bins=3: 0-33, 33-67, 67-100 (fewer states, less data needed)
    return min(int(value / (100.0 / bins)), bins - 1)
```

### Training Frequency

For faster learning (testing):

```python
# In start_scheduler()
scheduler.add_job(
    train_rl_model,
    trigger=IntervalTrigger(hours=6),  # Train every 6 hours
    id="rl_training_frequent"
)
```

### Reward Shaping

Adjust reward weights in `RewardFunction.calculate_reward()`:

```python
if interaction_type == "like":
    reward += 2.0  # Increase like importance
elif interaction_type == "dislike":
    reward -= 0.5  # Decrease dislike penalty
```

## Advanced Features

### Multi-Armed Bandit Alternative

For faster convergence, consider Upper Confidence Bound (UCB):

```python
def ucb_action_selection(state, exploration_param=2.0):
    state_tuple = state.to_tuple()
    total_visits = sum(visit_counts[state_tuple].values())
    
    ucb_values = {}
    for action in actions:
        action_tuple = action.to_tuple()
        q_value = q_table[state_tuple][action_tuple]
        visits = visit_counts[state_tuple][action_tuple]
        
        if visits == 0:
            return action  # Try unvisited actions first
        
        # UCB = Q(s,a) + c·√(ln(N)/n)
        ucb = q_value + exploration_param * np.sqrt(np.log(total_visits) / visits)
        ucb_values[action_tuple] = ucb
    
    best_action_tuple = max(ucb_values.items(), key=lambda x: x[1])[0]
    return RecommendationAction(*best_action_tuple)
```

### Deep Q-Network (DQN)

For larger state spaces, use neural network instead of Q-table:

```python
import torch
import torch.nn as nn

class QNetwork(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )
    
    def forward(self, state):
        return self.network(state)

# Use continuous personality values instead of discretization
# Train with experience replay and target networks
```

### Policy Gradient Methods

For direct policy optimization:

```python
# Actor-Critic architecture
# Actor: π(a|s) - probability of actions given state
# Critic: V(s) - value of state
# Update: ∇θ log π(a|s) · [r + γV(s') - V(s)]
```

## Troubleshooting

### No Training Improvement

**Symptoms**: Average reward stays flat or decreases

**Solutions**:
1. Check reward function - are rewards too sparse?
2. Increase learning rate: `learning_rate=0.2`
3. Reduce exploration decay: `exploration_decay=0.99`
4. Verify data quality - enough positive interactions?

### Q-Values Diverging

**Symptoms**: Max Q-value grows unbounded

**Solutions**:
1. Reduce learning rate: `learning_rate=0.05`
2. Lower discount factor: `discount_factor=0.9`
3. Add gradient clipping
4. Normalize rewards

### Insufficient Data

**Symptoms**: Few state-action pairs explored

**Solutions**:
1. Lower `min_interactions_per_user` threshold
2. Train on more days: `days_back=14`
3. Reduce state space bins: `bins=3`
4. Add simulated data for cold start

### Model Not Loading

**Symptoms**: `models/q_table.json` not found or corrupted

**Solutions**:
```bash
# Reset and retrain
rm models/q_table.json

curl -X POST http://localhost:8000/api/v1/admin/tasks/rl-training/trigger \
  -H "X-Admin-Key: your-key"
```

## Example Training Session

```python
# Simulate a training episode

# User: High openness (adventurous), Low neuroticism (stable)
personality = {
    "openness": 85,
    "conscientiousness": 50,
    "extraversion": 60,
    "agreeableness": 70,
    "neuroticism": 20
}

# Session 1: Evening, relaxed mood
state1 = RecommendationState(
    **personality,
    content_type="music",
    mood="relaxed",
    time_of_day="evening"
)

# RL suggests: energy=low, diversity=diverse, novelty=exploratory
# (Adventurous user + relaxed mood = diverse low-energy exploration)
action1 = agent.get_action(state1)

# User likes the recommendation
reward1 = 1.0
agent.update(state1, action1, reward1)

# Session 2: Morning, energetic mood
state2 = RecommendationState(
    **personality,
    content_type="music",
    mood="energetic",
    time_of_day="morning"
)

# RL suggests: energy=high, diversity=diverse, novelty=exploratory
action2 = agent.get_action(state2)

# User completes full listen + shares
reward2 = 1.3  # 0.5 (complete) + 0.8 (share)
agent.update(state2, action2, reward2, next_state=None)

# Over time, Q-values learn:
# Q(relaxed + evening + high_openness, low_diverse_exploratory) → high
# Q(energetic + morning + high_openness, high_diverse_exploratory) → high
```

## Production Checklist

- [ ] Train on at least 1000 interactions before deployment
- [ ] Monitor average reward > 0.3 for acceptable performance
- [ ] Set exploration rate to minimum (0.05) in production
- [ ] Enable model versioning (save with timestamps)
- [ ] Add A/B testing to compare RL vs rule-based recommendations
- [ ] Implement gradual rollout (10% → 50% → 100% traffic)
- [ ] Set up alerts for reward degradation
- [ ] Create model rollback procedure
- [ ] Document hyperparameter changes in git
- [ ] Add unit tests for reward calculation

## Next Steps

1. **A/B Testing Framework**: Compare RL recommendations vs rule-based
2. **Multi-Objective Optimization**: Balance engagement, diversity, and novelty
3. **Contextual Bandits**: Faster adaptation to user preferences
4. **Deep Learning**: Scale to larger state/action spaces
5. **Meta-Learning**: Transfer learning across users with similar personalities

## References

- Sutton & Barto: *Reinforcement Learning: An Introduction*
- [OpenAI Spinning Up](https://spinningup.openai.com/)
- [David Silver's RL Course](https://www.davidsilver.uk/teaching/)
