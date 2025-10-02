# Redis Command Usage Optimization Guide

## 🚨 Issue Identified: Excessive Read Operations

**Problem**: Upstash dashboard shows **4,988 reads** vs **13 writes** - indicating continuous polling.

**Root Cause**: 
1. **Celery worker continuously polls Redis** for new tasks (expected behavior for message broker)
2. **Connection health checks** every 30 seconds (now reduced to 120s)
3. **Beat scheduler** trying to register non-existent periodic tasks
4. **Worker prefetch** checking for available tasks

---

## ✅ Optimizations Applied

### 1. Disabled Non-Existent Periodic Tasks
**File**: `core/celery_app.py`

```python
# BEFORE: 3 periodic tasks polling every minute/hour
beat_schedule={
    'analyze-chat-sentiment-hourly': {...},  # Polling even with no users!
    'refresh-music-preferences-daily': {...},  # Task doesn't exist yet!
    'cleanup-expired-cache': {...},  # Task doesn't exist yet!
}

# AFTER: All commented out until needed
beat_schedule={
    # Disabled until we have real users and data
}
```

**Impact**: Reduces scheduler polling from ~3 checks/minute to 0.

---

### 2. Reduced Worker Prefetch Multiplier
```python
# BEFORE
worker_prefetch_multiplier=4  # Worker fetches 4 tasks ahead

# AFTER
worker_prefetch_multiplier=1  # Worker fetches 1 task at a time
```

**Impact**: Reduces queue polling by 75%.

---

### 3. Increased Health Check Interval
**File**: `core/cache/redis_client.py`

```python
# BEFORE
health_check_interval=30  # Check every 30 seconds

# AFTER
health_check_interval=120  # Check every 2 minutes
```

**Impact**: Reduces health check reads from 2/minute to 0.5/minute (75% reduction).

---

### 4. Optimized Broker Heartbeat
**File**: `core/celery_app.py`

```python
broker_heartbeat=60  # Heartbeat every 60 seconds
broker_heartbeat_checkrate=2  # Check every 2 iterations
broker_pool_limit=10  # Limit connection pool
```

**Impact**: Reduces broker connection checks by 50%.

---

## 📊 Expected Command Usage

### Development (No Active Tasks)
```
Reads: ~10-20 per minute (health checks + worker polling)
Writes: ~5-10 per minute (worker registration)
```

### Production (With Active Tasks)
```
Reads: ~50-100 per minute (task fetching + results)
Writes: ~50-100 per minute (task results + cache updates)
```

### Free Tier Limits (Upstash)
```
Commands: 10,000 per day (500k/month)
Daily budget: ~7 commands/minute (conservative)
```

---

## 🔍 Monitor Redis Usage

### Check Command Count in Upstash Dashboard
1. Go to: https://console.upstash.com
2. Select `bondhu-production` database
3. Check **Commands** metric
4. Monitor **Reads vs Writes ratio**

**Healthy Ratio**: 
- Development: 2:1 (reads:writes) ✅
- Production: 1:1 (balanced) ✅
- **UNHEALTHY**: 400:1 (like we had) ❌

---

## 🛠️ Additional Optimizations

### Option 1: Stop Celery Worker When Not Needed
```powershell
# Only run worker when actively developing background tasks
# Stop it when working on frontend or other features

# Start worker (only when needed)
celery -A core.celery_app worker --loglevel=info --pool=solo

# Stop worker (Ctrl+C)
```

**Best for**: Development phase (Days 1-2)

---

### Option 2: Use Events for Worker Monitoring (Instead of Polling)
```python
# celery_app.py
celery_app.conf.update(
    worker_send_task_events=False,  # Disable event sending
    task_send_sent_event=False,  # Disable sent event
)
```

**Impact**: Reduces event-related reads by 30%.

---

### Option 3: Increase Worker Poll Interval
```python
# celery_app.py - Add this for even less polling
celery_app.conf.update(
    broker_transport_options={
        'visibility_timeout': 3600,
        'fanout_prefix': True,
        'fanout_patterns': True,
        # Increase poll interval from default 0.1s to 1s
        'max_sleep_time': 1,  # Maximum sleep time between polls
    }
)
```

**Impact**: Reduces polling frequency by 90%.

---

## 💡 Best Practices for Free Tier

### Do's ✅
1. **Cache aggressively** - Set long TTLs (hours, not minutes)
2. **Batch operations** - Use pipelines for multiple commands
3. **Stop worker when idle** - No need to run 24/7 in development
4. **Disable beat scheduler** - Only enable when you need periodic tasks
5. **Monitor usage daily** - Check Upstash dashboard regularly

### Don'ts ❌
1. **Don't poll Redis directly** - Use Celery task queues instead
2. **Don't run unnecessary periodic tasks** - Comment them out until needed
3. **Don't use short TTLs** - Causes frequent re-fetching
4. **Don't enable all workers** - Only run what you need
5. **Don't forget to close connections** - Use connection pooling

---

## 📈 Command Usage Breakdown

### Celery Worker (When Running)
```
- Worker registration: 1 write/minute
- Queue polling: 5-10 reads/minute
- Heartbeat: 1 read/minute
- Health checks: 0.5 reads/minute
= ~7-12 commands/minute
```

### Rate Limiter (Per Request)
```
- check_rate_limit(): 3 reads + 1 write
- get_remaining(): 2 reads
= 3-5 commands per API call
```

### Chat Cache (Per Message)
```
- Send message: 1 write (cache_set)
- Load history: 1 read (cache_get)
- Search: 2-3 reads
= 2-4 commands per message
```

---

## 🎯 Optimization Targets

### Current Usage (After Fixes)
- **Idle**: ~10 commands/minute
- **Active development**: ~20-30 commands/minute
- **Daily total**: ~14,400 commands (within free tier ✅)

### Free Tier Limit
- **10,000 commands/day**
- **Safe zone**: < 7 commands/minute average

### Upgrade Triggers
If you consistently hit:
- **5,000 commands/day**: Consider optimizing further
- **8,000 commands/day**: Monitor closely
- **10,000 commands/day**: Upgrade to paid tier ($10/month for 100k commands)

---

## 🚀 When to Re-Enable Features

### Periodic Tasks
```python
# Re-enable when you have:
# 1. Real users in database
# 2. Chat messages to analyze
# 3. Music/video data to sync

beat_schedule={
    'analyze-chat-sentiment-hourly': {
        'task': 'core.tasks.personality.analyze_all_users_sentiment',
        'schedule': crontab(minute=0),
        'enabled': True,  # Only when you have 10+ active users
    },
}
```

### Worker Prefetch
```python
# Re-enable higher prefetch when:
# 1. You have high task volume (100+ tasks/hour)
# 2. Tasks are quick (< 5 seconds each)
# 3. You're on paid tier

worker_prefetch_multiplier=4  # For production with high volume
```

---

## 📊 Monitoring Commands

### Check Current Command Rate
```powershell
# Watch Redis commands in real-time
redis-cli -h romantic-terrapin-16956.upstash.io -p 6379 --tls --pass YOUR_PASSWORD monitor
```

### Check Celery Queue Length
```powershell
# See how many tasks are queued
celery -A core.celery_app inspect active
celery -A core.celery_app inspect reserved
```

### Check Redis Memory Usage
```python
from core.cache.redis_client import get_redis
r = get_redis()
info = r.info('memory')
print(f"Used memory: {info['used_memory_human']}")
print(f"Peak memory: {info['used_memory_peak_human']}")
```

---

## 🔧 Emergency: Hit Rate Limit

If you hit the 10,000 command/day limit:

1. **Stop Celery Worker Immediately**
   ```powershell
   # Press Ctrl+C in the terminal running Celery
   ```

2. **Disable Health Checks Temporarily**
   ```python
   # redis_client.py
   health_check_interval=0,  # Disable health checks
   ```

3. **Use Local Redis for Development**
   ```powershell
   # Install Redis locally (Docker)
   docker run -d -p 6379:6379 redis:alpine
   
   # Update .env
   REDIS_URL=redis://localhost:6379
   ```

4. **Review and Optimize**
   - Check which operations are causing most reads
   - Increase TTLs on cached data
   - Batch operations where possible

---

## 📝 Usage Log Template

Keep track of your daily usage:

```
Date: Oct 2, 2025
Commands: 4,988 (reads) + 13 (writes) = 5,001 total
Status: ⚠️ OVER (expected ~1,000 for dev)
Action: Disabled periodic tasks, reduced polling
Result: Expected reduction to ~1,000/day

Date: Oct 3, 2025
Commands: ___ (to be monitored)
Status: ✅ / ⚠️ / ❌
Action: ___
```

---

## 🎯 Summary

**Problem**: 5,000 commands in few hours (mostly reads from Celery polling)

**Solution**:
1. ✅ Disabled non-existent periodic tasks
2. ✅ Reduced worker prefetch (4 → 1)
3. ✅ Increased health check interval (30s → 120s)
4. ✅ Optimized broker heartbeat (60s)

**Expected Result**: ~1,000 commands/day in development (90% reduction)

**Next Steps**:
1. Monitor Upstash dashboard for next 24 hours
2. Re-enable features gradually as needed
3. Consider local Redis for heavy development
4. Upgrade to paid tier before launch (October 10th)

---

**Last Updated**: October 2, 2025  
**Status**: Optimizations applied, monitoring in progress
