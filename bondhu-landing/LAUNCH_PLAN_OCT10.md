# 🚀 Launch Plan - October 10, 2025 (8 DAYS)

**Current Date:** October 2, 2025  
**Launch Date:** October 10, 2025  
**Days Remaining:** 8 days

---

## 📊 CURRENT STATUS

### ✅ What's Working:
- Chat functionality (with personality awareness)
- Dashboard UI with stats cards
- User authentication & profiles
- Personality assessment onboarding

### 🔴 Critical Issues:
1. **Chat UX is broken** (messages disappear on reload)
2. **Music integration** - Not implemented
3. **Video integration** - Not implemented
4. **Personality learning from chat** - Not implemented
5. **Performance issues** - No caching layer

### 🟡 Can Be Delayed:
- Game integration (complex, push to v1.1)
- Advanced analytics
- Achievement system polish

---

## 🎯 LAUNCH REQUIREMENTS (By Oct 10)

### Must Have (P0):
1. ✅ **Chat persistence** - Messages survive reload
2. ✅ **Redis caching** - Performance optimization
3. ✅ **Music integration** - Spotify + YouTube API
4. ✅ **Video integration** - YouTube API
5. ✅ **Personality learning** - From chat sentiment data
6. ✅ **Session tracking** - Proper user sessions

### Nice to Have (P1):
- Real-time typing indicators
- Video/music recommendations based on personality
- Wellness score calculation from sentiment

### Future (P2):
- Game integration (Memory Palace, etc.)
- Advanced caching strategies
- WebSocket real-time updates

---

## 🔥 REDIS & CELERY ANALYSIS

### **Should You Use Redis?**
**YES - ABSOLUTELY CRITICAL** ✅

**Why:**
1. **Chat sentiment analysis** needs fast access (checked on every message)
2. **Personality context** fetched frequently (every chat interaction)
3. **Music/Video preferences** will be queried often
4. **Session state** needs to be reliable
5. **API rate limiting** for YouTube/Spotify APIs

**What to Cache:**
```
Priority 1 (Immediate):
- Personality context (30 min TTL)
- Chat sentiment history (60 min TTL)
- User session state (session duration TTL)

Priority 2 (Week 2):
- Music preferences from Spotify (24 hour TTL)
- Video preferences from YouTube (24 hour TTL)
- Playlist recommendations (12 hour TTL)

Priority 3 (Future):
- API rate limit counters (1 min TTL)
- Trending content (6 hour TTL)
```

---

### **Should You Use Celery?**
**YES - FOR BACKGROUND TASKS** ✅

**Why:**
1. **Music fetching** - Spotify API calls can take 2-5 seconds
2. **Video fetching** - YouTube API calls take 1-3 seconds
3. **Personality analysis** - LLM processing takes 1-2 seconds
4. **Sentiment aggregation** - Don't block chat responses

**What Tasks:**
```python
# Immediate (Week 1):
@celery.task
async def fetch_spotify_preferences(user_id: str):
    """Background: Fetch user's Spotify data (playlists, top tracks)"""
    
@celery.task
async def fetch_youtube_preferences(user_id: str):
    """Background: Fetch user's YouTube data (subscriptions, playlists)"""
    
@celery.task
async def analyze_chat_sentiment_batch(user_id: str):
    """Background: Analyze last N messages for personality insights"""
    
@celery.task
async def update_personality_profile(user_id: str):
    """Background: Update personality based on chat sentiment"""

# Future (Week 2):
@celery.task
async def generate_recommendations(user_id: str):
    """Background: Generate music/video recommendations"""
```

**Benefits:**
- Chat responses stay fast (< 1 second)
- Heavy API calls don't block UI
- Can retry failed API calls automatically
- Better error handling

---

## 🏗️ ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (Port 3000)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Chat    │  │  Music   │  │  Video   │  │Dashboard │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│               Next.js API Routes (/api/*)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ /api/chat    │  │ /api/music   │  │ /api/video   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Chat Service → Gemini Pro → Personality Context     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Music Service → Spotify API → User Preferences      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Video Service → YouTube API → User Preferences      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Personality Agent → Sentiment Analysis → Learning   │  │
│  └──────────────────────────────────────────────────────┘  │
└───────┬──────────────────┬──────────────────┬──────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Redis Cache    │  │ Celery Workers  │  │   Supabase DB   │
│  (Port 6379)    │  │  (Background)   │  │   (Postgres)    │
│                 │  │                 │  │                 │
│ - Personality   │  │ - Fetch Music   │  │ - Users         │
│ - Chat Sentiment│  │ - Fetch Video   │  │ - Chat Messages │
│ - Session State │  │ - Analyze Chat  │  │ - Personality   │
│ - API Limits    │  │ - Update Profile│  │ - Activity Stats│
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## 📅 8-DAY IMPLEMENTATION PLAN

### **Day 1 (Oct 2) - Infrastructure Setup** ⚡
**Time:** 4-6 hours

1. **Set Up Redis** (2 hours)
   - Use Upstash (free tier, serverless)
   - No local installation needed
   - Auto-scales with usage

2. **Set Up Celery** (2 hours)
   - Install Redis as message broker
   - Configure worker processes
   - Create task queue structure

3. **Update Configuration** (1 hour)
   - Add Redis connection strings
   - Update environment variables
   - Test connections

**Deliverable:** Redis + Celery running locally

---

### **Day 2 (Oct 3) - Chat Persistence & Caching** 🔄
**Time:** 6-8 hours

1. **Fix Chat Message Persistence** (3 hours)
   - Load messages from Supabase on mount
   - Save every message to database
   - Handle loading states

2. **Implement Redis Caching for Personality** (2 hours)
   - Cache personality context (30 min TTL)
   - Cache chat sentiment summary (60 min TTL)
   - Add cache invalidation logic

3. **Implement Session Tracking** (2 hours)
   - Create session on dashboard mount
   - Track activities in session
   - End session on leave

**Deliverable:** Chat works perfectly, no more lost messages

---

### **Day 3 (Oct 4) - Music Integration Part 1** 🎵
**Time:** 6-8 hours

1. **Spotify OAuth Integration** (3 hours)
   - Set up Spotify Developer account
   - Implement OAuth flow
   - Get access tokens

2. **Fetch Spotify Preferences** (3 hours)
   - Get user's top tracks/artists
   - Get user's playlists
   - Get saved albums

3. **Create Celery Task** (1 hour)
   - Background task to fetch Spotify data
   - Store in Supabase + Redis cache
   - Handle API errors

**Deliverable:** Spotify integration working

---

### **Day 4 (Oct 5) - Music Integration Part 2** 🎶
**Time:** 6-8 hours

1. **YouTube Music Integration** (3 hours)
   - Google OAuth for YouTube
   - Fetch subscriptions
   - Fetch playlists

2. **Music Preference Analysis** (2 hours)
   - Extract music genres
   - Identify mood patterns
   - Store in personality profile

3. **Music Dashboard Card** (2 hours)
   - Show recently played
   - Show top genres
   - Show listening stats

**Deliverable:** Music fully integrated

---

### **Day 5 (Oct 6) - Video Integration** 📺
**Time:** 6-8 hours

1. **YouTube API Integration** (3 hours)
   - Fetch user subscriptions (channels)
   - Fetch user playlists
   - Fetch liked videos

2. **Video Preference Analysis** (2 hours)
   - Extract video categories
   - Identify content preferences
   - Store in personality profile

3. **Video Dashboard Card** (2 hours)
   - Show subscriptions count
   - Show top categories
   - Show recent activity

**Deliverable:** Video fully integrated

---

### **Day 6 (Oct 7) - Personality Learning from Chat** 🧠
**Time:** 6-8 hours

1. **Sentiment Analysis Pipeline** (3 hours)
   - Aggregate sentiment scores from messages
   - Calculate mood trends over time
   - Detect emotional patterns

2. **Personality Update Logic** (3 hours)
   - Update personality traits based on sentiment
   - Adjust chat style based on mood
   - Store personality evolution history

3. **Celery Background Task** (1 hour)
   - Batch process messages every hour
   - Update personality profile automatically
   - Cache updated context in Redis

**Deliverable:** Personality learns from chat

---

### **Day 7 (Oct 8) - Polish & Integration Testing** ✨
**Time:** 8 hours

1. **End-to-End Testing** (3 hours)
   - Test full user journey
   - Test cache invalidation
   - Test API error handling

2. **Performance Optimization** (2 hours)
   - Optimize Redis cache keys
   - Add query indexes in Supabase
   - Minimize API calls

3. **UI/UX Polish** (3 hours)
   - Loading states for music/video
   - Error messages
   - Empty states

**Deliverable:** Everything works smoothly

---

### **Day 8-9 (Oct 9-10) - Deployment & Launch Prep** 🚀
**Time:** 8 hours

1. **Deploy Redis** (1 hour)
   - Upstash production setup
   - Configure connection strings

2. **Deploy Celery Workers** (2 hours)
   - Set up Railway/Render workers
   - Configure auto-scaling

3. **Deploy Backend** (2 hours)
   - Update environment variables
   - Test production endpoints

4. **Deploy Frontend** (1 hour)
   - Vercel deployment
   - Configure domain

5. **Final Testing** (2 hours)
   - Production smoke tests
   - Load testing
   - Fix any bugs

**Deliverable:** Live on October 10th! 🎉

---

## 🛠️ TECHNICAL IMPLEMENTATION

### **1. Redis Setup (Upstash - Recommended)**

**Why Upstash:**
- ✅ Serverless (no infrastructure management)
- ✅ Free tier: 10K commands/day
- ✅ Global edge network
- ✅ REST API (no TCP connection issues)
- ✅ 1-click setup

**Setup Steps:**
```bash
# 1. Create account at upstash.com
# 2. Create Redis database
# 3. Copy UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN

# Backend (.env)
REDIS_URL=<UPSTASH_REDIS_REST_URL>
REDIS_TOKEN=<UPSTASH_REDIS_REST_TOKEN>

# Frontend (.env.local)
UPSTASH_REDIS_REST_URL=<URL>
UPSTASH_REDIS_REST_TOKEN=<TOKEN>
```

**Python Setup:**
```python
# requirements.txt
redis==5.0.1
hiredis==2.3.2  # Optional: faster parsing

# core/cache/redis_client.py
import redis
from core.config import get_config

class RedisClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            config = get_config()
            cls._instance = redis.from_url(
                config.redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
        return cls._instance

def get_redis() -> redis.Redis:
    return RedisClient()
```

**Next.js Setup:**
```typescript
// lib/cache/redis.ts
import { Redis } from '@upstash/redis';

export const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!
});

// Helper functions
export async function getCached<T>(key: string): Promise<T | null> {
  const cached = await redis.get(key);
  return cached as T | null;
}

export async function setCached<T>(
  key: string, 
  value: T, 
  ttlSeconds: number
): Promise<void> {
  await redis.setex(key, ttlSeconds, JSON.stringify(value));
}
```

---

### **2. Celery Setup**

**Installation:**
```bash
# requirements.txt
celery[redis]==5.3.4
```

**Configuration:**
```python
# core/celery_app.py
from celery import Celery
from core.config import get_config

config = get_config()

celery_app = Celery(
    'bondhu',
    broker=config.redis_url,
    backend=config.redis_url,
    include=[
        'core.tasks.music',
        'core.tasks.video',
        'core.tasks.personality'
    ]
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000
)
```

**Example Tasks:**
```python
# core/tasks/music.py
from core.celery_app import celery_app
from core.integrations.spotify import SpotifyClient
from core.cache.redis_client import get_redis
import json

@celery_app.task(bind=True, max_retries=3)
def fetch_spotify_preferences(self, user_id: str, access_token: str):
    """Fetch Spotify preferences in background"""
    try:
        spotify = SpotifyClient(access_token)
        
        # Fetch data
        top_tracks = spotify.get_top_tracks(limit=50)
        playlists = spotify.get_playlists()
        saved_albums = spotify.get_saved_albums()
        
        # Store in cache
        redis_client = get_redis()
        cache_key = f"music:spotify:{user_id}"
        
        data = {
            'top_tracks': top_tracks,
            'playlists': playlists,
            'saved_albums': saved_albums,
            'fetched_at': datetime.now().isoformat()
        }
        
        # Cache for 24 hours
        redis_client.setex(cache_key, 86400, json.dumps(data))
        
        # Also store in Supabase for persistence
        # ... (Supabase insert logic)
        
        return {'status': 'success', 'tracks_count': len(top_tracks)}
        
    except Exception as e:
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
```

**Start Workers:**
```bash
# Development
celery -A core.celery_app worker --loglevel=info --pool=solo

# Production
celery -A core.celery_app worker --loglevel=info --concurrency=4
```

---

### **3. Chat Persistence Implementation**

**Database Schema Update:**
```sql
-- Ensure chat_messages table exists
CREATE TABLE IF NOT EXISTS chat_messages (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  message_text TEXT NOT NULL,
  sender_type TEXT NOT NULL CHECK (sender_type IN ('user', 'ai')),
  session_id TEXT,
  mood_detected TEXT,
  sentiment_score NUMERIC(3, 2),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast queries
CREATE INDEX idx_chat_messages_user_created 
  ON chat_messages(user_id, created_at DESC);

-- Enable RLS
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own messages" ON chat_messages
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own messages" ON chat_messages
  FOR INSERT WITH CHECK (auth.uid() = user_id);
```

**Next.js API Route:**
```typescript
// src/app/api/chat/history/route.ts
import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';
import { redis, getCached, setCached } from '@/lib/cache/redis';

export async function GET(request: Request) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '50');
    
    // Try cache first
    const cacheKey = `chat:history:${user.id}:${limit}`;
    const cached = await getCached<any[]>(cacheKey);
    
    if (cached) {
      return NextResponse.json({ messages: cached, cached: true });
    }
    
    // Fetch from database
    const { data: messages, error } = await supabase
      .from('chat_messages')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: true })
      .limit(limit);
    
    if (error) throw error;
    
    // Cache for 5 minutes
    await setCached(cacheKey, messages, 300);
    
    return NextResponse.json({ messages, cached: false });
    
  } catch (error) {
    console.error('Chat history error:', error);
    return NextResponse.json(
      { error: 'Failed to load chat history' },
      { status: 500 }
    );
  }
}
```

**Frontend Update:**
```typescript
// src/components/ui/enhanced-chat.tsx
useEffect(() => {
  const loadChatHistory = async () => {
    try {
      setIsLoading(true);
      
      const response = await fetch('/api/chat/history?limit=50');
      const { messages: historyMessages } = await response.json();
      
      // Transform to frontend format
      const formattedMessages = historyMessages.map((msg: any) => ({
        id: msg.id,
        sender: msg.sender_type === 'user' ? 'user' : 'bondhu',
        message: msg.message_text,
        timestamp: new Date(msg.created_at).toLocaleTimeString(),
        mood: msg.mood_detected,
        sentiment: msg.sentiment_score
      }));
      
      setMessages(formattedMessages);
      
    } catch (error) {
      console.error('Failed to load chat history:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  loadChatHistory();
}, []);

// Update sendMessage to save to DB
const sendMessage = async () => {
  if (!newMessage.trim() || !userId) return;
  
  // Optimistic UI update
  const userMsg = {
    id: `temp-${Date.now()}`,
    sender: 'user',
    message: newMessage,
    timestamp: new Date().toLocaleTimeString()
  };
  setMessages(prev => [...prev, userMsg]);
  setNewMessage('');
  setIsTyping(true);
  
  try {
    // Call backend (which stores in DB)
    const response = await chatApi.sendMessage(userId, newMessage);
    
    // Update with real ID from backend
    const aiMsg = {
      id: response.message_id || `ai-${Date.now()}`,
      sender: 'bondhu',
      message: response.response,
      timestamp: new Date(response.timestamp).toLocaleTimeString(),
      hasPersonalityContext: response.has_personality_context
    };
    
    setMessages(prev => [...prev, aiMsg]);
    
    // Invalidate cache so next load gets fresh data
    await fetch('/api/chat/invalidate-cache', { method: 'POST' });
    
  } catch (error) {
    console.error('Chat error:', error);
    setError('Failed to send message');
  } finally {
    setIsTyping(false);
  }
};
```

---

### **4. Personality Learning from Chat Sentiment**

**Backend Task:**
```python
# core/tasks/personality.py
from core.celery_app import celery_app
from core.database.supabase_client import get_supabase_client
from core.cache.redis_client import get_redis
import json
from datetime import datetime, timedelta
from statistics import mean, stdev

@celery_app.task
def analyze_chat_sentiment_batch(user_id: str):
    """
    Analyze recent chat messages and update personality profile
    Runs periodically (every hour) or triggered after N messages
    """
    supabase = get_supabase_client()
    redis_client = get_redis()
    
    # Fetch recent messages (last 24 hours)
    cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
    
    result = supabase.table('chat_messages') \
        .select('sentiment_score, mood_detected, created_at') \
        .eq('user_id', user_id) \
        .eq('sender_type', 'user') \
        .gte('created_at', cutoff) \
        .order('created_at', desc=False) \
        .execute()
    
    messages = result.data
    
    if len(messages) < 5:
        return {'status': 'insufficient_data'}
    
    # Calculate sentiment statistics
    scores = [msg['sentiment_score'] for msg in messages if msg['sentiment_score']]
    
    avg_sentiment = mean(scores) if scores else 0.5
    sentiment_volatility = stdev(scores) if len(scores) > 1 else 0
    
    # Detect dominant mood
    moods = [msg['mood_detected'] for msg in messages if msg['mood_detected']]
    mood_counts = {}
    for mood in moods:
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
    dominant_mood = max(mood_counts, key=mood_counts.get) if mood_counts else 'neutral'
    
    # Update personality insights
    insights = {
        'avg_sentiment_24h': round(avg_sentiment, 2),
        'sentiment_volatility': round(sentiment_volatility, 2),
        'dominant_mood': dominant_mood,
        'message_count_24h': len(messages),
        'analyzed_at': datetime.now().isoformat()
    }
    
    # Store in Redis (1 hour TTL)
    redis_client.setex(
        f"personality:sentiment:{user_id}",
        3600,
        json.dumps(insights)
    )
    
    # Update personality profile in Supabase
    personality_updates = {}
    
    # Adjust personality traits based on sentiment patterns
    if avg_sentiment < 0.3:
        # User showing signs of negative mood
        personality_updates['needs_support'] = True
        personality_updates['communication_style'] = 'empathetic_supportive'
    elif avg_sentiment > 0.7:
        # User in positive mood
        personality_updates['communication_style'] = 'enthusiastic_energetic'
    
    if sentiment_volatility > 0.3:
        # High emotional variability
        personality_updates['emotional_stability'] = 'variable'
    
    # Update personality profile
    if personality_updates:
        supabase.table('profiles') \
            .update({
                'personality_data': supabase.func.jsonb_set(
                    'personality_data',
                    '{chat_insights}',
                    json.dumps(insights)
                )
            }) \
            .eq('id', user_id) \
            .execute()
    
    # Invalidate personality cache
    redis_client.delete(f"personality:context:{user_id}")
    
    return {
        'status': 'success',
        'insights': insights,
        'updates_applied': personality_updates
    }
```

**Trigger Task After Chat:**
```python
# core/chat/gemini_service.py
async def send_message(self, user_id: str, message: str, session_id: str):
    # ... existing logic ...
    
    # Store message with sentiment
    await self._store_message(user_id, message, response, sentiment_score, mood)
    
    # Check if we should trigger personality analysis
    message_count = await self._get_recent_message_count(user_id)
    
    if message_count % 10 == 0:  # Every 10 messages
        from core.tasks.personality import analyze_chat_sentiment_batch
        analyze_chat_sentiment_batch.delay(user_id)
    
    return result
```

---

### **5. Music Integration (Spotify + YouTube)**

**Spotify Setup:**
```python
# core/integrations/spotify.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyClient:
    def __init__(self, access_token: str):
        self.sp = spotipy.Spotify(auth=access_token)
    
    def get_top_tracks(self, limit=50, time_range='medium_term'):
        """Get user's top tracks (last 6 months)"""
        return self.sp.current_user_top_tracks(
            limit=limit,
            time_range=time_range  # short_term, medium_term, long_term
        )
    
    def get_top_artists(self, limit=50):
        """Get user's top artists"""
        return self.sp.current_user_top_artists(limit=limit)
    
    def get_playlists(self):
        """Get user's playlists"""
        return self.sp.current_user_playlists()
    
    def get_saved_albums(self):
        """Get user's saved albums"""
        return self.sp.current_user_saved_albums()
    
    def analyze_music_preferences(self):
        """Analyze music preferences for personality insights"""
        top_tracks = self.get_top_tracks()
        top_artists = self.get_top_artists()
        
        # Extract genres
        genres = []
        for artist in top_artists['items']:
            genres.extend(artist['genres'])
        
        # Count genre frequency
        genre_counts = {}
        for genre in genres:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        # Get top genres
        top_genres = sorted(
            genre_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Audio features analysis
        track_ids = [track['id'] for track in top_tracks['items']]
        audio_features = self.sp.audio_features(track_ids)
        
        # Calculate average audio features
        avg_features = {
            'energy': mean([f['energy'] for f in audio_features if f]),
            'valence': mean([f['valence'] for f in audio_features if f]),
            'danceability': mean([f['danceability'] for f in audio_features if f]),
            'acousticness': mean([f['acousticness'] for f in audio_features if f])
        }
        
        return {
            'top_genres': [g[0] for g in top_genres],
            'audio_profile': avg_features,
            'total_tracks': len(top_tracks['items']),
            'total_artists': len(top_artists['items'])
        }
```

**YouTube Music Integration:**
```python
# core/integrations/youtube.py
from googleapiclient.discovery import build

class YouTubeClient:
    def __init__(self, access_token: str):
        self.youtube = build('youtube', 'v3', credentials=access_token)
    
    def get_subscriptions(self):
        """Get user's channel subscriptions"""
        request = self.youtube.subscriptions().list(
            part='snippet',
            mine=True,
            maxResults=50
        )
        return request.execute()
    
    def get_playlists(self):
        """Get user's playlists"""
        request = self.youtube.playlists().list(
            part='snippet,contentDetails',
            mine=True,
            maxResults=50
        )
        return request.execute()
    
    def get_liked_videos(self):
        """Get user's liked videos"""
        request = self.youtube.videos().list(
            part='snippet',
            myRating='like',
            maxResults=50
        )
        return request.execute()
    
    def analyze_video_preferences(self):
        """Analyze video preferences for personality insights"""
        subscriptions = self.get_subscriptions()
        playlists = self.get_playlists()
        
        # Extract categories from channel descriptions
        categories = []
        for sub in subscriptions.get('items', []):
            # Extract category keywords from channel description
            description = sub['snippet']['description'].lower()
            # ... category extraction logic ...
        
        return {
            'subscription_count': len(subscriptions.get('items', [])),
            'playlist_count': len(playlists.get('items', [])),
            'top_categories': categories[:10]
        }
```

**Celery Task:**
```python
# core/tasks/music.py
@celery_app.task(bind=True)
def fetch_music_preferences(self, user_id: str, spotify_token: str, youtube_token: str):
    """Fetch music preferences from Spotify and YouTube"""
    redis_client = get_redis()
    
    try:
        # Fetch Spotify data
        spotify = SpotifyClient(spotify_token)
        spotify_data = spotify.analyze_music_preferences()
        
        # Fetch YouTube data
        youtube = YouTubeClient(youtube_token)
        youtube_data = youtube.analyze_video_preferences()
        
        # Combine data
        music_profile = {
            'spotify': spotify_data,
            'youtube': youtube_data,
            'fetched_at': datetime.now().isoformat()
        }
        
        # Cache for 24 hours
        redis_client.setex(
            f"music:profile:{user_id}",
            86400,
            json.dumps(music_profile)
        )
        
        # Store in Supabase
        supabase = get_supabase_client()
        supabase.table('music_preferences').upsert({
            'user_id': user_id,
            'preferences': music_profile,
            'updated_at': datetime.now().isoformat()
        }).execute()
        
        return {'status': 'success', 'profile': music_profile}
        
    except Exception as e:
        raise self.retry(exc=e, countdown=60)
```

---

### **6. Video Integration (YouTube)**

Similar structure to music, using YouTube Data API v3.

---

## 📊 CACHING STRATEGY

### **Cache Layers:**

```
┌─────────────────────────────────────────────────┐
│  Layer 1: Browser Cache (localStorage)         │
│  TTL: 5-10 minutes                              │
│  - Active session state                         │
│  - UI preferences                               │
└───────────────┬─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────┐
│  Layer 2: Redis Cache                           │
│  TTL: 30 min - 24 hours                         │
│  - Personality context (30 min)                 │
│  - Chat sentiment (1 hour)                      │
│  - Music/Video preferences (24 hours)           │
│  - API rate limits (1 min)                      │
└───────────────┬─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────┐
│  Layer 3: Supabase (PostgreSQL)                 │
│  Permanent storage                              │
│  - User profiles                                │
│  - Chat messages                                │
│  - Personality data                             │
│  - Activity stats                               │
└─────────────────────────────────────────────────┘
```

### **Cache Keys Structure:**
```
personality:context:{user_id}           # 30 min
personality:sentiment:{user_id}         # 1 hour
chat:history:{user_id}:{limit}          # 5 min
music:profile:{user_id}                 # 24 hours
music:spotify:{user_id}                 # 24 hours
video:youtube:{user_id}                 # 24 hours
session:active:{user_id}                # session duration
ratelimit:spotify:{user_id}             # 1 min
ratelimit:youtube:{user_id}             # 1 min
```

---

## 🚦 PRIORITIES FOR OCTOBER 10

### **Week 1 (Oct 2-5):**
1. ✅ Redis + Celery setup (Day 1)
2. ✅ Chat persistence (Day 2)
3. ✅ Music integration (Days 3-4)
4. ✅ Session tracking (Day 2)

### **Week 2 (Oct 6-10):**
5. ✅ Video integration (Day 6)
6. ✅ Personality learning (Day 7)
7. ✅ Testing & polish (Day 8)
8. ✅ Deployment (Days 9-10)

---

## ✅ SUCCESS METRICS

By October 10, we should have:

- [ ] Chat messages persist across reloads
- [ ] Response time < 1 second for cached data
- [ ] Spotify integration working (OAuth + data fetch)
- [ ] YouTube integration working (OAuth + data fetch)
- [ ] Personality updates from chat sentiment
- [ ] Music/video preferences cached efficiently
- [ ] Celery handling background tasks
- [ ] Redis caching all hot data
- [ ] Zero data loss scenarios
- [ ] Clean error handling

---

## 🎯 NEXT STEPS

**RIGHT NOW:**
1. Set up Upstash Redis account (10 minutes)
2. Install Redis & Celery packages (5 minutes)
3. I'll create all the code implementations

**Want me to start implementing?** Which part should I begin with?

1. 🔴 Redis + Celery setup (infrastructure)
2. 🟡 Chat persistence (critical UX fix)
3. 🟢 Music integration (feature)
4. 🔵 Video integration (feature)

Let me know and I'll start building! 🚀
