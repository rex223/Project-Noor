# 🚀 Bondhu AI - Complete Implementation Roadmap

## Current Status ✅
- ✅ Multi-agent system (Music, Video, Gaming, Personality agents)
- ✅ LangGraph orchestration
- ✅ Google Gemini Pro integration
- ✅ FastAPI backend server running
- ✅ Supabase personality profiles integration
- ✅ Big Five personality assessment (frontend)
- ✅ Next.js frontend with authentication

---

## PHASE 1: Backend Data Collection Infrastructure 🔧
**Goal**: Set up automated background data collection every 4 days

### 1.1 Supabase Schema for Entertainment Data (PRIORITY 1) 📊
**Status**: ❌ Not Started

**Tasks**:
- [ ] Create `user_music_data` table schema
  - [ ] Add RLS policies for user isolation
  - [ ] Create indexes for performance
  - [ ] Add data validation constraints
  
- [ ] Create `user_video_data` table schema
  - [ ] Add RLS policies for user isolation
  - [ ] Create indexes for performance
  - [ ] Add data validation constraints
  
- [ ] Create `user_gaming_data` table schema
  - [ ] Add RLS policies for user isolation
  - [ ] Create indexes for performance
  - [ ] Add data validation constraints

- [ ] Create `entertainment_connections` table
  - [ ] Track which services users have connected
  - [ ] Store OAuth tokens securely
  - [ ] Track last collection timestamps
  - [ ] Add connection status (active/expired/disconnected)

- [ ] Create `data_collection_jobs` table
  - [ ] Track background job execution
  - [ ] Store job status and errors
  - [ ] Track next scheduled collection date

**Files to Create**:
- `bondhu-ai/database/entertainment-data-schema.sql`
- `bondhu-ai/database/data-collection-jobs-schema.sql`

**Estimated Time**: 3-4 hours

---

### 1.2 External API Integration Layer (PRIORITY 2) 🔌
**Status**: ❌ Not Started (Partial infrastructure exists in utils/)

**Tasks**:

#### Spotify Integration:
- [ ] Implement OAuth 2.0 flow
  - [ ] Create `/api/v1/auth/spotify/connect` endpoint
  - [ ] Create `/api/v1/auth/spotify/callback` endpoint
  - [ ] Store access/refresh tokens in Supabase
  
- [ ] Build data collection functions
  - [ ] Fetch recently played tracks (last 50)
  - [ ] Fetch top tracks (short/medium/long term)
  - [ ] Fetch top artists with genres
  - [ ] Fetch saved playlists and liked songs
  - [ ] Get audio features for tracks
  - [ ] Extract listening patterns (time of day, frequency)

- [ ] Create data storage functions
  - [ ] Transform Spotify API response to our schema
  - [ ] Store in `user_music_data` table
  - [ ] Update `entertainment_connections` table

#### YouTube Integration:
- [ ] Implement OAuth 2.0 flow
  - [ ] Create `/api/v1/auth/youtube/connect` endpoint
  - [ ] Create `/api/v1/auth/youtube/callback` endpoint
  - [ ] Store access/refresh tokens in Supabase
  
- [ ] Build data collection functions
  - [ ] Fetch watch history
  - [ ] Fetch liked videos
  - [ ] Fetch subscribed channels
  - [ ] Extract video categories and topics
  - [ ] Analyze viewing patterns (duration, frequency)

- [ ] Create data storage functions
  - [ ] Transform YouTube API response to our schema
  - [ ] Store in `user_video_data` table
  - [ ] Update `entertainment_connections` table

#### Steam Integration:
- [ ] Implement Steam API integration (API Key based)
  - [ ] Create `/api/v1/auth/steam/connect` endpoint
  - [ ] Store Steam ID in Supabase
  
- [ ] Build data collection functions
  - [ ] Fetch owned games library
  - [ ] Get playtime statistics
  - [ ] Fetch achievements
  - [ ] Get recently played games
  - [ ] Extract gaming patterns

- [ ] Create data storage functions
  - [ ] Transform Steam API response to our schema
  - [ ] Store in `user_gaming_data` table
  - [ ] Update `entertainment_connections` table

**Files to Create/Update**:
- `api/routes/auth/spotify.py` (OAuth flow)
- `api/routes/auth/youtube.py` (OAuth flow)
- `api/routes/auth/steam.py` (API key setup)
- `utils/spotify/data_collector.py` (Enhanced)
- `utils/youtube/data_collector.py` (New)
- `utils/steam/data_collector.py` (Enhanced)
- `core/database/entertainment_service.py` (Data storage layer)

**Estimated Time**: 8-10 hours

---

### 1.3 Background Job Scheduler (PRIORITY 3) ⏰
**Status**: ❌ Not Started

**Tasks**:
- [ ] Set up task queue system
  - [ ] Install Celery + Redis OR use APScheduler for simpler setup
  - [ ] Configure task broker
  - [ ] Set up worker processes
  
- [ ] Create scheduled tasks
  - [ ] Task: `collect_user_entertainment_data(user_id)`
  - [ ] Schedule: Every 4 days per user
  - [ ] Error handling and retry logic
  - [ ] Rate limiting for API calls
  
- [ ] Build job management system
  - [ ] Create `/api/v1/admin/jobs/trigger-collection` endpoint
  - [ ] Create `/api/v1/admin/jobs/status` endpoint
  - [ ] Implement job monitoring and logging
  - [ ] Email notifications on job failures

- [ ] User-specific scheduling
  - [ ] Calculate next collection date per user
  - [ ] Stagger collection times to avoid API rate limits
  - [ ] Priority queue for newly connected services

**Files to Create**:
- `core/scheduler/tasks.py` (Background tasks)
- `core/scheduler/config.py` (Scheduler configuration)
- `api/routes/admin/jobs.py` (Admin endpoints)
- `celeryconfig.py` OR `scheduler_config.py` (Task config)

**Decision Point**: 
- **Option A**: Celery + Redis (More scalable, production-ready)
- **Option B**: APScheduler (Simpler, good for MVP, in-process)

**Estimated Time**: 6-8 hours

---

### 1.4 Personality Evolution Engine (PRIORITY 4) 🧠
**Status**: ⚠️ Partial (Agents exist, need evolution logic)

**Tasks**:
- [ ] Create `PersonalityEvolutionEngine` class
  - [ ] Load latest entertainment data from Supabase
  - [ ] Trigger multi-agent analysis via orchestrator
  - [ ] Compare new results with existing personality profile
  - [ ] Calculate personality drift/changes over time
  
- [ ] Implement personality update logic
  - [ ] Weighted averaging with previous scores
  - [ ] Confidence-based updates
  - [ ] Track personality evolution history
  - [ ] Generate updated LLM context
  
- [ ] Create personality history tracking
  - [ ] Store personality snapshots over time
  - [ ] Calculate trait stability scores
  - [ ] Detect significant personality changes
  
- [ ] Build LLM context regeneration
  - [ ] Update conversation guidelines based on new data
  - [ ] Regenerate agent-specific guidelines
  - [ ] Update Supabase `personality_llm_context` field

**Files to Create**:
- `core/personality/evolution_engine.py`
- `core/personality/context_generator.py` (Enhanced)
- `database/personality-history-schema.sql`
- `api/routes/personality_evolution.py` (Admin endpoints)

**Estimated Time**: 8-10 hours

---

### 1.5 Data Collection Status API (PRIORITY 5) 📈
**Status**: ❌ Not Started

**Tasks**:
- [ ] Create status endpoints
  - [ ] `GET /api/v1/users/{user_id}/data-collection-status`
  - [ ] `GET /api/v1/users/{user_id}/connected-services`
  - [ ] `GET /api/v1/users/{user_id}/personality-history`
  
- [ ] Build status service
  - [ ] Check last collection timestamps
  - [ ] Calculate next collection date
  - [ ] Show data freshness indicators
  - [ ] Track collection success/failure rates

**Files to Create**:
- `api/routes/user_status.py`
- `core/database/status_service.py`

**Estimated Time**: 3-4 hours

---

## PHASE 2: Frontend Integration 🎨
**Goal**: Connect Next.js frontend to backend services

### 2.1 Entertainment Hub - Service Connections (PRIORITY 6) 🔗
**Status**: ⚠️ Partial UI exists

**Tasks**:
- [ ] Create service connection components
  - [ ] `SpotifyConnectionButton.tsx`
  - [ ] `YouTubeConnectionButton.tsx`
  - [ ] `SteamConnectionForm.tsx`
  
- [ ] Implement OAuth flows
  - [ ] Handle OAuth redirect callbacks
  - [ ] Store connection status in state
  - [ ] Show connection success/error messages
  
- [ ] Build connection status display
  - [ ] Show connected services with badges
  - [ ] Display last data collection timestamp
  - [ ] Show "Connect" button for disconnected services
  - [ ] Allow service disconnection

**Files to Create/Update**:
- `bondhu-landing/src/components/entertainment/ServiceConnectionButton.tsx`
- `bondhu-landing/src/components/entertainment/ConnectionStatus.tsx`
- `bondhu-landing/src/app/entertainment/page.tsx` (Update)
- `bondhu-landing/src/lib/api/entertainment.ts` (New API client)

**Estimated Time**: 6-8 hours

---

### 2.2 Data Collection Status Display (PRIORITY 7) 📊
**Status**: ❌ Not Started

**Tasks**:
- [ ] Create status components
  - [ ] `DataCollectionStatus.tsx`
  - [ ] `NextCollectionCountdown.tsx`
  - [ ] `ServiceHealthIndicator.tsx`
  
- [ ] Build status dashboard
  - [ ] Show per-service collection status
  - [ ] Display next collection countdown
  - [ ] Show data freshness indicators
  - [ ] Show collection history (optional)

**Files to Create**:
- `bondhu-landing/src/components/entertainment/DataCollectionStatus.tsx`
- `bondhu-landing/src/components/entertainment/CollectionHistory.tsx`

**Estimated Time**: 4-5 hours

---

### 2.3 Chat Integration with Personality Context (PRIORITY 8) 💬
**Status**: ⚠️ Chat UI exists, needs backend integration

**Tasks**:
- [ ] Create chat API endpoints
  - [ ] `POST /api/v1/chat/send` - Send message with personality context
  - [ ] `GET /api/v1/chat/history/{user_id}` - Get chat history
  - [ ] `POST /api/v1/chat/feedback` - User feedback on responses
  
- [ ] Implement personality-aware chat
  - [ ] Load personality profile before each chat session
  - [ ] Generate LLM context from personality data
  - [ ] Send to Gemini with context
  - [ ] Store chat history in Supabase
  
- [ ] Build chat components
  - [ ] Update `EnhancedChat.tsx` with API integration
  - [ ] Add personality indicator in chat UI
  - [ ] Show "Loading personality context..." state
  - [ ] Handle empty personality profiles

**Files to Create/Update**:
- `api/routes/chat.py` (New)
- `core/chat/gemini_handler.py` (New)
- `database/chat-history-schema.sql` (New)
- `bondhu-landing/src/components/ui/enhanced-chat.tsx` (Update)
- `bondhu-landing/src/lib/api/chat.ts` (New)

**Estimated Time**: 8-10 hours

---

## PHASE 3: Testing & Optimization 🧪
**Goal**: Ensure system reliability and performance

### 3.1 Testing Infrastructure (PRIORITY 9)
**Status**: ⚠️ Basic tests exist

**Tasks**:
- [ ] Write unit tests
  - [ ] Test data collection functions
  - [ ] Test personality evolution logic
  - [ ] Test API endpoints
  
- [ ] Write integration tests
  - [ ] Test end-to-end data collection flow
  - [ ] Test OAuth flows
  - [ ] Test personality update workflow
  
- [ ] Load testing
  - [ ] Test background job performance
  - [ ] Test API rate limits
  - [ ] Test database query performance

**Files to Create**:
- `tests/integration/test_data_collection.py`
- `tests/integration/test_personality_evolution.py`
- `tests/integration/test_oauth_flows.py`
- `tests/load/test_background_jobs.py`

**Estimated Time**: 8-10 hours

---

### 3.2 Monitoring & Logging (PRIORITY 10) 📊
**Status**: ⚠️ Basic logging exists

**Tasks**:
- [ ] Set up application monitoring
  - [ ] Add structured logging
  - [ ] Track API response times
  - [ ] Monitor background job execution
  - [ ] Track external API rate limits
  
- [ ] Create admin dashboard
  - [ ] System health metrics
  - [ ] Data collection statistics
  - [ ] User connection status overview
  - [ ] Error tracking and alerts

**Files to Create**:
- `core/monitoring/metrics.py`
- `api/routes/admin/monitoring.py`
- `bondhu-landing/src/app/admin/monitoring/page.tsx`

**Estimated Time**: 6-8 hours

---

## PHASE 4: Advanced Features (Future) 🔮
**Goal**: Enhance system capabilities

### 4.1 Manual Data Input Forms
- [ ] Music preferences form for non-Spotify users
- [ ] Video preferences form for non-YouTube users
- [ ] Gaming preferences form for non-Steam users

### 4.2 Personality Evolution Visualization
- [ ] Interactive personality timeline
- [ ] Trait change graphs
- [ ] Personality stability indicators

### 4.3 Data Privacy Controls
- [ ] Service disconnection with data deletion
- [ ] Data export functionality
- [ ] Granular privacy settings

### 4.4 In-App RPG Games
- [ ] Memory Palace game
- [ ] Color Symphony game
- [ ] Puzzle Master game

---

## ESTIMATED TIMELINE 📅

### Sprint 1 (Week 1-2): Backend Foundation
- Phase 1.1: Supabase Schema ✅
- Phase 1.2: External API Integration ✅
- Phase 1.3: Background Job Scheduler ✅

### Sprint 2 (Week 3-4): Intelligence & Frontend
- Phase 1.4: Personality Evolution Engine ✅
- Phase 1.5: Data Collection Status API ✅
- Phase 2.1: Entertainment Hub Connections ✅

### Sprint 3 (Week 5-6): Chat & Testing
- Phase 2.2: Data Collection Status Display ✅
- Phase 2.3: Chat Integration ✅
- Phase 3.1: Testing Infrastructure ✅

### Sprint 4 (Week 7-8): Polish & Launch
- Phase 3.2: Monitoring & Logging ✅
- Final testing and bug fixes ✅
- Production deployment ✅

---

## TECHNOLOGY DECISIONS NEEDED ⚠️

### 1. Background Job Scheduler
**Options**:
- **Celery + Redis**: More scalable, production-ready, requires infrastructure
- **APScheduler**: Simpler, good for MVP, in-process, easier to deploy

**Recommendation**: Start with **APScheduler** for MVP, migrate to Celery later if needed

### 2. Chat History Storage
**Options**:
- **Supabase PostgreSQL**: Consistent with rest of system, easy to query
- **Separate service**: Better for high-volume chat logs

**Recommendation**: Use **Supabase PostgreSQL** for MVP

### 3. Personality Update Strategy
**Options**:
- **Weighted Average**: Balance old and new data
- **Decay Function**: Give more weight to recent data
- **Threshold-based**: Only update if confidence is high

**Recommendation**: Start with **Weighted Average** with confidence weighting

---

## NEXT IMMEDIATE ACTIONS 🎯

1. **Review and approve this roadmap**
2. **Create Supabase schema for entertainment data** (Task 1.1)
3. **Set up one external API integration** (Spotify recommended - Task 1.2)
4. **Implement basic background scheduler** (APScheduler - Task 1.3)
5. **Test end-to-end data collection flow**

---

## SUCCESS METRICS 📊

### Technical Metrics:
- ✅ 95%+ uptime for background jobs
- ✅ <2s response time for chat API
- ✅ <5min data collection time per user
- ✅ 100% data isolation (no cross-user data)

### User Metrics:
- ✅ 70%+ users connect at least one service
- ✅ 50%+ users connect all three services
- ✅ <10s time to connect a service
- ✅ 90%+ personality evolution accuracy

---

**Ready to start? Let's begin with Phase 1.1: Supabase Schema! 🚀**
