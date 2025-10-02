# Day 2: Chat Persistence Testing Guide

**Date**: January 2025  
**Feature**: Chat message persistence with Redis caching

---

## 🎯 Test Objectives

1. Verify messages persist across page refreshes
2. Confirm Redis caching improves performance
3. Validate cache invalidation works correctly
4. Test search functionality
5. Ensure error handling and fallbacks work

---

## 🧪 Backend Tests

### Test 1: Cache Hit on Second Request

**Steps**:
1. Start backend server: `cd bondhu-ai && python -m uvicorn main:app --reload`
2. Send GET request to `/api/v1/chat/history/{user_id}`
3. Check logs for "Cache MISS"
4. Send same request again immediately
5. Check logs for "Cache HIT"

**Expected Result**:
```
[INFO] Cache MISS for chat history: chat:history:{user_id}:20:0
[INFO] Cached chat history for 86400s: chat:history:{user_id}:20:0
[INFO] Cache HIT for chat history: chat:history:{user_id}:20:0
```

**Command**:
```bash
# First request (cache miss)
curl http://localhost:8000/api/v1/chat/history/{your-user-id}

# Second request (cache hit - should be instant)
curl http://localhost:8000/api/v1/chat/history/{your-user-id}
```

---

### Test 2: Cache Invalidation After New Message

**Steps**:
1. Load chat history (creates cache)
2. Send new message via POST `/api/v1/chat/send`
3. Check logs for "Invalidated X cache keys"
4. Load history again
5. Verify new message appears

**Expected Result**:
```
[INFO] Cache HIT for chat history: chat:history:{user_id}:20:0
[INFO] Chat message stored with ID: {message_id}
[INFO] Invalidated 3 cache keys for user {user_id}
[INFO] Cache MISS for chat history: chat:history:{user_id}:20:0
```

**Command**:
```bash
# Send message
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -d '{"user_id": "{your-user-id}", "message": "Test message"}'

# Load history (should see new message)
curl http://localhost:8000/api/v1/chat/history/{your-user-id}
```

---

### Test 3: Search Functionality

**Steps**:
1. Seed database with test messages containing "personality"
2. Search for "personality" via GET `/api/v1/chat/search/{user_id}?q=personality`
3. Verify only matching messages returned
4. Search again with same query
5. Check logs for cache hit

**Expected Result**:
```json
{
  "messages": [
    {
      "id": "...",
      "message": "Tell me about personality traits",
      "response": "Your personality profile shows...",
      "has_personality_context": true,
      "created_at": "2025-01-02T..."
    }
  ],
  "total": 1,
  "user_id": "{user_id}"
}
```

**Command**:
```bash
# Search for messages
curl "http://localhost:8000/api/v1/chat/search/{your-user-id}?q=personality&limit=10"
```

---

### Test 4: Cache Expiration

**Steps**:
1. Load chat history (creates cache with 24h TTL)
2. Check Redis TTL: `redis-cli TTL chat:history:{user_id}:20:0`
3. Verify TTL is ~86400 seconds

**Expected Result**:
```bash
$ docker exec bondhu-redis redis-cli TTL chat:history:abc123:20:0
(integer) 86395  # Should be close to 86400
```

---

### Test 5: Clear History Invalidates Cache

**Steps**:
1. Load chat history (creates cache)
2. Send DELETE `/api/v1/chat/history/{user_id}`
3. Check logs for cache invalidation
4. Load history again
5. Verify returns empty array

**Command**:
```bash
# Clear history
curl -X DELETE http://localhost:8000/api/v1/chat/history/{your-user-id}

# Load history (should be empty)
curl http://localhost:8000/api/v1/chat/history/{your-user-id}
```

---

## 🎨 Frontend Tests

### Test 6: Load History on Dashboard Mount

**Steps**:
1. Send a few test messages via dashboard
2. Refresh page (Ctrl+R or F5)
3. Observe loading state appears
4. Verify all previous messages load
5. Check console for API calls

**Expected Result**:
- Loading spinner shows briefly
- All previous messages appear in order
- Scroll position at bottom
- Console shows: `GET /api/v1/chat/history/{user_id}` (200 OK)

**Manual Test**:
1. Navigate to http://localhost:3000/dashboard
2. Send message: "Hello Bondhu!"
3. Wait for response
4. Press F5 to refresh
5. ✅ Message still visible

---

### Test 7: Greeting Shows If No History

**Steps**:
1. Create fresh user account or clear existing history
2. Navigate to dashboard
3. Verify greeting message appears

**Expected Result**:
```
Hello {Name}! 🌟 I'm Bondhu, your AI companion. 
I've been looking forward to continuing our conversation. 
How are you feeling today?
```

---

### Test 8: Loading State During History Fetch

**Steps**:
1. Slow down network (Chrome DevTools: Network → Slow 3G)
2. Refresh dashboard
3. Observe loading animation

**Expected Result**:
- Animated Bondhu avatar appears
- Text: "Loading your conversation history..."
- No layout shift when messages load

---

### Test 9: Error Handling for Failed History Load

**Steps**:
1. Stop backend server
2. Refresh dashboard
3. Verify error handling

**Expected Result**:
- Greeting message shows (fallback)
- Console shows error (not visible to user)
- No blank screen or crash

---

### Test 10: Search UI (if implemented)

**Steps**:
1. Open chat search (if UI added)
2. Type "personality"
3. Verify matching messages highlighted
4. Search again (should use cache)

---

## 🔍 Redis Cache Inspection

### Check Cache Keys

```bash
# List all chat cache keys
docker exec bondhu-redis redis-cli KEYS "chat:*"

# Output example:
1) "chat:history:abc-123:20:0"
2) "chat:history:abc-123:50:0"
3) "chat:search:abc-123:personality:20"
```

### Check Cache Content

```bash
# Get cached history
docker exec bondhu-redis redis-cli GET "chat:history:abc-123:20:0"

# Output (JSON):
{
  "messages": [...],
  "total": 5,
  "user_id": "abc-123"
}
```

### Monitor Cache Operations in Real-Time

```bash
# Watch Redis commands
docker exec bondhu-redis redis-cli MONITOR
```

**Expected Output When Loading History**:
```
1673456789.123456 [0 127.0.0.1:12345] "GET" "chat:history:abc-123:20:0"
1673456790.234567 [0 127.0.0.1:12345] "SETEX" "chat:history:abc-123:20:0" "86400" "{...}"
```

---

## 📊 Performance Testing

### Measure Cache Hit Performance

**Script**: `test_cache_performance.py`

```python
import time
import requests

API_URL = "http://localhost:8000/api/v1/chat/history/test-user-123"

def measure_request():
    start = time.time()
    response = requests.get(API_URL)
    elapsed = (time.time() - start) * 1000  # Convert to ms
    return elapsed, response.status_code

# First request (cache miss)
time1, status1 = measure_request()
print(f"Cache MISS: {time1:.2f}ms (Status: {status1})")

# Second request (cache hit)
time2, status2 = measure_request()
print(f"Cache HIT: {time2:.2f}ms (Status: {status2})")

# Performance improvement
improvement = ((time1 - time2) / time1) * 100
print(f"Performance Improvement: {improvement:.1f}%")
```

**Expected Output**:
```
Cache MISS: 523.45ms (Status: 200)
Cache HIT: 4.12ms (Status: 200)
Performance Improvement: 99.2%
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Cache Always Misses
**Symptoms**: Every request shows "Cache MISS" in logs

**Causes**:
1. Redis not running
2. Wrong Redis URL in `.env`
3. Cache key format changed

**Solution**:
```bash
# Check Redis is running
docker ps | grep bondhu-redis

# Test Redis connection
docker exec bondhu-redis redis-cli PING
# Expected: PONG

# Check environment variable
cd bondhu-ai
cat .env | grep REDIS_URL
# Expected: REDIS_URL=redis://localhost:6379
```

---

### Issue 2: Messages Don't Persist After Refresh
**Symptoms**: Page refresh shows greeting instead of history

**Causes**:
1. Frontend not calling `loadChatHistory()`
2. User ID not set
3. Backend `/history` endpoint failing

**Solution**:
```typescript
// Check browser console for errors
console.log('User ID:', userId);
console.log('Loading history...');

// Verify API call
const history = await chatApi.getChatHistory(userId);
console.log('History loaded:', history);
```

---

### Issue 3: Cache Not Invalidating After Send
**Symptoms**: New message sent but old cached history returned

**Causes**:
1. `invalidate_user_chat_cache()` not called in `/send` endpoint
2. Redis SCAN not finding keys
3. Wrong cache key pattern

**Solution**:
```python
# Add logging to invalidation function
logger.info(f"Scanning for keys: chat:*:{user_id}:*")
logger.info(f"Deleted {deleted} keys")

# Manually clear cache
docker exec bondhu-redis redis-cli KEYS "chat:*" | xargs -I{} docker exec bondhu-redis redis-cli DEL {}
```

---

### Issue 4: Search Returns Wrong Results
**Symptoms**: Search for "test" returns unrelated messages

**Causes**:
1. Case sensitivity issue in query
2. Wrong SQL ILIKE syntax
3. Not searching both message and response

**Solution**:
```python
# Verify query construction
search_term = f"%{q.lower()}%"
logger.info(f"Search term: {search_term}")

# Test SQL directly
.or_(f"message.ilike.{search_term},response.ilike.{search_term}")
```

---

## ✅ Success Criteria

| Test | Criteria | Status |
|------|----------|--------|
| Cache Hit | Second request < 10ms | ⏳ |
| Cache Invalidation | New message clears cache | ⏳ |
| History Load | Messages persist after refresh | ⏳ |
| Loading State | Shows during fetch | ⏳ |
| Search | Returns correct results | ⏳ |
| Error Handling | No crashes on failure | ⏳ |
| Greeting Fallback | Shows when no history | ⏳ |
| Performance | 99%+ improvement on cache hit | ⏳ |

---

## 🚀 Automated Testing (Future)

### Unit Tests
```python
# tests/test_chat_cache.py
import pytest
from api.routes.chat import get_chat_history_cache_key

def test_cache_key_generation():
    key = get_chat_history_cache_key("user-123", 20, 0)
    assert key == "chat:history:user-123:20:0"

@pytest.mark.asyncio
async def test_cache_invalidation():
    await invalidate_user_chat_cache("user-123")
    # Verify keys deleted
```

### Integration Tests
```python
# tests/test_chat_integration.py
@pytest.mark.asyncio
async def test_send_message_invalidates_cache():
    # Load history (creates cache)
    history1 = await get_chat_history("user-123")
    
    # Send message
    await send_chat_message(ChatRequest(...))
    
    # Load history again (should be fresh)
    history2 = await get_chat_history("user-123")
    assert len(history2.messages) > len(history1.messages)
```

---

**Ready to Test!** Run through checklist and mark items as complete. 🧪
