# 🏗️ Bondhu AI System Architecture Summary

## 📊 Current System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     BONDHU AI ARCHITECTURE                       │
│                    Mental Health AI Companion                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                           │
│                        (Next.js 14 App)                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │ Dashboard  │  │  Chat UI   │  │ Entertainment│ │ Settings │ │
│  │   Page     │  │ (Enhanced) │  │     Hub      │ │   Page   │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │           Personality Assessment (Big Five Test)            │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │ REST API (axios)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API LAYER (FastAPI)                   │
│                     http://localhost:8000                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Authentication & OAuth Endpoints                         │  │
│  │  • POST /auth/spotify/connect → Spotify OAuth            │  │
│  │  • POST /auth/youtube/connect → YouTube OAuth            │  │
│  │  • POST /auth/steam/connect   → Steam API Key Setup      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Personality Context APIs (✅ COMPLETE)                   │  │
│  │  • GET /personality/user-context/{id}                     │  │
│  │  • GET /personality/llm-context/{id}                      │  │
│  │  • GET /personality/onboarding-status/{id}               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Chat Endpoints (🔨 TO BUILD)                            │  │
│  │  • POST /chat/send          → Send message with context   │  │
│  │  • GET  /chat/history/{id}  → Get chat history           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Data Collection Status (🔨 TO BUILD)                    │  │
│  │  • GET /users/{id}/data-collection-status                 │  │
│  │  • GET /users/{id}/connected-services                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              LANGCHAIN + LANGGRAPH AGENT LAYER                   │
│                   (✅ COMPLETE & RUNNING)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │            PersonalityOrchestrator (LangGraph)          │    │
│  │                                                          │    │
│  │    ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐ │    │
│  │    │ Music  │   │ Video  │   │ Gaming │   │Personality│   │
│  │    │ Agent  │   │ Agent  │   │ Agent  │   │  Agent   │    │
│  │    └───┬────┘   └───┬────┘   └───┬────┘   └───┬────┘    │
│  │        │            │            │            │          │
│  │        └────────────┴────────────┴────────────┘          │
│  │                      │                                    │
│  │              Parallel Execution                           │
│  │                      │                                    │
│  │              ┌───────▼────────┐                          │
│  │              │ State Manager  │                          │
│  │              │ (Memory Saver) │                          │
│  │              └────────────────┘                          │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Each Agent Uses:                                                │
│  • Google Gemini Pro (LangChain Google GenAI)                   │
│  • Tool-calling architecture                                     │
│  • Conversation memory                                           │
│  • Personality-aware prompts                                     │
│                                                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│            BACKGROUND JOB SCHEDULER (🔨 TO BUILD)               │
│                      (APScheduler)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Task: collect_user_entertainment_data(user_id)         │    │
│  │  Schedule: Every 4 days per user                        │    │
│  │                                                          │    │
│  │  Flow:                                                   │    │
│  │  1. Fetch data from Spotify API                         │    │
│  │  2. Fetch data from YouTube API                         │    │
│  │  3. Fetch data from Steam API                           │    │
│  │  4. Store in Supabase                                   │    │
│  │  5. Trigger PersonalityEvolutionEngine                  │    │
│  │  6. Update personality profile                          │    │
│  │  7. Regenerate LLM context                              │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PERSONALITY EVOLUTION ENGINE                   │
│                         (🔨 TO BUILD)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Input: Entertainment data from all sources             │    │
│  │                                                          │    │
│  │  Process:                                                │    │
│  │  1. Load existing personality profile                   │    │
│  │  2. Run multi-agent analysis via orchestrator           │    │
│  │  3. Calculate personality changes                       │    │
│  │  4. Weighted averaging (confidence-based)               │    │
│  │  5. Update Big Five scores                              │    │
│  │  6. Generate new LLM context (2000+ chars)              │    │
│  │                                                          │    │
│  │  Output: Updated personality profile in Supabase        │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER (Supabase)                     │
│                   PostgreSQL + Row Level Security                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  ✅ EXISTING TABLES:                                    │    │
│  │  • profiles (with personality scores)                   │    │
│  │  • auth.users (Supabase Auth)                           │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  🔨 TO CREATE TABLES:                                   │    │
│  │  • user_music_data        (Spotify, Last.fm data)       │    │
│  │  • user_video_data        (YouTube data)                │    │
│  │  • user_gaming_data       (Steam data)                  │    │
│  │  • entertainment_connections (OAuth tokens)             │    │
│  │  • data_collection_jobs   (Job tracking)                │    │
│  │  • chat_history           (Chat logs)                   │    │
│  │  • personality_history    (Personality snapshots)       │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  All tables have RLS policies for user data isolation            │
│                                                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL INTEGRATIONS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Spotify    │  │   YouTube    │  │    Steam     │         │
│  │     API      │  │   Data API   │  │     API      │         │
│  │ (OAuth 2.0)  │  │ (OAuth 2.0)  │  │ (API Key)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             Google Gemini Pro (Primary LLM)               │  │
│  │         Used by all agents and chat system                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow: End-to-End Journey

### 1️⃣ User Onboarding Flow
```
User Signs Up
    ↓
Personality Assessment (Big Five Test)
    ↓
Scores stored in Supabase (profiles table)
    ↓
LLM Context generated (2000+ character prompt)
    ↓
User Dashboard activated
```

### 2️⃣ Service Connection Flow (🔨 TO BUILD)
```
User clicks "Connect Spotify"
    ↓
Redirect to Spotify OAuth
    ↓
User authorizes
    ↓
Callback receives tokens
    ↓
Tokens stored in entertainment_connections
    ↓
First data collection triggered immediately
    ↓
Background job scheduled (every 4 days)
```

### 3️⃣ Background Data Collection (🔨 TO BUILD)
```
APScheduler triggers (every 4 days)
    ↓
For each user with connected services:
    ├─ Fetch Spotify data → user_music_data
    ├─ Fetch YouTube data → user_video_data
    └─ Fetch Steam data → user_gaming_data
    ↓
Trigger PersonalityEvolutionEngine
    ↓
Multi-agent analysis (Music, Video, Gaming agents)
    ↓
Personality Agent synthesizes results
    ↓
Calculate weighted personality updates
    ↓
Update profiles table
    ↓
Regenerate LLM context
    ↓
Ready for next chat session
```

### 4️⃣ Chat Session Flow (🔨 TO BUILD)
```
User sends message
    ↓
Backend loads personality profile
    ↓
Backend fetches LLM context
    ↓
Construct personality-aware prompt
    ↓
Send to Gemini Pro
    ↓
Receive empathetic response
    ↓
Store in chat_history
    ↓
Return to user
```

---

## 🎯 What We Have vs. What We Need

### ✅ COMPLETE (Already Built)
1. **Multi-Agent System**
   - ✅ 4 specialized agents (Music, Video, Gaming, Personality)
   - ✅ LangGraph orchestration
   - ✅ Google Gemini Pro integration
   - ✅ Personality-aware prompts
   - ✅ State management and memory

2. **Backend API**
   - ✅ FastAPI server running
   - ✅ Personality context endpoints
   - ✅ Database integration
   - ✅ Supabase client

3. **Frontend**
   - ✅ Next.js app with authentication
   - ✅ Personality assessment (Big Five test)
   - ✅ Dashboard UI
   - ✅ Chat UI components
   - ✅ Entertainment Hub UI

4. **Database**
   - ✅ User profiles with personality scores
   - ✅ LLM context storage
   - ✅ RLS policies

### 🔨 TO BUILD (Implementation Needed)

1. **Database Schema** (4 hours)
   - ❌ Entertainment data tables
   - ❌ OAuth token storage
   - ❌ Chat history table
   - ❌ Job tracking table

2. **External API Integration** (15 hours)
   - ❌ Spotify OAuth + data collection
   - ❌ YouTube OAuth + data collection
   - ❌ Steam API + data collection

3. **Background Jobs** (8 hours)
   - ❌ APScheduler setup
   - ❌ Data collection tasks
   - ❌ Job monitoring

4. **Personality Evolution** (10 hours)
   - ❌ Evolution engine
   - ❌ Weighted update logic
   - ❌ Context regeneration

5. **Chat Backend** (8 hours)
   - ❌ Chat endpoints
   - ❌ Gemini integration with context
   - ❌ History storage

6. **Frontend Integration** (12 hours)
   - ❌ Service connection buttons
   - ❌ OAuth redirect handling
   - ❌ Status displays
   - ❌ Chat API integration

**Total Estimated Time**: ~57 hours (~7-8 working days)

---

## 🎨 Technology Stack Summary

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom + shadcn/ui
- **State Management**: React hooks
- **API Client**: Axios

### Backend
- **Framework**: FastAPI (Python 3.12)
- **API Style**: REST
- **Authentication**: Supabase Auth
- **Documentation**: OpenAPI/Swagger

### AI/ML
- **Primary LLM**: Google Gemini Pro
- **Agent Framework**: LangChain
- **Orchestration**: LangGraph
- **ML Libraries**: scikit-learn, numpy, pandas

### Database
- **Primary DB**: Supabase (PostgreSQL)
- **Security**: Row Level Security (RLS)
- **Real-time**: Supabase Realtime

### Infrastructure
- **Background Jobs**: APScheduler (planned)
- **Hosting**: TBD (Vercel for frontend, Railway/Render for backend)
- **Monitoring**: TBD (Sentry planned)

### External APIs
- **Music**: Spotify Web API, Last.fm API
- **Video**: YouTube Data API v3
- **Gaming**: Steam Web API
- **LLM**: Google Gemini Pro API

---

## 🔐 Security & Privacy

### Data Isolation
- ✅ User-specific RLS policies on all tables
- ✅ OAuth tokens encrypted at rest
- ✅ No cross-user data mixing
- ✅ User can disconnect services and delete data

### API Security
- ✅ JWT-based authentication (Supabase)
- ✅ Rate limiting (planned)
- ✅ CORS policies
- ✅ HTTPS only in production

### Privacy Compliance
- ✅ User owns their data
- ✅ Data export functionality (planned)
- ✅ Service disconnection with data deletion (planned)
- ✅ Transparent data usage

---

## 📈 Scalability Considerations

### Current Architecture (MVP)
- **Concurrent Users**: 100-500 users
- **Background Jobs**: APScheduler (single process)
- **Database**: Supabase (shared instance)
- **LLM Calls**: Rate-limited to Gemini quotas

### Future Scaling (If Needed)
- **Concurrent Users**: 10,000+ users
- **Background Jobs**: Migrate to Celery + Redis
- **Database**: Supabase Pro or dedicated PostgreSQL
- **LLM Calls**: Implement caching and batching
- **Horizontal Scaling**: Multiple FastAPI workers

---

## 🎯 Success Criteria

### Technical
- ✅ 95%+ uptime for API
- ✅ <2s response time for chat
- ✅ <5min data collection per user
- ✅ 100% data isolation
- ✅ Zero cross-user data leaks

### User Experience
- ✅ <10s to connect a service
- ✅ Real-time personality updates
- ✅ Empathetic chat responses
- ✅ Transparent data usage

### Business
- ✅ 70%+ users connect 1+ service
- ✅ 50%+ users connect all 3 services
- ✅ 80%+ user retention after 7 days
- ✅ 90%+ positive sentiment in feedback

---

**This is an incredible system! Let's build it! 🚀**
