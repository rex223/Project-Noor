# 🐳 Bondhu AI - Docker Setup Guide

Complete Docker containerization for the Bondhu AI project with Redis, Celery, and main application services.

## 🚀 Quick Start (2 minutes)

### Prerequisites
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop/))
- Git (to clone repository)

### 1. Clone & Navigate
```bash
git clone <repository-url>
cd Project-Noor/bondhu-ai
```

### 2. Build & Run Everything
```bash
docker-compose up --build -d
```

### 3. Verify Services
```bash
# Check all services are running
docker-compose ps

# Test Redis connection
docker exec bondhu-redis redis-cli ping
# Should return: PONG

# Check API health (once it's running)
curl http://localhost:8000/health
```

**🎉 Done! Your complete Bondhu AI stack is running!**

---

## 📋 Services Overview

| Service | Port | Description |
|---------|------|-------------|
| **bondhu-api** | 8000 | Main FastAPI/Flask application |
| **redis** | 6379 | Redis cache & message broker |
| **celery-worker** | - | Background task processor |
| **celery-beat** | - | Scheduled task scheduler |
| **flower** | 5555 | Celery monitoring dashboard |

---

## 🔧 Development Commands

### Basic Operations
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart bondhu-api

# View logs
docker-compose logs -f bondhu-api
docker-compose logs -f celery-worker

# Rebuild after code changes
docker-compose up --build -d
```

### Service Management
```bash
# Scale Celery workers
docker-compose up -d --scale celery-worker=3

# Run commands in containers
docker-compose exec bondhu-api python -c "print('Hello from container')"
docker-compose exec redis redis-cli

# Shell access
docker-compose exec bondhu-api bash
```

---

## 🌐 Access Points

- **Main API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs (if FastAPI)
- **Flower (Celery Monitor):** http://localhost:5555
- **Redis:** localhost:6379 (for external tools)

---

## 🔍 Monitoring & Debugging

### Health Checks
```bash
# Check service health
docker-compose ps

# Detailed service status
docker inspect bondhu-api | grep -A 10 "Health"

# Test connections
docker-compose exec bondhu-api python -c "
from core.cache.redis_client import get_redis
r = get_redis()
r.set('test', 'docker-works')
print('✅ Redis:', r.get('test'))
"
```

### Logs & Debugging
```bash
# Follow logs in real-time
docker-compose logs -f

# Last 100 lines from specific service
docker-compose logs --tail=100 celery-worker

# Debug container issues
docker-compose exec bondhu-api env
docker-compose exec bondhu-api python --version
```

---

## 🛠 Production Configuration

### Environment Variables
Create `.env` file for production:
```bash
# Production Redis (Upstash)
REDIS_URL=rediss://default:password@host:6379
CELERY_BROKER_URL=rediss://default:password@host:6379
CELERY_RESULT_BACKEND=rediss://default:password@host:6379

# Security
SECRET_KEY=your-secret-key
DEBUG=false

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Production Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  bondhu-api:
    build: .
    ports:
      - "80:8000"
    environment:
      - REDIS_URL=${REDIS_URL}
      - DATABASE_URL=${DATABASE_URL}
    restart: always
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

---

## 🔄 Data Persistence

### Redis Data Backup
```bash
# Backup Redis data
docker exec bondhu-redis redis-cli SAVE
docker cp bondhu-redis:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb

# Restore Redis data
docker cp ./redis-backup.rdb bondhu-redis:/data/dump.rdb
docker-compose restart redis
```

### Logs Persistence
Logs are mounted to `./logs/` directory and persist across container restarts.

---

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find process using port
netstat -ano | findstr :8000
# Kill process (Windows)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead
```

**Container won't start:**
```bash
# Check container logs
docker-compose logs bondhu-api

# Check if all dependencies are met
docker-compose config --quiet && echo "Config OK" || echo "Config Error"

# Rebuild with no cache
docker-compose build --no-cache
```

**Redis connection failed:**
```bash
# Test Redis directly
docker-compose exec redis redis-cli ping

# Check network connectivity
docker-compose exec bondhu-api ping redis

# Verify environment variables
docker-compose exec bondhu-api env | grep REDIS
```

### Performance Issues
```bash
# Monitor resource usage
docker stats

# Check container resources
docker-compose exec bondhu-api cat /proc/meminfo
docker-compose exec bondhu-api df -h
```

---

## 📚 Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Bondhu API    │    │     Flower      │
│   (Port 8000)   │    │   (Port 5555)   │
└─────────┬───────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│      Redis      │◄───┤ Celery Worker   │
│   (Port 6379)   │    │                 │
└─────────┬───────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐
│  Celery Beat    │
│   (Scheduler)   │
└─────────────────┘
```

---

## 🚢 Deployment Options

### Local Development
```bash
docker-compose up -d
```

### Staging/Production
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Cloud Deployment (Docker Swarm/Kubernetes)
```bash
# Docker Swarm
docker stack deploy -c docker-compose.yml bondhu-stack

# Kubernetes (requires k8s manifests)
kubectl apply -f k8s/
```

---

## 📋 Team Checklist

- [ ] Docker Desktop installed
- [ ] Repository cloned
- [ ] `docker-compose up --build -d` executed
- [ ] All services show "healthy" in `docker-compose ps`
- [ ] API accessible at http://localhost:8000
- [ ] Flower dashboard accessible at http://localhost:5555
- [ ] Redis responding to ping

---

## 🔗 Useful Links

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Redis Docker Hub](https://hub.docker.com/_/redis)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Flower Documentation](https://flower.readthedocs.io/)

---

## 📞 Support

If you encounter issues:
1. Check this troubleshooting guide
2. Review container logs: `docker-compose logs service-name`
3. Verify Docker Desktop is running
4. Check disk space and memory availability

**Setup Time: ~2 minutes** ⏱️
**Team Productivity: +500%** 🚀