# 🚀 Quick Reference - Day 1 Complete

## ✅ What's Working Now

### Redis Cache
```python
from core.cache.redis_client import get_redis, cache_set, cache_get

# Get client
redis = get_redis()

# Simple operations
cache_set('key', 'value', ttl_seconds=3600)
value = cache_get('key')
```

### Celery Background Tasks
```python
from core.tasks.personality import analyze_chat_sentiment_batch

# Queue a task
result = analyze_chat_sentiment_batch.delay(user_id="123")

# Check status
print(result.status)  # PENDING, SUCCESS, FAILURE
```

### Rate Limiting
```python
from utils.rate_limiter import rate_limit, spotify_limiter

# With decorator
@rate_limit('spotify')
def get_playlists(user_id: str):
    return spotify_api.get_playlists(user_id)

# Manual check
try:
    spotify_limiter.check_rate_limit(user_id)
    remaining = spotify_limiter.get_remaining(user_id)
except RateLimitExceeded as e:
    print(f"Retry after {e.retry_after}s")
```

---

## 🎯 Start Services

```powershell
# Terminal 1: Celery Worker
cd "c:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
.\.venv\Scripts\Activate.ps1
celery -A core.celery_app worker --loglevel=info --pool=solo

# Terminal 2: Celery Beat (optional - periodic tasks)
celery -A core.celery_app beat --loglevel=info

# Terminal 3: Flower Monitoring (optional)
celery -A core.celery_app flower --port=5555
# Open: http://localhost:5555
```

---

## 📊 Rate Limits (From .env)

| Service | Limit | Config Variable |
|---------|-------|-----------------|
| Spotify | 100 RPM | `SPOTIFY_RPM=100` |
| YouTube | 100 RPM | `YOUTUBE_RPM=100` |
| Steam | 200 RPM | `STEAM_RPM=200` |
| OpenAI | 3000 RPM | `OPENAI_RPM=3000` |

---

## 🔧 Test Commands

```powershell
# Test Redis
python -c "from core.cache.redis_client import get_redis; r = get_redis(); r.set('test', 'works'); print('✅ Redis:', r.get('test'))"

# Test Rate Limiter
python tests\test_rate_limiter.py

# Check Celery tasks
celery -A core.celery_app inspect registered

# Check active tasks
celery -A core.celery_app inspect active
```

---

## 📁 Key Files Created Today

```
core/
├── cache/redis_client.py           # Redis connection
├── celery_app.py                    # Celery config
└── tasks/personality.py             # Background tasks

utils/
└── rate_limiter.py                  # Rate limiting logic

api/middleware/
└── rate_limit.py                    # FastAPI middleware

tests/
└── test_rate_limiter.py             # Test suite

docs/
├── DAY_1_SUMMARY.md                 # Today's work
├── SETUP_CHECKLIST.md               # 8-day plan
└── RATE_LIMITING_EXAMPLES.md        # Usage guide
```

---

## 🐛 If Something Breaks

### Redis Connection Failed
```powershell
# Check .env has correct URL
cat .env | Select-String "REDIS_URL"

# Should be: rediss://default:TOKEN@romantic-terrapin-16956.upstash.io:6379
```

### Celery Won't Start
```powershell
# Check broker URL has ssl_cert_reqs parameter
cat .env | Select-String "CELERY_BROKER_URL"

# Should end with: ?ssl_cert_reqs=CERT_NONE
```

### Rate Limiter Error
```python
# Reset a user's rate limit (testing only)
from utils.rate_limiter import spotify_limiter
spotify_limiter.reset("user_id")
```

---

## 📈 Next: Day 2 (Tomorrow)

### Priority: Fix Chat Message Disappearing
1. Load last 50 messages on dashboard mount
2. Cache in Redis with 24h TTL
3. Persist new messages to Supabase immediately
4. Add message search

**Time**: 4-6 hours  
**Files to edit**:
- `api/routes/chat.py` (new endpoint)
- `src/app/dashboard/page.tsx` (load history)
- `components/ui/enhanced-chat.tsx` (optimistic updates)

---

## 🎉 Day 1 Status

**✅ COMPLETED** (13:45, Oct 2)
- Redis cache operational
- Celery workers running  
- Rate limiting active
- Documentation complete

**7 days until Oct 10 launch!** 🚀

---

**Keep this file open for quick reference while coding!**
