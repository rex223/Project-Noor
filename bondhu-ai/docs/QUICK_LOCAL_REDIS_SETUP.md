# 🚀 5-Minute Setup: Local Redis with Docker

## The Problem
- Celery sends **126,720 commands/day** to Redis
- Upstash free tier: **10,000 commands/day**
- You're using **12.6x the free tier limit**

## The Solution
Local Redis with Docker = **Unlimited commands, $0 cost, zero maintenance**

---

## Setup (5 Minutes Total)

### Step 1: Start Redis Container (2 minutes)

Open PowerShell and run:

```powershell
docker run -d `
  --name bondhu-redis `
  -p 6379:6379 `
  --restart always `
  redis:alpine
```

**What this does:**
- Downloads Redis (~5MB)
- Starts it in the background
- Maps port 6379
- Auto-restarts if it crashes or computer reboots

**Verify it's running:**
```powershell
docker ps
```

You should see:
```
CONTAINER ID   IMAGE          STATUS          PORTS                    NAMES
abc123def456   redis:alpine   Up 10 seconds   0.0.0.0:6379->6379/tcp   bondhu-redis
```

✅ **Done! Redis is now running.**

---

### Step 2: Update .env File (2 minutes)

Open `.env` in `bondhu-ai` folder and change these 3 lines:

**BEFORE:**
```bash
REDIS_URL=rediss://default:AUI8AAIncDI1MmJhMjA1YzU3OTk0M2ZkYWI2YjhiZWFmM2MyM2QxMnAyMTY5NTY@romantic-terrapin-16956.upstash.io:6379
CELERY_BROKER_URL=rediss://default:AUI8AAIncDI1MmJhMjA1YzU3OTk0M2ZkYWI2YjhiZWFmM2MyM2QxMnAyMTY5NTY@romantic-terrapin-16956.upstash.io:6379?ssl_cert_reqs=CERT_NONE
CELERY_RESULT_BACKEND=rediss://default:AUI8AAIncDI1MmJhMjA1YzU3OTk0M2ZkYWI2YjhiZWFmM2MyM2QxMnAyMTY5NTY@romantic-terrapin-16956.upstash.io:6379?ssl_cert_reqs=CERT_NONE
```

**AFTER:**
```bash
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
```

**Optional:** Comment out the Upstash lines (keep them for production):
```bash
# Production Redis (Upstash) - use when deploying
# REDIS_URL=rediss://default:TOKEN@romantic-terrapin-16956.upstash.io:6379
# CELERY_BROKER_URL=rediss://default:TOKEN@romantic-terrapin-16956.upstash.io:6379?ssl_cert_reqs=CERT_NONE
# CELERY_RESULT_BACKEND=rediss://default:TOKEN@romantic-terrapin-16956.upstash.io:6379?ssl_cert_reqs=CERT_NONE

# Development Redis (Local)
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
```

✅ **Done! Config updated.**

---

### Step 3: Test Connection (1 minute)

```powershell
cd "c:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
.\.venv\Scripts\Activate.ps1

# Test Redis connection
python -c "from core.cache.redis_client import get_redis; r = get_redis(); r.set('test', 'local_works'); print('✅ Local Redis:', r.get('test'))"
```

**Expected output:**
```
✅ Local Redis: local_works
```

✅ **Done! Redis is working.**

---

### Step 4: Start Celery (1 minute)

```powershell
# Should still be in bondhu-ai directory with venv active
celery -A core.celery_app worker --loglevel=info --pool=solo
```

**Expected output:**
```
-------------- celery@LAPTOP-RVNG7NQ4 v5.3.4
.> transport:   redis://localhost:6379//
.> results:     redis://localhost:6379/
[tasks]
  . core.celery_app.debug_task
  . core.tasks.personality.analyze_all_users_sentiment
  . core.tasks.personality.analyze_chat_sentiment_batch
  . core.tasks.personality.update_personality_from_activity

celery@LAPTOP-RVNG7NQ4 ready.
```

✅ **Done! Celery is using local Redis with unlimited commands!**

---

## Verify Unlimited Commands

Run the monitor script again:

```powershell
# In a new terminal (keep Celery running)
cd "c:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
.\.venv\Scripts\Activate.ps1
python monitor_redis.py
```

**You'll see the same ~88 commands/minute, but now:**
- ✅ No quota limit
- ✅ No cost
- ✅ No stress

---

## That's It! 🎉

**Total time:** 5 minutes  
**Cost:** $0  
**Maintenance:** None (Docker auto-restarts Redis)

**What you get:**
- ✅ Unlimited Redis commands
- ✅ Celery runs 24/7 without issues
- ✅ Faster (< 1ms latency vs 50ms Upstash)
- ✅ Works offline
- ✅ Zero monitoring needed

---

## Common Questions

### Q: What if I restart my computer?
**A:** Redis auto-starts with Docker (because of `--restart always`)

### Q: What if Redis crashes?
**A:** Docker auto-restarts it (because of `--restart always`)

### Q: How do I stop Redis?
```powershell
docker stop bondhu-redis
```

### Q: How do I start Redis again?
```powershell
docker start bondhu-redis
```

### Q: How do I check if Redis is running?
```powershell
docker ps
```

### Q: How much RAM does it use?
**A:** ~20-50MB (negligible)

### Q: Do I need to update Redis?
**A:** No. But if you want to:
```powershell
docker pull redis:alpine
docker stop bondhu-redis
docker rm bondhu-redis
docker run -d --name bondhu-redis -p 6379:6379 --restart always redis:alpine
```

### Q: How do I see Redis logs?
```powershell
docker logs bondhu-redis
```

### Q: Can I use this for production?
**A:** For development, yes. For production, use Upstash paid tier or Railway/Redis Labs.

### Q: What if port 6379 is already in use?
```powershell
# Use a different port (e.g., 6380)
docker run -d --name bondhu-redis -p 6380:6379 --restart always redis:alpine

# Update .env
REDIS_URL=redis://localhost:6380
CELERY_BROKER_URL=redis://localhost:6380
CELERY_RESULT_BACKEND=redis://localhost:6380
```

---

## Maintenance Checklist

### Daily
- ❌ Nothing

### Weekly  
- ❌ Nothing

### Monthly
- ❌ Nothing

### Yearly
- ❌ Nothing

**Seriously, you never need to touch it again.** 🎉

---

## Switching Back to Upstash (For Production)

When you're ready to deploy:

1. Update `.env` to use Upstash URLs (uncomment the lines)
2. Upgrade Upstash to paid tier ($10/month)
3. Deploy

**That's it!** Same code works with both local and Upstash Redis.

---

## Summary

**Before:** 
- 126,720 commands/day to Upstash
- 10,000 command/day limit
- Constantly hitting quota
- Stress

**After:**
- Unlimited commands to local Redis
- $0 cost
- Zero maintenance
- Peace of mind

**Time to set up:** 5 minutes  
**Problem:** Solved forever ✅

---

## Ready? Let's Do This!

```powershell
# Copy and paste these commands:

# 1. Start Redis
docker run -d --name bondhu-redis -p 6379:6379 --restart always redis:alpine

# 2. Open .env file
cd "c:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
notepad .env
# Change the 3 REDIS_URL lines to: redis://localhost:6379

# 3. Test
.\.venv\Scripts\Activate.ps1
python -c "from core.cache.redis_client import get_redis; r = get_redis(); r.set('test', 'works'); print('✅', r.get('test'))"

# 4. Start Celery
celery -A core.celery_app worker --loglevel=info --pool=solo
```

**That's all!** Problem solved. 🚀
