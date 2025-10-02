"""
Monitor Redis commands to see what Celery is actually doing.
This will show you the exact Redis operations happening.
"""
import time
import redis
from core.config import get_config

config = get_config()

# Connect to Redis
redis_url = config.redis.url.replace('redis://', 'rediss://')
r = redis.from_url(redis_url, decode_responses=True)

print("🔍 Monitoring Redis commands for 30 seconds...")
print("=" * 60)
print()

# Get initial info
info_before = r.info('stats')
commands_before = info_before.get('total_commands_processed', 0)

# Monitor for 30 seconds
time.sleep(30)

# Get final info
info_after = r.info('stats')
commands_after = info_after.get('total_commands_processed', 0)

commands_in_30s = commands_after - commands_before
commands_per_minute = (commands_in_30s / 30) * 60
commands_per_day = commands_per_minute * 60 * 24

print(f"📊 Results:")
print(f"Commands in 30 seconds: {commands_in_30s}")
print(f"Commands per minute: {commands_per_minute:.1f}")
print(f"Commands per hour: {commands_per_minute * 60:.1f}")
print(f"Commands per day: {commands_per_day:.1f}")
print()
print(f"Free tier limit: 10,000 commands/day")
print(f"Overage: {commands_per_day - 10000:.1f} commands/day")
print()

# Show what keys exist
print("🔑 Current Redis keys:")
keys = r.keys('*')
for key in keys[:20]:  # Show first 20
    key_type = r.type(key)
    print(f"  - {key} ({key_type})")
if len(keys) > 20:
    print(f"  ... and {len(keys) - 20} more keys")
print()

# Show celery-specific keys
celery_keys = [k for k in keys if 'celery' in k.lower()]
print(f"🔧 Celery-related keys: {len(celery_keys)}")
for key in celery_keys[:10]:
    print(f"  - {key}")
