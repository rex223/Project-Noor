# Rate Limiting Examples

## Basic Usage with Decorator

### Spotify API Example
```python
from utils.rate_limiter import rate_limit, RateLimiter

@rate_limit('spotify')
def get_user_playlists(user_id: str):
    """Fetch playlists from Spotify API."""
    # This will automatically check rate limit for user_id
    # Rate limit: 100 requests per minute (from config)
    response = spotify_api.get_user_playlists(user_id)
    return response
```

### YouTube API Example
```python
from utils.rate_limiter import rate_limit

@rate_limit('youtube')
def get_watch_history(user_id: str):
    """Fetch watch history from YouTube API."""
    # Rate limit: 100 requests per minute
    response = youtube_api.get_watch_history(user_id)
    return response
```

### Steam API Example
```python
from utils.rate_limiter import rate_limit

@rate_limit('steam')
def get_game_stats(user_id: str, game_id: str):
    """Fetch game stats from Steam API."""
    # Rate limit: 200 requests per minute
    response = steam_api.get_game_stats(user_id, game_id)
    return response
```

## Manual Rate Limiting (Without Decorator)

```python
from utils.rate_limiter import RateLimiter, RateLimitExceeded

def fetch_spotify_data(user_id: str):
    limiter = RateLimiter('spotify')
    
    try:
        # Check rate limit before making API call
        limiter.check_rate_limit(user_id)
        
        # Make API call
        response = spotify_api.get_data(user_id)
        
        # Check remaining quota
        remaining = limiter.get_remaining(user_id)
        print(f"Remaining requests: {remaining}")
        
        return response
        
    except RateLimitExceeded as e:
        print(f"Rate limit hit! Retry after {e.retry_after} seconds")
        # Handle gracefully (queue, wait, notify user)
        return None
```

## FastAPI Integration

### Add Middleware to main.py
```python
from fastapi import FastAPI
from api.middleware.rate_limit import RateLimitMiddleware

app = FastAPI()
app.add_middleware(RateLimitMiddleware)
```

### Use in API Routes
```python
from fastapi import APIRouter, HTTPException
from utils.rate_limiter import spotify_limiter, RateLimitExceeded

router = APIRouter()

@router.get("/spotify/playlists/{user_id}")
async def get_playlists(user_id: str):
    try:
        # Check rate limit
        spotify_limiter.check_rate_limit(user_id)
        
        # Fetch data
        playlists = fetch_spotify_playlists(user_id)
        
        # Add rate limit info to response headers
        remaining = spotify_limiter.get_remaining(user_id)
        
        return {
            "data": playlists,
            "rate_limit": {
                "remaining": remaining,
                "limit": spotify_limiter.limit
            }
        }
        
    except RateLimitExceeded as e:
        # Middleware will automatically convert to 429 response
        raise e
```

## Celery Task Rate Limiting

```python
from celery import shared_task
from utils.rate_limiter import rate_limit, RateLimitExceeded

@shared_task(bind=True, max_retries=3)
@rate_limit('spotify')
def sync_spotify_data(self, user_id: str):
    """Background task to sync Spotify data."""
    try:
        # Rate limit is checked before execution
        data = fetch_spotify_data(user_id)
        return {"status": "success", "data": data}
        
    except RateLimitExceeded as e:
        # Retry after cooldown period
        raise self.retry(countdown=e.retry_after)
```

## Advanced: Per-User Rate Limiting in Agents

```python
# agents/music/spotify_agent.py
from utils.rate_limiter import spotify_limiter, RateLimitExceeded

class SpotifyAgent:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.limiter = spotify_limiter
    
    def fetch_data(self, endpoint: str):
        """Fetch data with automatic rate limiting."""
        try:
            # Check rate limit before each API call
            self.limiter.check_rate_limit(self.user_id)
            
            # Make API call
            response = self._make_request(endpoint)
            
            # Log remaining quota
            remaining = self.limiter.get_remaining(self.user_id)
            if remaining < 10:
                print(f"⚠️ Low rate limit: {remaining} requests left")
            
            return response
            
        except RateLimitExceeded as e:
            print(f"🚫 Rate limit exceeded for {self.user_id}")
            print(f"⏰ Retry after {e.retry_after} seconds")
            
            # Queue for later or notify user
            self._queue_for_retry(endpoint, e.retry_after)
            return None
```

## Testing Rate Limits

```python
# tests/test_rate_limiter.py
import time
from utils.rate_limiter import RateLimiter, RateLimitExceeded

def test_rate_limit():
    limiter = RateLimiter('spotify')  # 100 RPM
    user_id = "test_user_123"
    
    # First 100 requests should pass
    for i in range(100):
        try:
            limiter.check_rate_limit(user_id)
            print(f"✓ Request {i+1} allowed")
        except RateLimitExceeded:
            print(f"✗ Request {i+1} blocked (unexpected)")
    
    # 101st request should fail
    try:
        limiter.check_rate_limit(user_id)
        print("✗ Request 101 allowed (should be blocked)")
    except RateLimitExceeded as e:
        print(f"✓ Request 101 blocked: {e}")
        print(f"⏰ Retry after: {e.retry_after} seconds")
    
    # Reset for testing
    limiter.reset(user_id)
    print("✓ Rate limit reset")
    
    # Should work again
    limiter.check_rate_limit(user_id)
    print("✓ First request after reset allowed")

if __name__ == "__main__":
    test_rate_limit()
```

## Configuration

Rate limits are set in `.env`:
```bash
# Rate Limiting (requests per minute)
SPOTIFY_RPM=100      # Spotify API
YOUTUBE_RPM=100      # YouTube Data API
STEAM_RPM=200        # Steam Web API
OPENAI_RPM=3000      # OpenAI API
```

## Monitoring Rate Limits

```python
from utils.rate_limiter import spotify_limiter, youtube_limiter, steam_limiter

def check_all_rate_limits(user_id: str):
    """Check remaining quota for all services."""
    return {
        "spotify": {
            "remaining": spotify_limiter.get_remaining(user_id),
            "limit": spotify_limiter.limit
        },
        "youtube": {
            "remaining": youtube_limiter.get_remaining(user_id),
            "limit": youtube_limiter.limit
        },
        "steam": {
            "remaining": steam_limiter.get_remaining(user_id),
            "limit": steam_limiter.limit
        }
    }
```

## Best Practices

1. **Always use rate limiting for external APIs** (Spotify, YouTube, Steam, OpenAI)
2. **Use decorators for simplicity** (`@rate_limit('service')`)
3. **Handle RateLimitExceeded gracefully** (queue, retry with backoff)
4. **Monitor remaining quota** to avoid hitting limits
5. **Reset limits only for testing** (never in production)
6. **Use per-user identifiers** for fair distribution
7. **Set appropriate retry_after delays** when rate limited
8. **Add rate limit headers to API responses** for transparency

## Redis Storage

Rate limit data is stored in Redis with:
- **Keys**: `ratelimit:service:user_id`
- **Data Structure**: Sorted Set (ZSET) with timestamps
- **TTL**: 2x window size (auto-cleanup)
- **Algorithm**: Sliding window (more accurate than fixed window)
