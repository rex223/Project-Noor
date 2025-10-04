"""Redis-backed rate limiter for YouTube Data API access."""

from __future__ import annotations

import asyncio
import os
from typing import Optional
from dataclasses import dataclass

import redis


@dataclass
class RateLimitConfig:
    """Configuration values for YouTube API throttling."""

    api_key: str
    per_second: int
    per_minute: int
    burst: int = 1


class YouTubeRateLimiter:
    """Token-bucket style limiter shared across workers using Redis."""

    def __init__(
        self,
        *,
        config: RateLimitConfig,
        redis_client: Optional[redis.Redis] = None,
    ) -> None:
        self.config = config
        self.redis = redis_client

        # Local fallback counters if Redis unavailable.
        self._local_lock = asyncio.Lock()
        self._local_second_window = 0
        self._local_second_count = 0
        self._local_minute_window = 0
        self._local_minute_count = 0

    @property
    def _sec_key(self) -> str:
        return f"yt:rate:{self.config.api_key}:sec"

    @property
    def _min_key(self) -> str:
        return f"yt:rate:{self.config.api_key}:min"

    async def acquire(self) -> None:
        """Wait until a request slot is available."""

        if self.redis is None:
            await self._acquire_local()
        else:
            await self._acquire_redis()

    async def _acquire_redis(self) -> None:
        loop = asyncio.get_running_loop()

        while True:
            sec_count, min_count = await loop.run_in_executor(None, self._increment_counters)

            if sec_count <= self.config.per_second and min_count <= self.config.per_minute:
                return

            await loop.run_in_executor(None, self._decrement_counters)

            if sec_count > self.config.per_second:
                await asyncio.sleep(max(0.05, 1.0 / max(1, self.config.per_second)))
            else:
                await asyncio.sleep(1.0)

    def _increment_counters(self) -> tuple[int, int]:
        pipe = self.redis.pipeline()
        pipe.incr(self._sec_key)
        pipe.expire(self._sec_key, 1)
        pipe.incr(self._min_key)
        pipe.expire(self._min_key, 60)
        sec_count, _, min_count, _ = pipe.execute()
        return int(sec_count), int(min_count)

    def _decrement_counters(self) -> None:
        pipe = self.redis.pipeline()
        pipe.decr(self._sec_key)
        pipe.decr(self._min_key)
        pipe.execute()

    async def _acquire_local(self) -> None:
        while True:
            async with self._local_lock:
                loop = asyncio.get_running_loop()
                now = loop.time()

                if now - self._local_second_window >= 1:
                    self._local_second_window = now
                    self._local_second_count = 0

                if now - self._local_minute_window >= 60:
                    self._local_minute_window = now
                    self._local_minute_count = 0

                if (
                    self._local_second_count < self.config.per_second
                    and self._local_minute_count < self.config.per_minute
                ):
                    self._local_second_count += 1
                    self._local_minute_count += 1
                    return

            await asyncio.sleep(max(0.05, 1.0 / max(1, self.config.per_second)))
