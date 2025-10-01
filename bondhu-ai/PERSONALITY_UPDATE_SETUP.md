# Personality Update Pipeline - Setup Guide

## Overview

The personality update pipeline automatically aggregates user interaction insights (from chat and entertainment) and updates personality profiles daily.

## Architecture

### Components

1. **Scheduler** (`core/scheduler.py`)
   - APScheduler running background tasks
   - Daily personality updates at 2 AM
   - Weekly cleanup of old insights (90+ days)

2. **Update Endpoint** (`api/routes/chat.py`)
   - `/api/v1/chat/personality/update/{user_id}` - Update single user
   - Aggregates insights from last 30 days
   - Applies dampening factor (0.1) to prevent drastic changes

3. **Admin API** (`api/routes/admin.py`)
   - Manual task triggering
   - System health monitoring
   - Task history viewing

4. **Database Tables**
   - `chat_personality_insights` - Chat-based personality analysis
   - `entertainment_interactions` - Entertainment feedback with personality insights
   - `user_personality_profiles` - Big Five trait scores
   - `system_tasks` - Task execution logs

## Setup Instructions

### 1. Install Dependencies

```bash
cd bondhu-ai
pip install -r requirements.txt
```

New dependency added: `APScheduler==3.10.4`

### 2. Run Database Migrations

Execute these SQL files in your Supabase dashboard:

```sql
-- Create chat personality insights table
-- File: bondhu-landing/database/add_chat_personality_insights.sql

-- Create system tasks table
-- File: bondhu-landing/database/add_system_tasks_table.sql
```

### 3. Configure Admin API Key

In production, set environment variable:

```bash
ADMIN_API_KEY=your-secure-random-key-here
```

Update `api/routes/admin.py` to use:
```python
if x_admin_key != os.getenv("ADMIN_API_KEY"):
```

### 4. Start Backend

```bash
cd bondhu-ai
python main.py
```

The scheduler will start automatically and log:
```
Background scheduler started with personality update tasks
```

## Usage

### Automatic Updates

The scheduler runs automatically:
- **Daily at 2:00 AM** - Updates all active users (last 7 days)
- **Sunday at 3:00 AM** - Cleans up insights older than 90 days

### Manual Updates

#### Single User Update (Frontend)

Users can trigger their own update from the UI:

```typescript
import { bondhuAPI } from '@/lib/api-client'

const result = await bondhuAPI.updatePersonalityProfile(userId)
console.log(result.data.insights_processed) // Number of insights used
console.log(result.data.trait_changes) // Changes to Big Five traits
```

#### Trigger All Users (Admin API)

```bash
curl -X POST http://localhost:8000/api/v1/admin/tasks/personality-update/trigger \
  -H "X-Admin-Key: admin-dev-key-change-in-production"
```

#### System Health Check

```bash
curl http://localhost:8000/api/v1/admin/system/health \
  -H "X-Admin-Key: admin-dev-key-change-in-production"
```

Response:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "scheduler_running": true,
    "scheduled_jobs": [
      {
        "id": "personality_update",
        "name": "Update all user personalities",
        "next_run_time": "2025-10-02T02:00:00",
        "trigger": "cron[hour='2', minute='0']"
      }
    ],
    "last_personality_update": {
      "task_name": "personality_update",
      "executed_at": "2025-10-01T02:00:00",
      "users_processed": 45,
      "successful_updates": 43,
      "failed_updates": 2,
      "status": "completed_with_errors"
    },
    "active_users_count": 45
  }
}
```

#### View Task History

```bash
curl "http://localhost:8000/api/v1/admin/tasks/history?limit=20" \
  -H "X-Admin-Key: admin-dev-key-change-in-production"
```

## How It Works

### Personality Update Flow

1. **Collection Phase**
   - Fetch chat insights from `chat_personality_insights` (last 30 days)
   - Fetch entertainment insights from `entertainment_interactions` (last 30 days)

2. **Aggregation Phase**
   - Sum all personality adjustments by trait
   - Apply dampening factor: `new_value = current + (sum * 0.1)`
   - Clamp values between 0-100

3. **Update Phase**
   - Update `user_personality_profiles` table
   - Return trait changes for monitoring

### Example Update

User has these insights over 30 days:
```
Chat insights: 
  - Openness: +2.0 (creative language, curiosity)
  - Conscientiousness: +1.5 (planning, goals)

Entertainment insights:
  - Openness: +1.0 (diverse music preferences)
  - Extraversion: -0.5 (preference for solo content)
```

Aggregated adjustments:
```
Openness: +3.0
Conscientiousness: +1.5
Extraversion: -0.5
```

After dampening (×0.1):
```
Openness: +0.3 (50.0 → 50.3)
Conscientiousness: +0.15 (50.0 → 50.15)
Extraversion: -0.05 (50.0 → 49.95)
```

### Why Dampening?

The 0.1 dampening factor prevents:
- Drastic personality changes from short-term behavior
- Overreaction to outlier interactions
- Unstable recommendation algorithms

Over time, consistent patterns accumulate into meaningful trait shifts.

## Monitoring

### Logs

Watch the scheduler logs:
```bash
tail -f logs/bondhu.log | grep "personality_update"
```

### Database Queries

Check recent tasks:
```sql
SELECT * FROM system_tasks 
WHERE task_name = 'personality_update' 
ORDER BY executed_at DESC 
LIMIT 10;
```

Check personality changes:
```sql
SELECT 
  user_id,
  openness,
  conscientiousness,
  extraversion,
  agreeableness,
  neuroticism,
  updated_at
FROM user_personality_profiles
WHERE updated_at > NOW() - INTERVAL '1 day'
ORDER BY updated_at DESC;
```

## Troubleshooting

### Scheduler Not Running

Check logs for:
```
Failed to start scheduler: [error message]
```

Common issues:
- Missing APScheduler dependency
- Database connection issues
- Timezone configuration

### No Updates Happening

1. Check active users count:
```sql
SELECT COUNT(DISTINCT user_id) 
FROM chat_messages 
WHERE timestamp > NOW() - INTERVAL '7 days';
```

2. Check for insights:
```sql
SELECT COUNT(*) 
FROM chat_personality_insights 
WHERE timestamp > NOW() - INTERVAL '30 days';
```

3. Verify scheduler status via admin API

### Manual Recovery

If automated tasks fail, run manual update for all users:
```bash
curl -X POST http://localhost:8000/api/v1/admin/tasks/personality-update/trigger \
  -H "X-Admin-Key: your-admin-key"
```

## Security Notes

⚠️ **Important Security Considerations:**

1. **Admin API Key**
   - Change default key in production: `admin-dev-key-change-in-production`
   - Store in environment variable
   - Rotate periodically

2. **Rate Limiting**
   - Add rate limiting to admin endpoints
   - Implement IP whitelisting for production

3. **Logging**
   - Don't log user IDs in public logs
   - Redact sensitive personality data

4. **Database Access**
   - Use service role for scheduler tasks
   - Implement RLS policies correctly

## Performance

### Expected Load

- **Daily update**: ~100ms per user
- **1000 active users**: ~2 minutes total
- **Database queries**: ~5 per user

### Optimization

If updates take too long:
1. Add database indexes on timestamp columns
2. Batch updates in chunks
3. Use connection pooling
4. Consider async processing queue

## Next Steps

After implementing Task 5, proceed to Task 6:
- Implement RL training loop
- Build reward function
- Optimize recommendation algorithms

See `DEVELOPMENT.md` for the complete roadmap.
