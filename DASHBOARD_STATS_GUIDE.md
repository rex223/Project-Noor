# Dashboard Activity Stats System

## Overview
The dashboard "Your Progress" section now uses **dynamic, real-time data** from the database instead of placeholder values. This document explains the complete system architecture.

---

## Database Schema

### Table: `user_activity_stats`

**Location:** `database/user-activity-stats.sql`

**Purpose:** Stores aggregated activity statistics for each user to power the 6 dashboard cards.

**Key Columns:**

1. **Wellness Score**
   - `wellness_score` (0-100): Current wellness score
   - `wellness_trend` (+/-): Percentage change this week
   - `last_mood_update`: Timestamp of last update

2. **Chat Sessions**
   - `total_chat_sessions`: Total number of chat sessions
   - `total_messages`: Total messages sent
   - `messages_today`: Messages sent today (resets daily)
   - `last_chat_date`: Timestamp of last chat

3. **Games Played**
   - `total_games_played`: Total games completed
   - `games_this_week`: Games played this week
   - `last_game_date`: Timestamp of last game
   - `favorite_game`: Most played game name

4. **Growth Streak**
   - `current_streak_days`: Current consecutive days streak
   - `longest_streak_days`: Personal best streak
   - `last_activity_date`: Last activity timestamp

5. **Achievements**
   - `total_achievements`: Total achievements earned
   - `achievements_this_month`: Achievements earned this month
   - `achievement_list` (JSONB): Array of achievement objects

6. **Active Sessions**
   - `active_sessions`: Number of currently active sessions
   - `active_sessions_today`: Active sessions today
   - `active_session_types` (JSONB): Array of session types ['chat', 'game', 'video', 'music']

---

## Database Functions

The schema includes **6 helper functions** to update stats from anywhere in your app:

### 1. `increment_chat_session(user_id, message_count)`
Increments chat session count and message count.

**Usage Example:**
```typescript
await supabase.rpc('increment_chat_session', {
  user_id: user.id,
  message_count: 1
})
```

### 2. `increment_game_played(user_id, game_name)`
Increments games played counter.

**Usage Example:**
```typescript
await supabase.rpc('increment_game_played', {
  user_id: user.id,
  game_name: 'Memory Palace'
})
```

### 3. `update_wellness_score(user_id, new_score, trend_change)`
Updates the wellness score and trend.

**Usage Example:**
```typescript
await supabase.rpc('update_wellness_score', {
  user_id: user.id,
  new_score: 85,
  trend_change: 12 // +12%
})
```

### 4. `update_streak(user_id)`
Calculates and updates the user's activity streak (auto-resets if >1 day gap).

**Usage Example:**
```typescript
await supabase.rpc('update_streak', {
  user_id: user.id
})
```

### 5. `add_achievement(user_id, achievement_name, achievement_description)`
Adds a new achievement to the user's list.

**Usage Example:**
```typescript
await supabase.rpc('add_achievement', {
  user_id: user.id,
  achievement_name: 'First Chat',
  achievement_description: 'Completed your first conversation with Bondhu'
})
```

### 6. `update_active_sessions(user_id, session_types)`
Updates the count of active sessions.

**Usage Example:**
```typescript
await supabase.rpc('update_active_sessions', {
  user_id: user.id,
  session_types: ['chat', 'game', 'video']
})
```

---

## API Routes

### GET `/api/activity-stats`

**Purpose:** Fetches the current user's activity statistics.

**Response Format:**
```json
{
  "wellnessScore": 85,
  "wellnessTrend": 12,
  "totalMessages": 150,
  "messagesToday": 8,
  "totalGamesPlayed": 12,
  "gamesThisWeek": 2,
  "currentStreakDays": 23,
  "longestStreakDays": 30,
  "totalAchievements": 8,
  "achievementsThisMonth": 2,
  "activeSessions": 3,
  "activeSessionsToday": 3,
  "lastActivityDate": "2025-10-02T10:30:00Z",
  "updatedAt": "2025-10-02T10:30:00Z"
}
```

**Usage in Frontend:**
```typescript
const response = await fetch('/api/activity-stats')
const stats = await response.json()
```

### POST `/api/activity-stats`

**Purpose:** Updates specific stats from the frontend.

**Request Body:**
```json
{
  "action": "increment_chat",
  "data": {
    "messageCount": 1
  }
}
```

**Available Actions:**
- `increment_chat` - Increment chat messages
- `increment_game` - Increment games played
- `update_wellness` - Update wellness score
- `update_streak` - Update activity streak
- `add_achievement` - Add new achievement
- `update_active_sessions` - Update active sessions

**Example Usage:**
```typescript
// When user sends a chat message
await fetch('/api/activity-stats', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'increment_chat',
    data: { messageCount: 1 }
  })
})

// When user completes a game
await fetch('/api/activity-stats', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'increment_game',
    data: { gameName: 'Puzzle Master' }
  })
})
```

---

## Frontend Integration

### Dashboard Page (`src/app/dashboard/page.tsx`)

**State Management:**
```typescript
const [activityStats, setActivityStats] = useState<any>(null)
```

**Data Fetching:**
```typescript
useEffect(() => {
  const getProfile = async () => {
    // ... existing profile fetch code ...
    
    // Fetch activity stats
    const response = await fetch('/api/activity-stats')
    if (response.ok) {
      const stats = await response.json()
      setActivityStats(stats)
    }
  }
  getProfile()
}, [])
```

**Component Usage:**
```tsx
<DashboardStats stats={activityStats} />
```

### Dashboard Stats Component (`src/components/ui/dashboard-stats.tsx`)

**Props Interface:**
```typescript
interface DashboardStatsProps {
  stats?: {
    wellnessScore?: number;
    wellnessTrend?: number;
    totalMessages?: number;
    messagesToday?: number;
    totalGamesPlayed?: number;
    gamesThisWeek?: number;
    currentStreakDays?: number;
    longestStreakDays?: number;
    totalAchievements?: number;
    achievementsThisMonth?: number;
    activeSessions?: number;
    activeSessionsToday?: number;
  } | null;
}
```

**Loading State:**
- Shows `--` when stats are null/undefined
- Shows real values once loaded
- Automatically calculates trend text based on data

---

## Setup Instructions

### 1. Run the Database Migration

```bash
# In Supabase Dashboard SQL Editor, run these in order:
1. database/schema.sql (if not already run)
2. database/personality-schema-update.sql (if not already run)
3. database/user-activity-stats.sql (NEW - run this now!)
```

### 2. Initialize Stats for Existing Users

The migration automatically:
- Creates a trigger to initialize stats for new users
- Inserts default stats for all existing users (ON CONFLICT DO NOTHING)

### 3. Verify the Setup

```sql
-- Check if table exists
SELECT * FROM user_activity_stats LIMIT 1;

-- Check your own stats
SELECT * FROM user_activity_stats WHERE user_id = auth.uid();
```

---

## How to Update Stats in Your App

### Chat Component Integration

Add this to your chat message handler:

```typescript
// In src/components/ui/enhanced-chat.tsx or wherever you handle chat
const handleSendMessage = async (message: string) => {
  // ... existing message sending code ...
  
  // Update stats
  await fetch('/api/activity-stats', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: 'increment_chat',
      data: { messageCount: 1 }
    })
  })
}
```

### Game Component Integration

Add this when a game is completed:

```typescript
// In game components (PuzzleMaster, MemoryPalace, ColorSymphony)
const handleGameComplete = async () => {
  // ... existing game completion code ...
  
  // Update stats
  await fetch('/api/activity-stats', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: 'increment_game',
      data: { gameName: 'Memory Palace' } // or 'Puzzle Master', 'Color Symphony'
    })
  })
}
```

### Wellness Score Updates

Add this to personality assessments or mood tracking:

```typescript
const updateWellness = async (score: number, trend: number) => {
  await fetch('/api/activity-stats', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: 'update_wellness',
      data: { score, trend }
    })
  })
}
```

### Achievement System

Add this when milestones are reached:

```typescript
const unlockAchievement = async (name: string, description: string) => {
  await fetch('/api/activity-stats', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: 'add_achievement',
      data: { name, description }
    })
  })
}
```

---

## Testing the System

### 1. Test with SQL (Quick)

```sql
-- Manually set some test data for your user
UPDATE user_activity_stats SET
  wellness_score = 85,
  wellness_trend = 12,
  total_messages = 150,
  messages_today = 8,
  total_games_played = 12,
  games_this_week = 2,
  current_streak_days = 23,
  total_achievements = 8,
  achievements_this_month = 2,
  active_sessions = 3
WHERE user_id = auth.uid();
```

### 2. Test with API Calls

```typescript
// In browser console on dashboard page
await fetch('/api/activity-stats', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'increment_chat',
    data: { messageCount: 5 }
  })
})

// Refresh the page to see the update!
```

### 3. Test Database Functions Directly

```sql
-- Test increment chat
SELECT increment_chat_session(auth.uid(), 5);

-- Test game increment
SELECT increment_game_played(auth.uid(), 'Memory Palace');

-- Check the results
SELECT * FROM user_activity_stats WHERE user_id = auth.uid();
```

---

## Next Steps

### Recommended Integrations:

1. **Chat Component** ✅ HIGH PRIORITY
   - Update stats on every message sent
   - Track conversation sessions

2. **Game Components** ✅ HIGH PRIORITY
   - Update stats on game completion
   - Track favorite game

3. **Activity Tracking** ✅ HIGH PRIORITY
   - Update streak daily on any activity
   - Track active sessions (chat open, game in progress, etc.)

4. **Wellness/Mood System** ⚠️ MEDIUM PRIORITY
   - Calculate wellness score from personality data
   - Update trends weekly

5. **Achievement System** ⚠️ MEDIUM PRIORITY
   - Define achievement milestones
   - Award achievements automatically

---

## Maintenance

### Daily/Weekly Cleanup Tasks (Optional)

You can create these as cron jobs or Supabase Edge Functions:

```sql
-- Reset daily counters at midnight
UPDATE user_activity_stats SET
  messages_today = 0,
  active_sessions_today = 0
WHERE last_activity_date::DATE < CURRENT_DATE;

-- Reset weekly counters
UPDATE user_activity_stats SET
  games_this_week = 0
WHERE last_game_date < DATE_TRUNC('week', CURRENT_DATE);

-- Reset monthly counters
UPDATE user_activity_stats SET
  achievements_this_month = 0
WHERE updated_at < DATE_TRUNC('month', CURRENT_DATE);
```

---

## Troubleshooting

### Stats Not Showing Up?

1. **Check if table exists:**
   ```sql
   SELECT * FROM user_activity_stats LIMIT 1;
   ```

2. **Check if your user has a row:**
   ```sql
   SELECT * FROM user_activity_stats WHERE user_id = auth.uid();
   ```

3. **Manually initialize if missing:**
   ```sql
   INSERT INTO user_activity_stats (user_id) VALUES (auth.uid());
   ```

### API Route Not Working?

1. Check browser console for errors
2. Check Supabase logs for RLS policy issues
3. Verify RLS policies allow SELECT/UPDATE for authenticated users
4. Check that functions have GRANT EXECUTE permissions

### Stats Not Updating?

1. Verify POST requests are succeeding (check Network tab)
2. Check Supabase function execution logs
3. Manually test the database function directly
4. Verify RLS policies aren't blocking updates

---

## Production Checklist

- [ ] Run `user-activity-stats.sql` migration in production
- [ ] Verify all existing users have stats rows
- [ ] Test API routes in production
- [ ] Integrate chat message tracking
- [ ] Integrate game completion tracking
- [ ] Set up daily/weekly/monthly cleanup tasks (optional)
- [ ] Monitor database performance (add indexes if needed)
- [ ] Set up analytics/logging for stat updates

---

## Summary

✅ **Database:** New `user_activity_stats` table with 6 helper functions  
✅ **API:** GET and POST endpoints at `/api/activity-stats`  
✅ **Frontend:** Dashboard fetches and displays real data  
✅ **Loading States:** Shows `--` while loading, real values when ready  
✅ **Dynamic Trends:** Calculates trend text based on actual data  

**Your dashboard is now fully dynamic!** 🎉

Next: Integrate stat updates throughout your app wherever users perform activities (chat, games, wellness checks, etc.).
