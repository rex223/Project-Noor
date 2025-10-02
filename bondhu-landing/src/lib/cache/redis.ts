/**
 * Redis Cache Utilities for Next.js
 * Uses Upstash Redis REST API (serverless-friendly)
 */

import { Redis } from '@upstash/redis';

// Initialize Redis client (will use env vars)
export const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

/**
 * Get cached value
 * @param key Cache key
 * @returns Cached value or null
 */
export async function getCached<T>(key: string): Promise<T | null> {
  try {
    const cached = await redis.get(key);
    return cached as T | null;
  } catch (error) {
    console.error(`Redis GET error for key ${key}:`, error);
    return null;
  }
}

/**
 * Set cached value with TTL
 * @param key Cache key
 * @param value Value to cache
 * @param ttlSeconds Time to live in seconds
 */
export async function setCached<T>(
  key: string,
  value: T,
  ttlSeconds: number
): Promise<void> {
  try {
    await redis.setex(key, ttlSeconds, JSON.stringify(value));
  } catch (error) {
    console.error(`Redis SETEX error for key ${key}:`, error);
  }
}

/**
 * Delete cached value
 * @param key Cache key to delete
 */
export async function deleteCached(key: string): Promise<void> {
  try {
    await redis.del(key);
  } catch (error) {
    console.error(`Redis DEL error for key ${key}:`, error);
  }
}

/**
 * Delete all keys matching pattern
 * @param pattern Key pattern (e.g., "chat:*")
 */
export async function deletePattern(pattern: string): Promise<void> {
  try {
    const keys = await redis.keys(pattern);
    if (keys.length > 0) {
      await redis.del(...keys);
    }
  } catch (error) {
    console.error(`Redis DEL pattern error for ${pattern}:`, error);
  }
}

/**
 * Check if key exists
 * @param key Cache key
 * @returns True if exists, false otherwise
 */
export async function cacheExists(key: string): Promise<boolean> {
  try {
    const exists = await redis.exists(key);
    return exists > 0;
  } catch (error) {
    console.error(`Redis EXISTS error for key ${key}:`, error);
    return false;
  }
}

/**
 * Get remaining TTL for key
 * @param key Cache key
 * @returns TTL in seconds, -1 if no expiry, -2 if key doesn't exist
 */
export async function cacheTTL(key: string): Promise<number> {
  try {
    return await redis.ttl(key);
  } catch (error) {
    console.error(`Redis TTL error for key ${key}:`, error);
    return -2;
  }
}

/**
 * Cache key generators
 */
export const cacheKeys = {
  // Chat related
  chatHistory: (userId: string, limit: number) => `chat:history:${userId}:${limit}`,
  chatSession: (sessionId: string) => `chat:session:${sessionId}`,
  
  // Personality related
  personalityContext: (userId: string) => `personality:context:${userId}`,
  personalitySentiment: (userId: string) => `personality:sentiment:${userId}`,
  
  // Music related
  musicProfile: (userId: string) => `music:profile:${userId}`,
  spotifyData: (userId: string) => `music:spotify:${userId}`,
  
  // Video related
  videoProfile: (userId: string) => `video:youtube:${userId}`,
  
  // Session related
  activeSession: (userId: string) => `session:active:${userId}`,
  
  // Rate limiting
  rateLimitSpotify: (userId: string) => `ratelimit:spotify:${userId}`,
  rateLimitYouTube: (userId: string) => `ratelimit:youtube:${userId}`,
};

/**
 * Cache TTL constants (in seconds)
 */
export const cacheTTLs = {
  SHORT: 5 * 60,        // 5 minutes
  MEDIUM: 30 * 60,      // 30 minutes
  LONG: 60 * 60,        // 1 hour
  DAILY: 24 * 60 * 60,  // 24 hours
  WEEKLY: 7 * 24 * 60 * 60,  // 7 days
};

/**
 * Typed cache helpers for common use cases
 */

// Chat history cache
export async function getChatHistory(userId: string, limit: number = 50) {
  const key = cacheKeys.chatHistory(userId, limit);
  return getCached<any[]>(key);
}

export async function setChatHistory(
  userId: string,
  messages: any[],
  limit: number = 50
) {
  const key = cacheKeys.chatHistory(userId, limit);
  await setCached(key, messages, cacheTTLs.SHORT);
}

export async function invalidateChatHistory(userId: string) {
  await deletePattern(`chat:history:${userId}:*`);
}

// Personality context cache
export async function getPersonalityContext(userId: string) {
  const key = cacheKeys.personalityContext(userId);
  return getCached<any>(key);
}

export async function setPersonalityContext(userId: string, context: any) {
  const key = cacheKeys.personalityContext(userId);
  await setCached(key, context, cacheTTLs.MEDIUM);
}

export async function invalidatePersonalityContext(userId: string) {
  await deleteCached(cacheKeys.personalityContext(userId));
  await deleteCached(cacheKeys.personalitySentiment(userId));
}

// Music profile cache
export async function getMusicProfile(userId: string) {
  const key = cacheKeys.musicProfile(userId);
  return getCached<any>(key);
}

export async function setMusicProfile(userId: string, profile: any) {
  const key = cacheKeys.musicProfile(userId);
  await setCached(key, profile, cacheTTLs.DAILY);
}

// Video profile cache
export async function getVideoProfile(userId: string) {
  const key = cacheKeys.videoProfile(userId);
  return getCached<any>(key);
}

export async function setVideoProfile(userId: string, profile: any) {
  const key = cacheKeys.videoProfile(userId);
  await setCached(key, profile, cacheTTLs.DAILY);
}
