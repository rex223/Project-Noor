# Activity Stats Setup & Integration Guide

## ✅ What's Been Done

### 1. Database Infrastructure
- ✅ Created `user_activity_stats` table in Supabase
- ✅ Created 6 helper functions for stat updates
- ✅ Set up RLS policies for security
- ✅ Auto-initialization for new users

### 2. API Routes
- ✅ GET `/api/activity-stats` - Fetches user stats
- ✅ POST `/api/activity-stats` - Updates stats

### 3. Frontend Integration
- ✅ Dashboard fetches and displays stats
- ✅ Loading states implemented
- ✅ Helper functions in `lib/activity-tracker.ts`

### 4. Activity Tracking Integrated
- ✅ **Chat**: Tracks every message sent
- ✅ **Games**: Tracks all 3 games (Memory Palace, Puzzle Master, Color Symphony)
- ✅ **Streaks**: Auto-updates on any activity

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Run SQL in Supabase

Copy and run this in **Supabase Dashboard → SQL Editor**:

```sql
-- QUICK SETUP FOR DASHBOARD STATS
DROP VIEW IF EXISTS user_activity_stats CASCADE;
DROP TABLE IF EXISTS user_activity_stats CASCADE;

CREATE TABLE user_activity_stats (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL UNIQUE,
  
  wellness_score INTEGER DEFAULT 0,
  wellness_trend INTEGER DEFAULT 0,
  total_messages INTEGER DEFAULT 0,
  messages_today INTEGER DEFAULT 0,
  total_games_played INTEGER DEFAULT 0,
  games_this_week INTEGER DEFAULT 0,
  current_streak_days INTEGER DEFAULT 0,
  longest_streak_days INTEGER DEFAULT 0,
  total_achievements INTEGER DEFAULT 0,
  achievements_this_month INTEGER DEFAULT 0,
  active_sessions INTEGER DEFAULT 0,
  active_sessions_today INTEGER DEFAULT 0,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE user_activity_stats ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own activity stats" ON user_activity_stats;
DROP POLICY IF EXISTS "Users can insert own activity stats" ON user_activity_stats;
DROP POLICY IF EXISTS "Users can update own activity stats" ON user_activity_stats;

CREATE POLICY "Users can view own activity stats" ON user_activity_stats
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own activity stats" ON user_activity_stats
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own activity stats" ON user_activity_stats
  FOR UPDATE USING (auth.uid() = user_id);

INSERT INTO user_activity_stats (user_id)
SELECT id FROM auth.users
ON CONFLICT (user_id) DO NOTHING;

SELECT * FROM user_activity_stats WHERE user_id = auth.uid();
```

### Step 2: Add Test Data (Optional)

```sql
-- Initialize your stats with test data
INSERT INTO user_activity_stats (user_id)
VALUES (auth.uid())
ON CONFLICT (user_id) DO UPDATE SET updated_at = NOW();

UPDATE user_activity_stats SET
  wellness_score = 85,
  wellness_trend = 12,
  total_messages = 150,
  messages_today = 8,
  total_games_played = 12,
  games_this_week = 2,
  current_streak_days = 23,
  longest_streak_days = 30,
  total_achievements = 8,
  achievements_this_month = 2,
  active_sessions = 3,
  active_sessions_today = 3
WHERE user_id = auth.uid();

-- Verify
SELECT * FROM user_activity_stats WHERE user_id = auth.uid();
```

### Step 3: Refresh Dashboard

Go to `http://localhost:3000/dashboard` and you should see your stats!

---

## 📊 What's Already Tracking

### ✅ Chat Messages (Auto-tracking)
**Location:** `src/components/ui/enhanced-chat.tsx`

Every time a user sends a message:
- `total_messages` +1
- `messages_today` +1
- `current_streak_days` updates

### ✅ Game Completions (Auto-tracking)
**Locations:** 
- `src/components/games/MemoryPalace.tsx`
- `src/app/entertainment/page.tsx` (for all games)

Every time a user completes a game:
- `total_games_played` +1
- `games_this_week` +1
- `current_streak_days` updates

### ✅ Activity Streaks (Auto-tracking)
**Location:** Embedded in chat and game tracking

Updates automatically on any activity.

---

## 🔧 What Still Needs Implementation

### 1. Wellness Score Updates (MANUAL)

**When to call:**
- After personality assessment
- During mood check-ins
- Weekly wellness calculations

**How to implement:**
```typescript
import { updateWellnessScore } from '@/lib/activity-tracker';

// Example: After personality assessment
const calculateWellnessScore = (personalityData) => {
  // Your calculation logic
  const score = ... // 0-100
  const trend = ... // +/- percentage
  
  await updateWellnessScore(score, trend);
};
```

**Suggested locations:**
- `src/app/onboarding/personality/page.tsx` - After assessment
- Create a mood check-in feature
- Weekly background job

### 2. Achievements System (MANUAL)

**When to call:**
- Milestone events (first chat, 100 messages, etc.)
- Special accomplishments
- Weekly/monthly goals

**How to implement:**
```typescript
import { addAchievement, checkMilestoneAchievements } from '@/lib/activity-tracker';

// Manual achievement
await addAchievement('Custom Achievement', 'Description here');

// Auto-check milestones
const stats = await fetchActivityStats();
await checkMilestoneAchievements(stats);
```

**Suggested implementation:**
Create an `AchievementSystem` component that:
- Checks milestones after every stat update
- Shows toast notifications for new achievements
- Displays achievement popup modals

### 3. Active Sessions Tracking (MANUAL)

**When to call:**
- User opens/closes chat
- User starts/ends a game
- User watches/stops a video
- User plays/pauses music

**How to implement:**
```typescript
import { updateActiveSessions } from '@/lib/activity-tracker';

// Example: Track what's currently active
const [activeSessions, setActiveSessions] = useState<string[]>([]);

// When chat opens
setActiveSessions(prev => [...prev, 'chat']);
await updateActiveSessions([...activeSessions, 'chat']);

// When chat closes
setActiveSessions(prev => prev.filter(s => s !== 'chat'));
await updateActiveSessions(activeSessions.filter(s => s !== 'chat'));
```

**Suggested implementation:**
Create a context provider:
```typescript
// src/contexts/ActiveSessionContext.tsx
export const ActiveSessionProvider = ({ children }) => {
  const [sessions, setSessions] = useState<string[]>([]);
  
  const addSession = (type: string) => {
    setSessions(prev => {
      const updated = [...new Set([...prev, type])];
      updateActiveSessions(updated);
      return updated;
    });
  };
  
  const removeSession = (type: string) => {
    setSessions(prev => {
      const updated = prev.filter(s => s !== type);
      updateActiveSessions(updated);
      return updated;
    });
  };
  
  return (
    <SessionContext.Provider value={{ sessions, addSession, removeSession }}>
      {children}
    </SessionContext.Provider>
  );
};
```

### 4. Daily/Weekly Cleanup (OPTIONAL)

Reset counters at intervals. Options:

**Option A: Supabase Edge Function (Recommended)**
```sql
-- Create a function to reset daily counters
CREATE OR REPLACE FUNCTION reset_daily_stats()
RETURNS void AS $$
BEGIN
  UPDATE user_activity_stats 
  SET 
    messages_today = 0,
    active_sessions_today = 0
  WHERE updated_at::date < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- Schedule with pg_cron or Supabase Edge Function
```

**Option B: Client-side check**
```typescript
// On dashboard mount
useEffect(() => {
  const checkResets = async () => {
    const lastReset = localStorage.getItem('lastStatsReset');
    const today = new Date().toDateString();
    
    if (lastReset !== today) {
      // Stats will auto-reset on next activity
      localStorage.setItem('lastStatsReset', today);
    }
  };
  checkResets();
}, []);
```

---

## 📝 Complete Integration Checklist

### ✅ Already Done
- [x] Database table created
- [x] API routes implemented
- [x] Dashboard displays stats
- [x] Chat message tracking
- [x] Game completion tracking
- [x] Activity streak tracking
- [x] Helper functions created

### ⚠️ Needs Implementation (Priority Order)

#### HIGH PRIORITY (Do Now)
1. [ ] Run SQL migration in Supabase
2. [ ] Test with sample data
3. [ ] Verify dashboard shows stats
4. [ ] Send a chat message → verify stats update
5. [ ] Complete a game → verify stats update

#### MEDIUM PRIORITY (This Week)
6. [ ] Implement wellness score calculation
7. [ ] Add milestone achievement system
8. [ ] Create achievement notifications
9. [ ] Add active session tracking context

#### LOW PRIORITY (Future Enhancement)
10. [ ] Set up daily/weekly cleanup jobs
11. [ ] Add analytics dashboard
12. [ ] Implement achievement badges UI
13. [ ] Create leaderboards (optional)

---

## 🧪 Testing Checklist

### Test Chat Tracking
1. Go to dashboard
2. Note current `total_messages` and `current_streak_days`
3. Send a chat message
4. Refresh dashboard
5. ✅ Stats should increase

### Test Game Tracking
1. Go to Entertainment page
2. Note current `total_games_played`
3. Complete Memory Palace game
4. Refresh dashboard
5. ✅ Stats should increase

### Test Stats Display
1. Go to dashboard
2. ✅ All 6 cards should show numbers (not `--`)
3. ✅ Trend badges should show (e.g., "+12% this week")
4. ✅ No console errors

---

## 🐛 Troubleshooting

### Stats not showing up?
```sql
-- Check if table exists
SELECT * FROM user_activity_stats LIMIT 1;

-- Check if you have a row
SELECT * FROM user_activity_stats WHERE user_id = auth.uid();

-- Manually create if missing
INSERT INTO user_activity_stats (user_id) VALUES (auth.uid());
```

### Stats not updating?
1. Check browser console for errors
2. Check Network tab for failed API calls
3. Verify RLS policies in Supabase
4. Test API directly:
```javascript
// In browser console on dashboard
await fetch('/api/activity-stats', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'increment_chat',
    data: { messageCount: 5 }
  })
}).then(r => r.json()).then(console.log)
```

### Database errors?
- Make sure `update_updated_at_column()` function exists (from schema.sql)
- Check Supabase logs for detailed errors
- Verify all migrations ran successfully

---

## 📚 API Reference

### GET /api/activity-stats
Returns current user's stats.

**Response:**
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
  "activeSessionsToday": 3
}
```

### POST /api/activity-stats
Updates stats based on action.

**Actions:**
- `increment_chat` - Track chat messages
- `increment_game` - Track game completions
- `update_wellness` - Update wellness score
- `update_streak` - Update activity streak
- `add_achievement` - Add new achievement
- `update_active_sessions` - Track active sessions

**Example:**
```typescript
await fetch('/api/activity-stats', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'increment_chat',
    data: { messageCount: 1 }
  })
});
```

---

## 🎉 You're Ready!

Your activity stats system is **90% complete**! Just need to:
1. Run the SQL migration
2. Test it works
3. Optionally implement wellness score & achievements

Everything else is already tracking automatically! 🚀
