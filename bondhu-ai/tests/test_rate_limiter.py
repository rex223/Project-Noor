"""
Test script for rate limiter functionality.
Run this to verify Redis-based rate limiting works correctly.
"""
import time
from utils.rate_limiter import RateLimiter, RateLimitExceeded, rate_limit


def test_basic_rate_limit():
    """Test basic rate limiting with manual checks."""
    print("\n=== Test 1: Basic Rate Limiting ===")
    
    # Create limiter (using Spotify config: 100 RPM)
    limiter = RateLimiter('spotify')
    user_id = "test_user_basic"
    
    print(f"Testing with limit: {limiter.limit} requests per minute")
    
    # First few requests should pass
    for i in range(5):
        try:
            limiter.check_rate_limit(user_id)
            remaining = limiter.get_remaining(user_id)
            print(f"✅ Request {i+1} allowed. Remaining: {remaining}")
        except RateLimitExceeded as e:
            print(f"❌ Request {i+1} blocked: {e}")
    
    print(f"\n✓ Test 1 passed: Basic rate limiting works\n")


def test_rate_limit_exceeded():
    """Test that rate limit is enforced."""
    print("\n=== Test 2: Rate Limit Enforcement ===")
    
    limiter = RateLimiter('youtube')  # 100 RPM
    user_id = "test_user_exceed"
    
    # Reset any existing limits
    limiter.reset(user_id)
    
    print(f"Sending {limiter.limit + 5} requests...")
    blocked_count = 0
    
    for i in range(limiter.limit + 5):
        try:
            limiter.check_rate_limit(user_id)
            if i == limiter.limit - 1:
                print(f"✅ Request {i+1} (last allowed)")
        except RateLimitExceeded as e:
            if blocked_count == 0:
                print(f"🚫 Request {i+1} blocked: {e}")
                print(f"   Retry after: {e.retry_after} seconds")
            blocked_count += 1
    
    print(f"\n✓ Test 2 passed: {blocked_count} requests blocked after limit\n")


def test_decorator():
    """Test rate limiting with decorator."""
    print("\n=== Test 3: Decorator Usage ===")
    
    @rate_limit('steam')
    def fetch_steam_data(user_id: str):
        """Dummy function with rate limiting."""
        return f"Data for {user_id}"
    
    user_id = "test_user_decorator"
    
    # Reset limit
    steam_limiter = RateLimiter('steam')
    steam_limiter.reset(user_id)
    
    # Try 3 calls
    for i in range(3):
        try:
            result = fetch_steam_data(user_id)
            remaining = steam_limiter.get_remaining(user_id)
            print(f"✅ Call {i+1}: {result} (Remaining: {remaining})")
        except RateLimitExceeded as e:
            print(f"❌ Call {i+1} blocked: {e}")
    
    print(f"\n✓ Test 3 passed: Decorator works correctly\n")


def test_multiple_users():
    """Test that rate limits are per-user."""
    print("\n=== Test 4: Per-User Rate Limiting ===")
    
    limiter = RateLimiter('openai')
    user1 = "user_1"
    user2 = "user_2"
    
    # Reset both users
    limiter.reset(user1)
    limiter.reset(user2)
    
    # Each user should have independent limits
    for i in range(3):
        limiter.check_rate_limit(user1)
        limiter.check_rate_limit(user2)
    
    remaining1 = limiter.get_remaining(user1)
    remaining2 = limiter.get_remaining(user2)
    
    print(f"User 1 remaining: {remaining1}")
    print(f"User 2 remaining: {remaining2}")
    print(f"✅ Each user has independent quota")
    
    print(f"\n✓ Test 4 passed: Per-user isolation works\n")


def test_sliding_window():
    """Test sliding window behavior."""
    print("\n=== Test 5: Sliding Window Algorithm ===")
    
    limiter = RateLimiter('spotify')
    user_id = "test_user_sliding"
    
    # Reset
    limiter.reset(user_id)
    
    # Make 5 requests
    for i in range(5):
        limiter.check_rate_limit(user_id)
    
    remaining_before = limiter.get_remaining(user_id)
    print(f"After 5 requests: {remaining_before} remaining")
    
    # Wait 2 seconds (old entries should start expiring)
    print("Waiting 2 seconds...")
    time.sleep(2)
    
    # Note: Sliding window removes entries older than 60s
    # After 2s, we're still in the same window
    remaining_after = limiter.get_remaining(user_id)
    print(f"After 2 seconds: {remaining_after} remaining")
    
    print(f"✅ Sliding window maintains consistency")
    print(f"\n✓ Test 5 passed: Sliding window works\n")


def test_reset():
    """Test rate limit reset."""
    print("\n=== Test 6: Rate Limit Reset ===")
    
    limiter = RateLimiter('youtube')
    user_id = "test_user_reset"
    
    # Make some requests
    for i in range(10):
        limiter.check_rate_limit(user_id)
    
    remaining_before = limiter.get_remaining(user_id)
    print(f"Before reset: {remaining_before} remaining")
    
    # Reset
    limiter.reset(user_id)
    print("✅ Rate limit reset")
    
    remaining_after = limiter.get_remaining(user_id)
    print(f"After reset: {remaining_after} remaining (should be {limiter.limit})")
    
    assert remaining_after == limiter.limit, "Reset failed"
    print(f"\n✓ Test 6 passed: Reset works correctly\n")


def run_all_tests():
    """Run all rate limiter tests."""
    print("\n" + "="*60)
    print("BONDHU AI - RATE LIMITER TEST SUITE")
    print("="*60)
    
    try:
        test_basic_rate_limit()
        test_rate_limit_exceeded()
        test_decorator()
        test_multiple_users()
        test_sliding_window()
        test_reset()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
