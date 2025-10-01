# 📋 Bondhu AI - Quick TODO Checklist

## 🔥 IMMEDIATE PRIORITIES (This Week)

### Day 1-2: Database Schema
- [ ] **1.1.1** Create `entertainment-data-schema.sql`
  - [ ] `user_music_data` table
  - [ ] `user_video_data` table  
  - [ ] `user_gaming_data` table
  - [ ] `entertainment_connections` table
  - [ ] RLS policies for all tables
  - [ ] Run migration on Supabase

### Day 3-4: Spotify Integration
- [ ] **1.2.1** Create OAuth endpoints
  - [ ] `api/routes/auth/spotify.py`
  - [ ] `/auth/spotify/connect` endpoint
  - [ ] `/auth/spotify/callback` endpoint
- [ ] **1.2.2** Build data collector
  - [ ] `utils/spotify/data_collector.py`
  - [ ] Fetch tracks, artists, genres
  - [ ] Transform and store in Supabase
- [ ] **1.2.3** Test with real Spotify account

### Day 5-6: Background Scheduler
- [ ] **1.3.1** Install APScheduler
- [ ] **1.3.2** Create scheduler config
  - [ ] `core/scheduler/config.py`
  - [ ] `core/scheduler/tasks.py`
- [ ] **1.3.3** Implement data collection task
  - [ ] `collect_user_entertainment_data(user_id)`
  - [ ] Schedule every 4 days
- [ ] **1.3.4** Test scheduled execution

### Day 7: Integration Test
- [ ] **Test complete flow**:
  - [ ] Connect Spotify account
  - [ ] Trigger data collection
  - [ ] Verify data in Supabase
  - [ ] Check next collection date

---

## 🎯 SPRINT 1 (Week 1-2): Backend Foundation

### ✅ Already Complete
- [x] Multi-agent system
- [x] LangGraph orchestration
- [x] Gemini Pro integration
- [x] FastAPI server
- [x] Personality profiles

### 🔨 To Complete

#### Database (4 hours)
- [ ] Create entertainment data tables
- [ ] Create data collection jobs table
- [ ] Add RLS policies
- [ ] Create indexes
- [ ] Run migrations

#### Spotify Integration (4 hours)
- [ ] OAuth flow
- [ ] Data collection functions
- [ ] Storage layer
- [ ] Error handling

#### YouTube Integration (4 hours)
- [ ] OAuth flow
- [ ] Data collection functions
- [ ] Storage layer
- [ ] Error handling

#### Steam Integration (3 hours)
- [ ] API key setup endpoint
- [ ] Data collection functions
- [ ] Storage layer
- [ ] Error handling

#### Background Scheduler (6 hours)
- [ ] Install APScheduler
- [ ] Create task definitions
- [ ] Implement scheduling logic
- [ ] Add job monitoring
- [ ] Add error notifications

---

## 🚀 SPRINT 2 (Week 3-4): Intelligence Layer

#### Personality Evolution Engine (8 hours)
- [ ] Create `PersonalityEvolutionEngine` class
- [ ] Implement weighted personality updates
- [ ] Track personality history
- [ ] Regenerate LLM context
- [ ] Test with real data

#### Data Status API (3 hours)
- [ ] `/users/{id}/data-collection-status` endpoint
- [ ] `/users/{id}/connected-services` endpoint
- [ ] `/users/{id}/personality-history` endpoint

#### Frontend - Entertainment Hub (6 hours)
- [ ] Create service connection components
- [ ] Implement OAuth redirect handling
- [ ] Build connection status display
- [ ] Add disconnect functionality
- [ ] Style with existing design system

---

## 💬 SPRINT 3 (Week 5-6): Chat System

#### Chat Backend (8 hours)
- [ ] Create chat schema in Supabase
- [ ] `/chat/send` endpoint
- [ ] `/chat/history/{user_id}` endpoint
- [ ] Gemini integration with personality context
- [ ] Chat history storage

#### Chat Frontend (6 hours)
- [ ] Update `EnhancedChat` component
- [ ] Integrate with chat API
- [ ] Show personality context status
- [ ] Display chat history
- [ ] Add feedback mechanism

#### Status Display (4 hours)
- [ ] `DataCollectionStatus` component
- [ ] `NextCollectionCountdown` component
- [ ] Service health indicators
- [ ] Integration into dashboard

---

## 🧪 SPRINT 4 (Week 7-8): Testing & Launch

#### Testing (8 hours)
- [ ] Unit tests for data collectors
- [ ] Integration tests for OAuth flows
- [ ] End-to-end personality update test
- [ ] Load testing for background jobs
- [ ] API endpoint tests

#### Monitoring (6 hours)
- [ ] Structured logging setup
- [ ] Performance metrics tracking
- [ ] Error tracking and alerts
- [ ] Admin dashboard for monitoring

#### Documentation (4 hours)
- [ ] API documentation (OpenAPI/Swagger)
- [ ] User guide for connecting services
- [ ] Admin guide for monitoring
- [ ] Deployment guide

#### Launch Prep (4 hours)
- [ ] Environment variable management
- [ ] Production configuration
- [ ] Database backups setup
- [ ] Deploy to production
- [ ] Monitor initial users

---

## 📦 QUICK WINS (Can do anytime)

- [ ] Add loading states to all frontend components
- [ ] Add error boundaries in React
- [ ] Implement retry logic for failed API calls
- [ ] Add request rate limiting
- [ ] Create health check dashboard
- [ ] Add user onboarding tour
- [ ] Implement feature flags
- [ ] Add analytics tracking

---

## 🐛 KNOWN ISSUES TO FIX

- [ ] None yet - system is fresh! 🎉

---

## 📝 NOTES

### Architecture Decisions Made:
1. ✅ Using Google Gemini Pro (not OpenAI)
2. ✅ APScheduler for background jobs (not Celery for MVP)
3. ✅ Supabase for all data storage
4. ✅ 4-day data collection interval
5. ✅ User-specific data isolation

### Key Implementation Details:
- Background jobs run every 4 days per user
- Chat sessions load fresh personality context
- External API data cached in Supabase
- Personality evolution uses weighted averaging
- All entertainment data is user-isolated with RLS

### Security Considerations:
- OAuth tokens encrypted in Supabase
- RLS policies on all tables
- API rate limiting required
- User data completely isolated
- Service disconnection must delete user data

---

## 🎯 TODAY'S FOCUS

**Start Here**:
1. Create `entertainment-data-schema.sql`
2. Run migration on Supabase
3. Create Spotify OAuth endpoints
4. Test Spotify connection flow

**Goal**: Have Spotify integration working end-to-end by end of day!

---

**Last Updated**: October 1, 2025
**Status**: Phase 1 - Backend Foundation
**Next Milestone**: Complete Spotify Integration
