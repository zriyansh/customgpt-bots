"""
Rate limiting for WhatsApp bot
"""

import asyncio
import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
import structlog
from cachetools import TTLCache

logger = structlog.get_logger()


class RateLimiter:
    def __init__(self, redis_url: Optional[str] = None, 
                 daily_limit: int = 100, 
                 minute_limit: int = 5,
                 hour_limit: int = 30):
        self.redis_url = redis_url
        self.redis = None
        self.daily_limit = daily_limit
        self.minute_limit = minute_limit
        self.hour_limit = hour_limit
        
        # In-memory cache as fallback
        self.memory_cache = TTLCache(maxsize=10000, ttl=86400)  # 24 hours
        
        if redis_url:
            try:
                import redis.asyncio as redis
                self.redis_available = True
            except ImportError:
                logger.warning("Redis not available, using in-memory cache")
                self.redis_available = False
        else:
            self.redis_available = False
    
    async def initialize(self):
        """Initialize Redis connection if available"""
        if self.redis_available and self.redis_url:
            try:
                import redis.asyncio as redis
                self.redis = await redis.from_url(self.redis_url, decode_responses=True)
                await self.redis.ping()
                logger.info("Redis connected for rate limiting")
            except Exception as e:
                logger.error("Redis connection failed", error=str(e))
                self.redis_available = False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
    
    async def check_connection(self) -> str:
        """Check Redis connection status"""
        if self.redis:
            try:
                await self.redis.ping()
                return "connected"
            except:
                return "disconnected"
        return "not_configured"
    
    async def check_rate_limit(self, user_id: str) -> Tuple[bool, Optional[str], Dict]:
        """
        Check if user has exceeded rate limits
        Returns: (is_allowed, error_message, stats)
        """
        now = datetime.now()
        
        # Keys for rate limiting
        daily_key = f"rate:daily:{user_id}:{now.strftime('%Y%m%d')}"
        minute_key = f"rate:minute:{user_id}:{now.strftime('%Y%m%d%H%M')}"
        hour_key = f"rate:hour:{user_id}:{now.strftime('%Y%m%d%H')}"
        
        try:
            if self.redis_available and self.redis:
                return await self._check_redis_rate_limit(
                    user_id, daily_key, minute_key, hour_key, now
                )
            else:
                return await self._check_memory_rate_limit(
                    user_id, daily_key, minute_key, hour_key, now
                )
        except Exception as e:
            logger.error("rate_limit_error", user_id=user_id, error=str(e))
            # In case of error, allow the request but log it
            return True, None, {}
    
    async def _check_redis_rate_limit(self, user_id: str, daily_key: str, 
                                     minute_key: str, hour_key: str, 
                                     now: datetime) -> Tuple[bool, Optional[str], Dict]:
        """Check rate limit using Redis"""
        # Get current counts
        daily_count = await self.redis.get(daily_key)
        minute_count = await self.redis.get(minute_key)
        hour_count = await self.redis.get(hour_key)
        
        daily_count = int(daily_count) if daily_count else 0
        minute_count = int(minute_count) if minute_count else 0
        hour_count = int(hour_count) if hour_count else 0
        
        # Check minute limit
        if minute_count >= self.minute_limit:
            remaining_seconds = 60 - now.second
            return False, f"Rate limit exceeded. Please wait {remaining_seconds} seconds.", {
                'daily_used': daily_count,
                'daily_limit': self.daily_limit,
                'minute_used': minute_count,
                'minute_limit': self.minute_limit
            }
        
        # Check hourly limit
        if hour_count >= self.hour_limit:
            remaining_minutes = 60 - now.minute
            return False, f"Hourly limit reached. Please wait {remaining_minutes} minutes.", {
                'daily_used': daily_count,
                'daily_limit': self.daily_limit,
                'hourly_used': hour_count,
                'hourly_limit': self.hour_limit
            }
        
        # Check daily limit
        if daily_count >= self.daily_limit:
            reset_time = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0)
            hours_until_reset = (reset_time - now).seconds // 3600
            return False, f"Daily limit reached. Resets in {hours_until_reset} hours.", {
                'daily_used': daily_count,
                'daily_limit': self.daily_limit,
                'reset_in_hours': hours_until_reset
            }
        
        # Increment counters
        pipe = self.redis.pipeline()
        pipe.incr(daily_key)
        pipe.expire(daily_key, 86400)  # 24 hours
        pipe.incr(minute_key)
        pipe.expire(minute_key, 60)  # 1 minute
        pipe.incr(hour_key)
        pipe.expire(hour_key, 3600)  # 1 hour
        await pipe.execute()
        
        return True, None, {
            'daily_used': daily_count + 1,
            'daily_limit': self.daily_limit,
            'daily_remaining': self.daily_limit - (daily_count + 1),
            'minute_used': minute_count + 1,
            'minute_limit': self.minute_limit,
            'minute_remaining': self.minute_limit - (minute_count + 1),
            'hourly_used': hour_count + 1,
            'hourly_limit': self.hour_limit,
            'hourly_remaining': self.hour_limit - (hour_count + 1)
        }
    
    async def _check_memory_rate_limit(self, user_id: str, daily_key: str, 
                                      minute_key: str, hour_key: str, 
                                      now: datetime) -> Tuple[bool, Optional[str], Dict]:
        """Check rate limit using in-memory cache"""
        # Get current counts from memory
        daily_count = self.memory_cache.get(daily_key, 0)
        minute_count = self.memory_cache.get(minute_key, 0)
        hour_count = self.memory_cache.get(hour_key, 0)
        
        # Check minute limit
        if minute_count >= self.minute_limit:
            remaining_seconds = 60 - now.second
            return False, f"Rate limit exceeded. Please wait {remaining_seconds} seconds.", {
                'daily_used': daily_count,
                'daily_limit': self.daily_limit,
                'minute_used': minute_count,
                'minute_limit': self.minute_limit
            }
        
        # Check hourly limit
        if hour_count >= self.hour_limit:
            remaining_minutes = 60 - now.minute
            return False, f"Hourly limit reached. Please wait {remaining_minutes} minutes.", {
                'daily_used': daily_count,
                'daily_limit': self.daily_limit,
                'hourly_used': hour_count,
                'hourly_limit': self.hour_limit
            }
        
        # Check daily limit
        if daily_count >= self.daily_limit:
            reset_time = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0)
            hours_until_reset = (reset_time - now).seconds // 3600
            return False, f"Daily limit reached. Resets in {hours_until_reset} hours.", {
                'daily_used': daily_count,
                'daily_limit': self.daily_limit,
                'reset_in_hours': hours_until_reset
            }
        
        # Increment counters in memory
        self.memory_cache[daily_key] = daily_count + 1
        self.memory_cache[minute_key] = minute_count + 1
        self.memory_cache[hour_key] = hour_count + 1
        
        return True, None, {
            'daily_used': daily_count + 1,
            'daily_limit': self.daily_limit,
            'daily_remaining': self.daily_limit - (daily_count + 1),
            'minute_used': minute_count + 1,
            'minute_limit': self.minute_limit,
            'minute_remaining': self.minute_limit - (minute_count + 1),
            'hourly_used': hour_count + 1,
            'hourly_limit': self.hour_limit,
            'hourly_remaining': self.hour_limit - (hour_count + 1)
        }
    
    async def get_user_stats(self, user_id: str) -> Dict:
        """Get usage statistics for a user"""
        now = datetime.now()
        stats = {
            'user_id': user_id,
            'timestamp': now.isoformat(),
            'daily': {},
            'weekly': {},
            'monthly': {}
        }
        
        try:
            # Daily stats
            daily_key = f"rate:daily:{user_id}:{now.strftime('%Y%m%d')}"
            hour_key = f"rate:hour:{user_id}:{now.strftime('%Y%m%d%H')}"
            
            if self.redis_available and self.redis:
                daily_count = await self.redis.get(daily_key)
                hour_count = await self.redis.get(hour_key)
                
                stats['daily'] = {
                    'used': int(daily_count) if daily_count else 0,
                    'limit': self.daily_limit,
                    'remaining': self.daily_limit - (int(daily_count) if daily_count else 0)
                }
                
                stats['hourly'] = {
                    'used': int(hour_count) if hour_count else 0,
                    'limit': self.hour_limit,
                    'remaining': self.hour_limit - (int(hour_count) if hour_count else 0)
                }
                
                # Weekly stats (last 7 days)
                weekly_total = 0
                for i in range(7):
                    date = now - timedelta(days=i)
                    key = f"rate:daily:{user_id}:{date.strftime('%Y%m%d')}"
                    count = await self.redis.get(key)
                    weekly_total += int(count) if count else 0
                
                stats['weekly'] = {
                    'used': weekly_total,
                    'average_per_day': round(weekly_total / 7, 2)
                }
                
                # Monthly stats (last 30 days)
                monthly_total = 0
                for i in range(30):
                    date = now - timedelta(days=i)
                    key = f"rate:daily:{user_id}:{date.strftime('%Y%m%d')}"
                    count = await self.redis.get(key)
                    monthly_total += int(count) if count else 0
                
                stats['monthly'] = {
                    'used': monthly_total,
                    'average_per_day': round(monthly_total / 30, 2)
                }
            else:
                # Use memory cache
                daily_count = self.memory_cache.get(daily_key, 0)
                hour_count = self.memory_cache.get(hour_key, 0)
                
                stats['daily'] = {
                    'used': daily_count,
                    'limit': self.daily_limit,
                    'remaining': self.daily_limit - daily_count
                }
                
                stats['hourly'] = {
                    'used': hour_count,
                    'limit': self.hour_limit,
                    'remaining': self.hour_limit - hour_count
                }
                
        except Exception as e:
            logger.error("stats_error", user_id=user_id, error=str(e))
            
        return stats
    
    async def reset_user_limits(self, user_id: str, limit_type: str = 'all'):
        """Reset user limits (admin function)"""
        now = datetime.now()
        
        if self.redis_available and self.redis:
            if limit_type in ['daily', 'all']:
                key = f"rate:daily:{user_id}:{now.strftime('%Y%m%d')}"
                await self.redis.delete(key)
            
            if limit_type in ['hour', 'all']:
                key = f"rate:hour:{user_id}:{now.strftime('%Y%m%d%H')}"
                await self.redis.delete(key)
            
            if limit_type in ['minute', 'all']:
                key = f"rate:minute:{user_id}:{now.strftime('%Y%m%d%H%M')}"
                await self.redis.delete(key)
        else:
            # Clear from memory cache
            keys_to_remove = []
            for key in self.memory_cache:
                if key.startswith(f"rate:") and user_id in key:
                    if limit_type == 'all' or limit_type in key:
                        keys_to_remove.append(key)
            
            for key in keys_to_remove:
                self.memory_cache.pop(key, None)
        
        logger.info("limits_reset", user_id=user_id, limit_type=limit_type)