# 🎯 QUICK START - Day 1 Implementation

**Date:** October 2, 2025  
**Goal:** Get Redis + Celery running in 2 hours  
**Status:** Ready to implement

---

## ⚡ Step-by-Step Installation (30 minutes)

### 1. Install Backend Dependencies (5 min)
```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
pip install -r requirements-redis-celery.txt
```

### 2. Install Frontend Dependencies (2 min)
```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-landing"
npm install @upstash/redis
```

### 3. Set Up Upstash Redis (10 min)
1. Go to https://upstash.com/
2. Sign up (free, use GitHub OAuth)
3. Create database:
   - Name: `bondhu-production`
   - Region: Choose closest to you
   - Type: Regional (free tier)
4. Copy credentials:
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN`

### 4. Update Environment Variables (5 min)

**Backend (.env):**
```bash
# Add to bondhu-ai/.env

# Redis Connection
REDIS_URL=redis://default:[YOUR_PASSWORD]@[YOUR_ENDPOINT]:6379

# Upstash (for REST API)
UPSTASH_REDIS_REST_URL=https://[YOUR_ENDPOINT].upstash.io
UPSTASH_REDIS_REST_TOKEN=[YOUR_TOKEN]
```

**Frontend (.env.local):**
```bash
# Add to bondhu-landing/.env.local

# Upstash Redis
UPSTASH_REDIS_REST_URL=https://[YOUR_ENDPOINT].upstash.io
UPSTASH_REDIS_REST_TOKEN=[YOUR_TOKEN]
```

### 5. Update Config File (5 min)

Edit `bondhu-ai/core/config/settings.py`:

```python
# Add after other imports
import os

class Settings(BaseSettings):
    # ... existing settings ...
    
    # Redis Configuration
    redis_url: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
    upstash_redis_url: str = os.getenv('UPSTASH_REDIS_REST_URL', '')
    upstash_redis_token: str = os.getenv('UPSTASH_REDIS_REST_TOKEN', '')
```

---

## ✅ Test Installation (10 minutes)

### Test 1: Redis Connection (Backend)
```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
python -c "from core.cache.redis_client import get_redis; r = get_redis(); r.set('test', 'works'); print('Redis OK:', r.get('test'))"
```

**Expected output:** `Redis OK: works`

### Test 2: Celery Worker Start
```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
celery -A core.celery_app worker --loglevel=info --pool=solo
```

**Expected output:**
```
-------------- celery@YOUR_PC v5.3.4
...
[tasks]
  . core.tasks.personality.analyze_chat_sentiment_batch
...
celery@YOUR_PC ready.
```

Press `Ctrl+C` to stop (for now)

### Test 3: Frontend Redis (after npm run dev)
```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-landing"
npm run dev
```

Check browser console - no Redis errors should appear.

---

## 🚀 Start Everything (Development Mode)

Open **4 PowerShell terminals:**

### Terminal 1: Backend API
```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
python main.py
```

### Terminal 2: Celery Worker
```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
celery -A core.celery_app worker --loglevel=info --pool=solo
```

### Terminal 3: Frontend
```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-landing"
npm run dev
```

### Terminal 4: Celery Flower (Optional - Monitoring)
```powershell
cd "C:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
celery -A core.celery_app flower --port=5555
```

Then open: http://localhost:5555

---

## 🎯 Files Created

You now have these new files:

**Backend:**
- ✅ `core/cache/redis_client.py` - Redis connection & helpers
- ✅ `core/cache/__init__.py` - Cache module exports
- ✅ `core/celery_app.py` - Celery configuration
- ✅ `core/tasks/personality.py` - Sentiment analysis tasks
- ✅ `requirements-redis-celery.txt` - Python dependencies

**Frontend:**
- ✅ `src/lib/cache/redis.ts` - Redis utilities for Next.js

**Documentation:**
- ✅ `LAUNCH_PLAN_OCT10.md` - Complete 8-day plan
- ✅ `SETUP_REDIS_CELERY.md` - Detailed setup guide
- ✅ `QUICKSTART_DAY1.md` - This file

---

## 🐛 Common Issues & Fixes

### Issue: "Cannot connect to Redis"
**Fix:**
1. Check Upstash dashboard - database is running
2. Verify `.env` has correct credentials
3. Try ping in Upstash console

### Issue: "Celery import error"
**Fix:**
```powershell
cd bondhu-ai
pip install --upgrade celery redis
```

### Issue: "Module 'core.tasks' not found"
**Fix:**
Check `core/tasks/__init__.py` exists (create if missing):
```python
# core/tasks/__init__.py
"""Background tasks module"""
```

---

## ✅ Verification Checklist

Before moving to Day 2:

- [ ] Redis ping works (test output says "works")
- [ ] Celery worker starts without errors
- [ ] Frontend dev server runs without Redis errors
- [ ] All 4 terminals can run simultaneously
- [ ] Flower dashboard accessible (optional)

---

## 📅 Next Steps (Day 2 - Tomorrow)

**Day 2 Tasks: Chat Persistence & Caching**
1. Create `chat_messages` table in Supabase
2. Implement chat history loading
3. Add personality context caching
4. Test message persistence across reloads

**Estimated Time:** 6-8 hours

---

## 🎉 Success!

If all tests passed, you're ready to move on!

**Current Status:**
- ✅ Infrastructure ready
- ✅ Redis connected
- ✅ Celery workers ready
- ⏳ Ready for Day 2 implementation

---

**Questions or issues?** Check the detailed guide in `SETUP_REDIS_CELERY.md`

**Want to start Day 2 now?** Let me know and I'll create the chat persistence implementation!
