# 🚀 Redis & Celery Setup Guide

**Time Required:** 30 minutes  
**Difficulty:** Easy

---

## 📋 Prerequisites

- Python 3.10+ installed
- Node.js 18+ installed
- Supabase account
- Git installed

---

## 🔴 Step 1: Set Up Upstash Redis (10 minutes)

### 1.1 Create Upstash Account
1. Go to https://upstash.com/
2. Sign up with GitHub/Google (free)
3. Verify email

### 1.2 Create Redis Database
1. Click "Create Database"
2. Choose these settings:
   - **Name:** bondhu-production
   - **Type:** Regional (free tier)
   - **Region:** Choose closest to your users
   - **Eviction:** noeviction
3. Click "Create"

### 1.3 Get Connection Details
1. Click on your database
2. Copy these values:
   - **UPSTASH_REDIS_REST_URL**
   - **UPSTASH_REDIS_REST_TOKEN**
   - **Redis Connection String** (for Python)

### 1.4 Test Connection
```bash
# Test using curl
curl -H "Authorization: Bearer YOUR_TOKEN" https://YOUR_URL/get/test
```

---

## ⚙️ Step 2: Backend Setup (Python/FastAPI)

### 2.1 Install Dependencies
```bash
cd bondhu-ai
pip install -r requirements-redis-celery.txt
```

### 2.2 Update .env File
```bash
# Add to bondhu-ai/.env

# Redis (from Upstash)
REDIS_URL=redis://default:YOUR_PASSWORD@YOUR_ENDPOINT:6379
UPSTASH_REDIS_REST_URL=https://YOUR_ENDPOINT.upstash.io
UPSTASH_REDIS_REST_TOKEN=YOUR_TOKEN

# Celery
CELERY_BROKER_URL=redis://default:YOUR_PASSWORD@YOUR_ENDPOINT:6379
CELERY_RESULT_BACKEND=redis://default:YOUR_PASSWORD@YOUR_ENDPOINT:6379
```

### 2.3 Create Redis Client
```bash
# File already created: core/cache/redis_client.py
# Just verify it exists
```

### 2.4 Create Celery App
```bash
# File already created: core/celery_app.py
# Just verify it exists
```

### 2.5 Test Redis Connection
```bash
cd bondhu-ai
python -c "from core.cache.redis_client import get_redis; r = get_redis(); r.set('test', 'works'); print(r.get('test'))"
```

Expected output: `works`

---

## 🎯 Step 3: Frontend Setup (Next.js)

### 3.1 Install Dependencies
```bash
cd bondhu-landing
npm install @upstash/redis
```

### 3.2 Update .env.local
```bash
# Add to bondhu-landing/.env.local

# Redis (from Upstash)
UPSTASH_REDIS_REST_URL=https://YOUR_ENDPOINT.upstash.io
UPSTASH_REDIS_REST_TOKEN=YOUR_TOKEN
```

### 3.3 Create Redis Utility
```bash
# File: src/lib/cache/redis.ts (will create next)
```

---

## 🔄 Step 4: Start Celery Worker

### 4.1 Start Worker (Development)
```bash
cd bondhu-ai

# Windows (PowerShell)
celery -A core.celery_app worker --loglevel=info --pool=solo

# macOS/Linux
celery -A core.celery_app worker --loglevel=info
```

### 4.2 Verify Worker is Running
You should see:
```
-------------- celery@YOUR_MACHINE v5.3.4 (emerald-rush)
--- ***** ----- 
-- ******* ---- Windows-10-10.0.19045-SP0 2025-10-02 12:00:00
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         bondhu:0x...
- ** ---------- .> transport:   redis://...
- ** ---------- .> results:     redis://...
- *** --- * --- .> concurrency: 4 (solo)
-- ******* ---- .> task events: OFF
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery
                

[tasks]
  . core.tasks.music.fetch_spotify_preferences
  . core.tasks.personality.analyze_chat_sentiment_batch

[2025-10-02 12:00:00,000: INFO/MainProcess] Connected to redis://...
[2025-10-02 12:00:00,000: INFO/MainProcess] celery@YOUR_MACHINE ready.
```

### 4.3 Test Celery Task
```python
# In Python shell or test script
from core.tasks.personality import analyze_chat_sentiment_batch

# Trigger task
task = analyze_chat_sentiment_batch.delay('test-user-id')
print(f"Task ID: {task.id}")
print(f"Task Status: {task.status}")
```

---

## 🎨 Step 5: Optional - Flower (Celery Monitoring)

### 5.1 Start Flower
```bash
cd bondhu-ai
celery -A core.celery_app flower --port=5555
```

### 5.2 Access Dashboard
Open browser: http://localhost:5555

You'll see:
- Active workers
- Task history
- Task success/failure rates
- Real-time monitoring

---

## ✅ Step 6: Verify Everything Works

### 6.1 Check Redis
```bash
# Backend
cd bondhu-ai
python -c "from core.cache.redis_client import get_redis; r = get_redis(); print('Redis OK' if r.ping() else 'Redis FAIL')"
```

### 6.2 Check Celery
```bash
# Backend
cd bondhu-ai
celery -A core.celery_app inspect active
```

Should show: `-> celery@YOUR_MACHINE: OK`

### 6.3 Check Frontend Redis
```bash
# Frontend
cd bondhu-landing
npm run dev

# Then in browser console:
# Go to http://localhost:3000
# Open DevTools > Console
# The app should connect without errors
```

---

## 🐛 Troubleshooting

### Issue: "Redis connection refused"
**Solution:**
1. Check if Upstash Redis URL is correct
2. Verify token is not expired
3. Check firewall settings

### Issue: "Celery worker won't start"
**Solution:**
1. Make sure Redis is accessible
2. On Windows, use `--pool=solo`
3. Check Python version (3.10+)

### Issue: "Module not found: celery_app"
**Solution:**
1. Make sure you're in `bondhu-ai` directory
2. Run `pip install -r requirements-redis-celery.txt`
3. Check `core/__init__.py` exists

### Issue: "Frontend Redis connection fails"
**Solution:**
1. Check `.env.local` has correct values
2. Restart Next.js dev server
3. Clear browser cache

---

## 🚀 Production Deployment

### Backend (Railway/Render)
```yaml
# railway.toml or render.yaml
services:
  - type: web
    name: bondhu-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: REDIS_URL
        sync: false
      - key: CELERY_BROKER_URL
        sync: false

  - type: worker
    name: celery-worker
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: celery -A core.celery_app worker --loglevel=info
    envVars:
      - key: REDIS_URL
        sync: false
```

### Frontend (Vercel)
```bash
# Vercel will auto-detect Next.js
# Just add environment variables in Vercel dashboard:
# - UPSTASH_REDIS_REST_URL
# - UPSTASH_REDIS_REST_TOKEN
```

---

## 📊 Performance Expectations

### Before Redis/Celery:
- Chat response: 1-2 seconds
- Personality context: 500ms-2s per message
- Music fetch: Blocks UI for 3-5 seconds

### After Redis/Celery:
- Chat response: 300-500ms (cached personality)
- Personality context: 50-100ms (Redis cache)
- Music fetch: 0ms UI blocking (background task)

---

## 🎯 Next Steps

After setup is complete:

1. ✅ Implement chat persistence (Day 2 task)
2. ✅ Add personality caching (Day 2 task)
3. ✅ Build music integration (Days 3-4)
4. ✅ Build video integration (Day 5)
5. ✅ Implement personality learning (Day 6)

---

## 📝 Quick Reference

### Start Development Environment
```bash
# Terminal 1: Backend
cd bondhu-ai
python main.py

# Terminal 2: Celery Worker
cd bondhu-ai
celery -A core.celery_app worker --loglevel=info --pool=solo

# Terminal 3: Frontend
cd bondhu-landing
npm run dev

# Terminal 4 (Optional): Flower
cd bondhu-ai
celery -A core.celery_app flower --port=5555
```

### Redis CLI Commands (via Upstash Console)
```redis
# Check all keys
KEYS *

# Get value
GET personality:context:user-123

# Set value with TTL
SETEX test:key 60 "expires in 60 seconds"

# Delete key
DEL test:key

# Check TTL
TTL personality:context:user-123
```

---

## ✅ Checklist

Before moving to implementation:

- [ ] Upstash Redis created and tested
- [ ] Backend `.env` updated with Redis URL
- [ ] Frontend `.env.local` updated with Upstash tokens
- [ ] Python packages installed (`requirements-redis-celery.txt`)
- [ ] NPM package installed (`@upstash/redis`)
- [ ] Celery worker starts without errors
- [ ] Redis connection test passes
- [ ] Flower dashboard accessible (optional)

---

**Setup Complete!** 🎉

Now you're ready to implement the features in the 8-day plan.

**Next:** Start with Day 2 - Chat Persistence & Caching
