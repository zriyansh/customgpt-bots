"""
Rate Limiter for CustomGPT Slack Bot
"""

import time
import asyncio
import logging
from typing import Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from config import Config

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting implementation with Redis support"""
    
    def __init__(self):
        self.local_storage: Dict[str, list] = defaultdict(list)
        self.redis_client: Optional[redis.Redis] = None
        
        if REDIS_AVAILABLE and Config.REDIS_URL:
            asyncio.create_task(self._init_redis())
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                Config.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis connected for rate limiting")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {str(e)}. Using local storage.")
            self.redis_client = None
    
    async def check_rate_limit(self, user_id: str, channel_id: str) -> bool:
        """
        Check if a user/channel has exceeded rate limits
        
        Returns:
            bool: True if request is allowed, False if rate limited
        """
        current_time = time.time()
        
        # Check user rate limit
        user_key = f"user:{user_id}"
        if not await self._check_limit(
            user_key,
            current_time,
            Config.RATE_LIMIT_PER_USER,
            Config.RATE_LIMIT_WINDOW_USER
        ):
            logger.warning(f"User {user_id} exceeded rate limit")
            return False
        
        # Check channel rate limit
        channel_key = f"channel:{channel_id}"
        if not await self._check_limit(
            channel_key,
            current_time,
            Config.RATE_LIMIT_PER_CHANNEL,
            Config.RATE_LIMIT_WINDOW_CHANNEL
        ):
            logger.warning(f"Channel {channel_id} exceeded rate limit")
            return False
        
        return True
    
    async def _check_limit(self, key: str, current_time: float, limit: int, window: int) -> bool:
        """Check and update rate limit for a specific key"""
        if self.redis_client:
            return await self._check_limit_redis(key, current_time, limit, window)
        else:
            return self._check_limit_local(key, current_time, limit, window)
    
    async def _check_limit_redis(self, key: str, current_time: float, limit: int, window: int) -> bool:
        """Check rate limit using Redis"""
        try:
            # Use Redis sorted set for sliding window
            pipeline = self.redis_client.pipeline()
            
            # Remove old entries
            min_time = current_time - window
            pipeline.zremrangebyscore(key, 0, min_time)
            
            # Count current entries
            pipeline.zcard(key)
            
            # Add current request
            pipeline.zadd(key, {str(current_time): current_time})
            
            # Set expiry
            pipeline.expire(key, window)
            
            results = await pipeline.execute()
            count = results[1]
            
            return count < limit
        except Exception as e:
            logger.error(f"Redis error in rate limiting: {str(e)}")
            # Fallback to local storage
            return self._check_limit_local(key, current_time, limit, window)
    
    def _check_limit_local(self, key: str, current_time: float, limit: int, window: int) -> bool:
        """Check rate limit using local storage"""
        # Clean old entries
        min_time = current_time - window
        self.local_storage[key] = [
            timestamp for timestamp in self.local_storage[key]
            if timestamp > min_time
        ]
        
        # Check limit
        if len(self.local_storage[key]) >= limit:
            return False
        
        # Add current request
        self.local_storage[key].append(current_time)
        return True
    
    async def get_remaining_quota(self, user_id: str) -> Dict[str, int]:
        """Get remaining quota for a user"""
        current_time = time.time()
        user_key = f"user:{user_id}"
        
        if self.redis_client:
            try:
                # Get count from Redis
                min_time = current_time - Config.RATE_LIMIT_WINDOW_USER
                count = await self.redis_client.zcount(user_key, min_time, current_time)
                remaining = max(0, Config.RATE_LIMIT_PER_USER - count)
            except Exception:
                remaining = self._get_remaining_local(user_key, current_time, Config.RATE_LIMIT_PER_USER, Config.RATE_LIMIT_WINDOW_USER)
        else:
            remaining = self._get_remaining_local(user_key, current_time, Config.RATE_LIMIT_PER_USER, Config.RATE_LIMIT_WINDOW_USER)
        
        return {
            "remaining": remaining,
            "limit": Config.RATE_LIMIT_PER_USER,
            "window": Config.RATE_LIMIT_WINDOW_USER
        }
    
    def _get_remaining_local(self, key: str, current_time: float, limit: int, window: int) -> int:
        """Get remaining quota from local storage"""
        min_time = current_time - window
        valid_requests = [t for t in self.local_storage[key] if t > min_time]
        return max(0, limit - len(valid_requests))
    
    async def reset_limits(self, user_id: Optional[str] = None, channel_id: Optional[str] = None):
        """Reset rate limits for a user or channel"""
        if user_id:
            key = f"user:{user_id}"
            await self._reset_key(key)
            logger.info(f"Reset rate limit for user {user_id}")
        
        if channel_id:
            key = f"channel:{channel_id}"
            await self._reset_key(key)
            logger.info(f"Reset rate limit for channel {channel_id}")
    
    async def _reset_key(self, key: str):
        """Reset a specific rate limit key"""
        if self.redis_client:
            try:
                await self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Failed to reset Redis key {key}: {str(e)}")
        
        if key in self.local_storage:
            del self.local_storage[key]
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()