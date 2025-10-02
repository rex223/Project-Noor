# Setup Local Redis for Development

## 🎯 Goal
Run Redis locally (free, unlimited commands) for Celery + caching during development.

---

## Option 1: Docker (Recommended) ⭐

### Prerequisites
- Docker Desktop for Windows
- Download: https://www.docker.com/products/docker-desktop/

### Steps

**1. Start Redis Container:**
```powershell
# Pull and run Redis
docker run -d `
  --name bondhu-redis `
  -p 6379:6379 `
  --restart unless-stopped `
  redis:alpine

# Verify it's running
docker ps
```

**2. Update `.env` in `bondhu-ai` folder:**
```bash
# Comment out Upstash URLs
# REDIS_URL=rediss://default:TOKEN@romantic-terrapin-16956.upstash.io:6379
# CELERY_BROKER_URL=rediss://default:TOKEN@romantic-terrapin-16956.upstash.io:6379?ssl_cert_reqs=CERT_NONE
# CELERY_RESULT_BACKEND=rediss://default:TOKEN@romantic-terrapin-16956.upstash.io:6379?ssl_cert_reqs=CERT_NONE

# Add local Redis URLs
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
```

**3. Test Connection:**
```powershell
cd "c:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
.\.venv\Scripts\Activate.ps1

python -c "from core.cache.redis_client import get_redis; r = get_redis(); r.set('test', 'local_works'); print('✅ Local Redis:', r.get('test'))"
```

**4. Start Celery (Unlimited Polling!):**
```powershell
celery -A core.celery_app worker --loglevel=info --pool=solo
```

**5. Useful Docker Commands:**
```powershell
# Stop Redis
docker stop bondhu-redis

# Start Redis
docker start bondhu-redis

# View Redis logs
docker logs bondhu-redis

# Remove Redis container
docker rm -f bondhu-redis

# Connect to Redis CLI
docker exec -it bondhu-redis redis-cli
```

---

## Option 2: Native Redis for Windows

### Prerequisites
- Redis for Windows (unofficial build)

### Steps

**1. Download Redis:**
- Go to: https://github.com/tporadowski/redis/releases
- Download: `Redis-x64-5.0.14.1.zip`
- Extract to: `C:\Redis`

**2. Install as Windows Service:**
```powershell
# Open PowerShell as Administrator
cd C:\Redis
.\redis-server.exe --service-install redis.windows.conf
.\redis-server.exe --service-start
```

**3. Update `.env` (same as Docker option above)**

**4. Test Connection (same as Docker option above)**

---

## Option 3: WSL2 with Redis (Linux on Windows)

### Prerequisites
- Windows 11 with WSL2 enabled

### Steps

**1. Install Redis in WSL:**
```bash
# In WSL terminal
sudo apt update
sudo apt install redis-server

# Start Redis
sudo service redis-server start

# Check status
redis-cli ping
# Should return: PONG
```

**2. Update `.env`:**
```bash
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
```

**3. Test from Windows:**
```powershell
cd "c:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
.\.venv\Scripts\Activate.ps1

python -c "from core.cache.redis_client import get_redis; r = get_redis(); r.set('test', 'wsl_works'); print('✅ WSL Redis:', r.get('test'))"
```

---

## 🔧 Troubleshooting

### Issue: "Connection refused" error

**Check if Redis is running:**
```powershell
# Docker
docker ps | Select-String "bondhu-redis"

# Windows Service
Get-Service | Select-String "redis"

# WSL
wsl redis-cli ping
```

**Restart Redis:**
```powershell
# Docker
docker restart bondhu-redis

# Windows Service
net stop Redis
net start Redis

# WSL
sudo service redis-server restart
```

---

### Issue: "No module named 'redis'" in Python

**Reinstall Redis package:**
```powershell
cd bondhu-ai
.\.venv\Scripts\Activate.ps1
pip install redis==4.6.0
```

---

### Issue: Port 6379 already in use

**Find what's using the port:**
```powershell
netstat -ano | findstr :6379
```

**Kill the process:**
```powershell
# Replace PID with the number from netstat
taskkill /PID 12345 /F
```

---

## 🎯 Verify Everything Works

**Full Test Suite:**
```powershell
cd "c:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
.\.venv\Scripts\Activate.ps1

# Test 1: Redis connection
python -c "from core.cache.redis_client import get_redis; r = get_redis(); print('✅ Redis connected')"

# Test 2: Cache operations
python -c "from core.cache.redis_client import cache_set, cache_get; cache_set('test', 'data', 60); print('✅ Cache:', cache_get('test'))"

# Test 3: Rate limiter
python -c "from utils.rate_limiter import spotify_limiter; spotify_limiter.check_rate_limit('test_user'); print('✅ Rate limiter works')"

# Test 4: Celery task
celery -A core.celery_app worker --loglevel=info --pool=solo
# Should show "celery@LAPTOP ready" with 4 tasks

# Test 5: Celery inspect (in new terminal)
celery -A core.celery_app inspect ping
# Should return: {'celery@LAPTOP': {'ok': 'pong'}}
```

---

## 📊 Benefits of Local Redis

| Feature | Upstash Free | Local Redis |
|---------|--------------|-------------|
| Commands | 10,000/day ❌ | Unlimited ✅ |
| Cost | $0 | $0 |
| Latency | 50-100ms | <1ms ⚡ |
| Offline | No | Yes ✅ |
| Celery 24/7 | No ❌ | Yes ✅ |
| Setup Time | 5 min | 10 min |

---

## 🚀 Quick Commands Reference

```powershell
# Start all services for development
docker start bondhu-redis
cd "c:\Users\mdhaa\Desktop\Project Noor\bondhu-ai"
.\.venv\Scripts\Activate.ps1
celery -A core.celery_app worker --loglevel=info --pool=solo

# In another terminal: Start backend
cd bondhu-ai
python main.py

# In another terminal: Start frontend
cd bondhu-landing
npm run dev
```

---

## 🔄 Switch Between Local and Upstash

**Development (Local Redis):**
```bash
# .env
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
```

**Production (Upstash):**
```bash
# .env
REDIS_URL=rediss://default:TOKEN@romantic-terrapin-16956.upstash.io:6379
CELERY_BROKER_URL=rediss://default:TOKEN@romantic-terrapin-16956.upstash.io:6379?ssl_cert_reqs=CERT_NONE
CELERY_RESULT_BACKEND=rediss://default:TOKEN@romantic-terrapin-16956.upstash.io:6379?ssl_cert_reqs=CERT_NONE
```

**Just change 3 lines in `.env` - that's it!** 🎉

---

## 📝 Recommended Workflow

1. **Day 1-8 (Development)**: Use local Redis
2. **Day 9 (Pre-launch)**: Switch to Upstash, test production config
3. **Day 10+ (Production)**: Keep Upstash, upgrade to paid tier if needed

---

**Setup Time**: 10 minutes  
**Cost**: $0  
**Benefits**: Unlimited commands, faster, works offline  
**Recommended for**: All development work ✅
