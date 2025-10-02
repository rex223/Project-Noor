# 📋 Redis & Celery - Complete Setup Checklist

**Time:** 30 minutes  
**Difficulty:** Easy  
**Prerequisites:** Python 3.10+, Node.js 18+, Git

---

## ✅ Pre-Installation Checklist

- [ ] Python 3.10+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Git installed and Project Noor cloned
- [ ] Backend `.env` file exists
- [ ] Frontend `.env.local` file exists
- [ ] Supabase account active

---

## 📦 Step 1: Install Dependencies (5 min)

### Backend (Python)
```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
pip install -r requirements-redis-celery.txt
```

**Expected Output:**
```
Successfully installed redis-5.0.1 hiredis-2.3.2 celery-5.3.4 ...
```

- [ ] Redis installed
- [ ] Celery installed
- [ ] No error messages

---

### Frontend (Node.js)
```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-landing"
npm install @upstash/redis
```

**Expected Output:**
```
added 1 package, and audited XXX packages in Xs
```

- [ ] @upstash/redis installed
- [ ] No vulnerabilities

---

## 🔴 Step 2: Set Up Upstash Redis (10 min)

### 2.1 Create Account
1. Go to **https://upstash.com/**
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"** (or Google)
4. Verify email if prompted

- [ ] Account created
- [ ] Email verified
- [ ] Logged into dashboard

---

### 2.2 Create Redis Database
1. Click **"Create Database"** button
2. Fill in details:
   - **Name:** `bondhu-production`
   - **Type:** Regional (FREE)
   - **Region:** Choose closest to your users
   - **Primary Region:** (auto-selected)
   - **Read Region:** None
   - **Eviction:** noeviction
   - **TLS:** Enabled
3. Click **"Create"**

- [ ] Database created
- [ ] Status shows "Active"

---

### 2.3 Copy Credentials
1. Click on your **`bondhu-production`** database
2. Scroll to **"REST API"** section
3. Copy these values:

**Copy These:**
```
UPSTASH_REDIS_REST_URL=https://XXXXX.upstash.io
UPSTASH_REDIS_REST_TOKEN=XXXXXXXXXX
```

4. Scroll to **"Connection"** section (for Python)
5. Copy the **"Redis Connection String"**:

**Copy This:**
```
REDIS_URL=redis://default:XXXXXX@XXXXX.upstash.io:6379
```

- [ ] REST URL copied
- [ ] REST Token copied
- [ ] Connection string copied

---

## ⚙️ Step 3: Update Environment Variables (5 min)

### 3.1 Backend (.env)

**File:** `bondhu-ai/.env`

**Add these lines at the bottom:**
```bash
# ==========================================
# Redis & Celery Configuration
# ==========================================

# Redis Connection (from Upstash)
REDIS_URL=redis://default:YOUR_PASSWORD@YOUR_ENDPOINT.upstash.io:6379

# Upstash REST API (from Upstash)
UPSTASH_REDIS_REST_URL=https://YOUR_ENDPOINT.upstash.io
UPSTASH_REDIS_REST_TOKEN=YOUR_TOKEN_HERE

# Celery (uses same Redis)
CELERY_BROKER_URL=redis://default:YOUR_PASSWORD@YOUR_ENDPOINT.upstash.io:6379
CELERY_RESULT_BACKEND=redis://default:YOUR_PASSWORD@YOUR_ENDPOINT.upstash.io:6379
```

**Replace:**
- `YOUR_PASSWORD` → Your actual password
- `YOUR_ENDPOINT` → Your actual endpoint
- `YOUR_TOKEN_HERE` → Your actual token

- [ ] REDIS_URL added
- [ ] UPSTASH_REDIS_REST_URL added
- [ ] UPSTASH_REDIS_REST_TOKEN added
- [ ] CELERY_BROKER_URL added
- [ ] CELERY_RESULT_BACKEND added
- [ ] File saved

---

### 3.2 Frontend (.env.local)

**File:** `bondhu-landing/.env.local`

**Add these lines:**
```bash
# ==========================================
# Redis Configuration (Upstash)
# ==========================================

UPSTASH_REDIS_REST_URL=https://YOUR_ENDPOINT.upstash.io
UPSTASH_REDIS_REST_TOKEN=YOUR_TOKEN_HERE
```

**Replace:**
- `YOUR_ENDPOINT` → Your actual endpoint
- `YOUR_TOKEN_HERE` → Your actual token

- [ ] UPSTASH_REDIS_REST_URL added
- [ ] UPSTASH_REDIS_REST_TOKEN added
- [ ] File saved

---

## ✅ Step 4: Test Installation (5 min)

### Test 1: Redis Connection (Backend)

```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
python -c "from core.cache.redis_client import get_redis; r = get_redis(); r.set('test', 'works'); print('✅ Redis OK:', r.get('test'))"
```

**Expected Output:**
```
✅ Redis OK: works
```

**If you see errors:**
- Check `.env` has correct values
- Verify Upstash database is "Active"
- Try ping in Upstash console

- [ ] Test passed
- [ ] Output shows "works"

---

### Test 2: Celery Worker Start

```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
celery -A core.celery_app worker --loglevel=info --pool=solo
```

**Expected Output:**
```
-------------- celery@YOUR_PC v5.3.4 (emerald-rush)
--- ***** ----- 
-- ******* ---- Windows-10-10.0.XXXXX
...
[tasks]
  . core.tasks.personality.analyze_chat_sentiment_batch
  . core.tasks.personality.analyze_all_users_sentiment
  . core.tasks.personality.update_personality_from_activity

[2025-10-02 XX:XX:XX,XXX: INFO/MainProcess] Connected to redis://...
[2025-10-02 XX:XX:XX,XXX: INFO/MainProcess] celery@YOUR_PC ready.
```

**Look for:**
- ✅ "celery@YOUR_PC ready"
- ✅ "Connected to redis"
- ✅ Tasks listed

**Press Ctrl+C to stop**

- [ ] Worker started
- [ ] No import errors
- [ ] Tasks registered

---

### Test 3: Celery Task Registration

```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
celery -A core.celery_app inspect registered
```

**Expected Output:**
```
-> celery@YOUR_PC: OK
    * core.tasks.personality.analyze_all_users_sentiment
    * core.tasks.personality.analyze_chat_sentiment_batch
    * core.tasks.personality.update_personality_from_activity
```

- [ ] All 3 tasks listed
- [ ] No errors

---

## 🚀 Step 5: Start Development Environment (5 min)

### Open 3 PowerShell Terminals

**Terminal 1: Backend API**
```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
python main.py
```

**Expected:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Uvicorn running on http://localhost:8000
```

- [ ] Server started
- [ ] No errors
- [ ] Port 8000 active

---

**Terminal 2: Celery Worker**
```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
celery -A core.celery_app worker --loglevel=info --pool=solo
```

**Expected:**
```
celery@YOUR_PC ready.
```

- [ ] Worker running
- [ ] Connected to Redis
- [ ] Tasks registered

---

**Terminal 3: Frontend**
```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-landing"
npm run dev
```

**Expected:**
```
  ▲ Next.js 15.5.3
  - Local:        http://localhost:3000
  ✓ Ready in XXXms
```

- [ ] Server started
- [ ] No errors
- [ ] Port 3000 active

---

### Test 4: Frontend Redis (Browser)

1. Open **http://localhost:3000**
2. Open **DevTools** (F12)
3. Go to **Console** tab
4. Look for errors

**Should NOT see:**
- ❌ Redis connection errors
- ❌ Environment variable warnings

- [ ] No Redis errors in console
- [ ] Page loads successfully

---

## 🎉 Final Verification

### All Systems Check

Run this command in a **4th terminal**:
```powershell
# Check backend
curl http://localhost:8000

# Check frontend
curl http://localhost:3000
```

**Expected:**
- Backend: JSON response or "Not Found" (OK)
- Frontend: HTML content (OK)

- [ ] Backend responding
- [ ] Frontend responding
- [ ] All 3 terminals running
- [ ] No errors in any terminal

---

## 📊 System Status Dashboard

### Terminal Overview:
```
┌─────────────────────────────────────────────────┐
│ Terminal 1: Backend API                         │
│ Status: ✅ Running on http://localhost:8000     │
│ Logs: INFO level                                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Terminal 2: Celery Worker                       │
│ Status: ✅ Ready, 3 tasks registered            │
│ Logs: INFO level                                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Terminal 3: Frontend Dev Server                 │
│ Status: ✅ Running on http://localhost:3000     │
│ Logs: Next.js output                            │
└─────────────────────────────────────────────────┘
```

- [ ] All 3 terminals active
- [ ] All services connected
- [ ] Ready for development

---

## 🎯 What You've Accomplished

### Infrastructure:
- ✅ Redis cache connected (Upstash)
- ✅ Celery task queue configured
- ✅ Background workers running
- ✅ Frontend cache client ready

### Files Created:
- ✅ `core/cache/redis_client.py` (Backend Redis)
- ✅ `core/celery_app.py` (Celery config)
- ✅ `core/tasks/personality.py` (Sentiment tasks)
- ✅ `src/lib/cache/redis.ts` (Frontend Redis)

### Configuration:
- ✅ Environment variables set
- ✅ Redis credentials configured
- ✅ Celery broker connected

### Tests:
- ✅ Redis connection verified
- ✅ Celery worker starts
- ✅ Tasks registered
- ✅ All services running

---

## 🚦 Next Steps

### You Are Here: Day 1 ✅
- [x] Redis & Celery setup

### Tomorrow: Day 2 🔄
- [ ] Chat message persistence
- [ ] Load messages from database
- [ ] Cache chat history
- [ ] Test reload persistence

### This Week: Days 3-8 🚀
- [ ] Music integration (Spotify + YouTube)
- [ ] Video integration (YouTube)
- [ ] Personality learning from chat
- [ ] Testing & deployment

---

## 🐛 Troubleshooting Quick Reference

### "Cannot connect to Redis"
```powershell
# Test manually
python -c "from core.cache.redis_client import get_redis; print(get_redis().ping())"
```

### "Celery worker won't start"
```powershell
# Check imports
celery -A core.celery_app inspect registered
```

### "Frontend Redis errors"
- Restart Next.js dev server
- Clear browser cache
- Check `.env.local` values

---

## 📚 Documentation

- **Quick Start:** `QUICKSTART_DAY1.md` (you are here!)
- **Complete Plan:** `LAUNCH_PLAN_OCT10.md`
- **Setup Guide:** `SETUP_REDIS_CELERY.md`
- **Summary:** `IMPLEMENTATION_SUMMARY.md`

---

## ✅ Completion Checklist

### Installation Phase:
- [ ] All dependencies installed
- [ ] Upstash account created
- [ ] Redis database active
- [ ] Environment variables set

### Testing Phase:
- [ ] Redis connection test passed
- [ ] Celery worker starts
- [ ] Tasks registered
- [ ] Frontend runs without errors

### Running Phase:
- [ ] Backend API running
- [ ] Celery worker running
- [ ] Frontend dev server running
- [ ] All terminals stable

### Verification Phase:
- [ ] Can access http://localhost:8000
- [ ] Can access http://localhost:3000
- [ ] No errors in any console
- [ ] Redis ping successful

---

## 🎉 SUCCESS!

If all checkboxes are checked, you're ready for Day 2!

**Current Status:**
- ✅ Infrastructure: Complete
- ✅ Configuration: Complete
- ✅ Testing: Complete
- 🎯 Ready for: Chat Persistence Implementation

---

**Congratulations! You've completed Day 1 setup! 🚀**

Ready to start Day 2? Let me know and I'll create the chat persistence implementation!
