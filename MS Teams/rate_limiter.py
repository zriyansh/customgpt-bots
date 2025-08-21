"""
Rate Limiter for CustomGPT Microsoft Teams Bot
"""

import time
import asyncio
import logging
from typing import Dict, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from enum import Enum

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from config import Config

logger = logging.getLogger(__name__)

class RateLimitScope(Enum):
    """Rate limit scopes"""
    USER = "user"
    CHANNEL = "channel"
    TENANT = "tenant"
    API = "api"

class RateLimiter:
    """Rate limiting implementation with Redis support and API limits integration"""
    
    def __init__(self, customgpt_client=None):
        self.local_storage: Dict[str, list] = defaultdict(list)
        self.redis_client: Optional[redis.Redis] = None
        self.customgpt_client = customgpt_client
        self.api_limits_cache = {}
        self.api_limits_timestamp = None
        self.api_limits_ttl = 300  # 5 minutes cache
        
        if REDIS_AVAILABLE and Config.REDIS_URL:
            asyncio.create_task(self._init_redis())
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        try:
            if Config.REDIS_SSL:
                self.redis_client = redis.from_url(
                    Config.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    ssl_cert_reqs="none"
                )
            else:
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
    
    async def check_rate_limit(
        self,
        user_id: str,
        channel_id: str,
        tenant_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a request has exceeded rate limits
        
        Returns:
            Tuple[bool, Optional[str]]: (is_allowed, error_message)
        """
        current_time = time.time()
        
        # Check API limits first
        api_check = await self._check_api_limits()
        if not api_check[0]:
            return api_check
        
        # Check user rate limit
        user_key = f"{RateLimitScope.USER.value}:{tenant_id}:{user_id}"
        if not await self._check_limit(
            user_key,
            current_time,
            Config.RATE_LIMIT_PER_USER,
            Config.RATE_LIMIT_WINDOW_USER
        ):
            remaining = await self._get_reset_time(user_key, Config.RATE_LIMIT_WINDOW_USER)
            logger.warning(f"User {user_id} exceeded rate limit")
            return False, f"You've exceeded the rate limit. Please try again in {remaining} seconds."
        
        # Check channel rate limit
        channel_key = f"{RateLimitScope.CHANNEL.value}:{tenant_id}:{channel_id}"
        if not await self._check_limit(
            channel_key,
            current_time,
            Config.RATE_LIMIT_PER_CHANNEL,
            Config.RATE_LIMIT_WINDOW_CHANNEL
        ):
            remaining = await self._get_reset_time(channel_key, Config.RATE_LIMIT_WINDOW_CHANNEL)
            logger.warning(f"Channel {channel_id} exceeded rate limit")
            return False, f"This channel has exceeded the rate limit. Please try again in {remaining} seconds."
        
        # Check tenant rate limit
        tenant_key = f"{RateLimitScope.TENANT.value}:{tenant_id}"
        if not await self._check_limit(
            tenant_key,
            current_time,
            Config.RATE_LIMIT_PER_TENANT,
            Config.RATE_LIMIT_WINDOW_TENANT
        ):
            remaining = await self._get_reset_time(tenant_key, Config.RATE_LIMIT_WINDOW_TENANT)
            logger.warning(f"Tenant {tenant_id} exceeded rate limit")
            return False, f"Your organization has exceeded the rate limit. Please try again in {remaining} seconds."
        
        return True, None
    
    async def _check_api_limits(self) -> Tuple[bool, Optional[str]]:
        """Check CustomGPT API usage limits"""
        if not self.customgpt_client:
            return True, None
        
        try:
            # Get cached or fresh API limits
            now = datetime.now(timezone.utc)
            if self.api_limits_timestamp and self.api_limits_cache:
                cache_age = (now - self.api_limits_timestamp).total_seconds()
                if cache_age < self.api_limits_ttl:
                    limits = self.api_limits_cache
                else:
                    limits = await self.customgpt_client.get_usage_limits()
                    self.api_limits_cache = limits
                    self.api_limits_timestamp = now
            else:
                limits = await self.customgpt_client.get_usage_limits()
                self.api_limits_cache = limits
                self.api_limits_timestamp = now
            
            # Check query limits
            if 'max_queries' in limits and 'current_queries' in limits:
                remaining_queries = limits['max_queries'] - limits['current_queries']
                if remaining_queries <= 0:
                    return False, "API query limit exceeded. Please upgrade your CustomGPT plan."
                elif remaining_queries < 10:
                    logger.warning(f"Low API queries remaining: {remaining_queries}")
            
            return True, None
        except Exception as e:
            logger.error(f"Error checking API limits: {str(e)}")
            # Don't block on API limit check failures
            return True, None
    
    async def _check_limit(self, key: str, current_time: float, limit: int, window: int) -> bool:
        """Check and update rate limit for a specific key"""
        if self.redis_client:
            return await self._check_limit_redis(key, current_time, limit, window)
        else:
            return self._check_limit_local(key, current_time, limit, window)
    
    async def _check_limit_redis(self, key: str, current_time: float, limit: int, window: int) -> bool:
        """Check rate limit using Redis with sliding window"""
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
            pipeline.expire(key, window + 60)  # Add buffer for safety
            
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
    
    async def _get_reset_time(self, key: str, window: int) -> int:
        """Get seconds until rate limit resets"""
        current_time = time.time()
        
        if self.redis_client:
            try:
                # Get oldest entry
                oldest = await self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest:
                    oldest_time = oldest[0][1]
                    reset_time = oldest_time + window
                    return max(1, int(reset_time - current_time))
            except Exception:
                pass
        
        # Fallback to local storage
        if key in self.local_storage and self.local_storage[key]:
            oldest_time = min(self.local_storage[key])
            reset_time = oldest_time + window
            return max(1, int(reset_time - current_time))
        
        return 60  # Default to 1 minute
    
    async def get_remaining_quota(
        self,
        user_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get remaining quota for a user"""
        current_time = time.time()
        user_key = f"{RateLimitScope.USER.value}:{tenant_id}:{user_id}"
        
        if self.redis_client:
            try:
                # Get count from Redis
                min_time = current_time - Config.RATE_LIMIT_WINDOW_USER
                count = await self.redis_client.zcount(user_key, min_time, current_time)
                remaining = max(0, Config.RATE_LIMIT_PER_USER - count)
            except Exception:
                remaining = self._get_remaining_local(
                    user_key,
                    current_time,
                    Config.RATE_LIMIT_PER_USER,
                    Config.RATE_LIMIT_WINDOW_USER
                )
        else:
            remaining = self._get_remaining_local(
                user_key,
                current_time,
                Config.RATE_LIMIT_PER_USER,
                Config.RATE_LIMIT_WINDOW_USER
            )
        
        # Get API limits if available
        api_remaining = None
        if self.api_limits_cache:
            if 'max_queries' in self.api_limits_cache and 'current_queries' in self.api_limits_cache:
                api_remaining = self.api_limits_cache['max_queries'] - self.api_limits_cache['current_queries']
        
        return {
            "user_remaining": remaining,
            "user_limit": Config.RATE_LIMIT_PER_USER,
            "user_window": Config.RATE_LIMIT_WINDOW_USER,
            "api_remaining": api_remaining,
            "api_limit": self.api_limits_cache.get('max_queries') if self.api_limits_cache else None
        }
    
    def _get_remaining_local(self, key: str, current_time: float, limit: int, window: int) -> int:
        """Get remaining quota from local storage"""
        min_time = current_time - window
        valid_requests = [t for t in self.local_storage[key] if t > min_time]
        return max(0, limit - len(valid_requests))
    
    async def reset_limits(
        self,
        user_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ):
        """Reset rate limits for a user, channel, or tenant"""
        if user_id and tenant_id:
            key = f"{RateLimitScope.USER.value}:{tenant_id}:{user_id}"
            await self._reset_key(key)
            logger.info(f"Reset rate limit for user {user_id} in tenant {tenant_id}")
        
        if channel_id and tenant_id:
            key = f"{RateLimitScope.CHANNEL.value}:{tenant_id}:{channel_id}"
            await self._reset_key(key)
            logger.info(f"Reset rate limit for channel {channel_id} in tenant {tenant_id}")
        
        if tenant_id and not user_id and not channel_id:
            key = f"{RateLimitScope.TENANT.value}:{tenant_id}"
            await self._reset_key(key)
            logger.info(f"Reset rate limit for tenant {tenant_id}")
    
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
    
    def get_rate_limit_headers(
        self,
        user_id: str,
        tenant_id: str
    ) -> Dict[str, str]:
        """Get rate limit headers for response"""
        current_time = time.time()
        user_key = f"{RateLimitScope.USER.value}:{tenant_id}:{user_id}"
        
        remaining = self._get_remaining_local(
            user_key,
            current_time,
            Config.RATE_LIMIT_PER_USER,
            Config.RATE_LIMIT_WINDOW_USER
        )
        
        reset_time = int(current_time + Config.RATE_LIMIT_WINDOW_USER)
        
        return {
            "X-RateLimit-Limit": str(Config.RATE_LIMIT_PER_USER),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
            "X-RateLimit-Window": str(Config.RATE_LIMIT_WINDOW_USER)
        }