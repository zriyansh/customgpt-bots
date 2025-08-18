import asyncio
import time
from typing import Dict, Optional, Tuple
import redis.asyncio as redis
from datetime import datetime, timedelta
import json
import structlog

logger = structlog.get_logger()


class RateLimiter:
    def __init__(self, redis_client: redis.Redis, 
                 daily_limit: int = 100, 
                 minute_limit: int = 5):
        self.redis = redis_client
        self.daily_limit = daily_limit
        self.minute_limit = minute_limit
        
    async def check_rate_limit(self, user_id: int) -> Tuple[bool, Optional[str], Dict]:
        """
        Check if user has exceeded rate limits
        Returns: (is_allowed, error_message, stats)
        """
        now = datetime.now()
        
        # Keys for rate limiting
        daily_key = f"rate:daily:{user_id}:{now.strftime('%Y%m%d')}"
        minute_key = f"rate:minute:{user_id}:{now.strftime('%Y%m%d%H%M')}"
        
        try:
            # Get current counts
            daily_count = await self.redis.get(daily_key)
            minute_count = await self.redis.get(minute_key)
            
            daily_count = int(daily_count) if daily_count else 0
            minute_count = int(minute_count) if minute_count else 0
            
            # Check minute limit
            if minute_count >= self.minute_limit:
                remaining_seconds = 60 - now.second
                return False, f"Rate limit exceeded. Please wait {remaining_seconds} seconds.", {
                    'daily_used': daily_count,
                    'daily_limit': self.daily_limit,
                    'minute_used': minute_count,
                    'minute_limit': self.minute_limit
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
            await pipe.execute()
            
            return True, None, {
                'daily_used': daily_count + 1,
                'daily_limit': self.daily_limit,
                'daily_remaining': self.daily_limit - (daily_count + 1),
                'minute_used': minute_count + 1,
                'minute_limit': self.minute_limit,
                'minute_remaining': self.minute_limit - (minute_count + 1)
            }
            
        except Exception as e:
            logger.error("rate_limit_error", user_id=user_id, error=str(e))
            # In case of Redis error, allow the request but log it
            return True, None, {}
    
    async def get_user_stats(self, user_id: int) -> Dict:
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
            daily_count = await self.redis.get(daily_key)
            stats['daily'] = {
                'used': int(daily_count) if daily_count else 0,
                'limit': self.daily_limit,
                'remaining': self.daily_limit - (int(daily_count) if daily_count else 0)
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
                'average_per_day': weekly_total / 7
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
                'average_per_day': monthly_total / 30
            }
            
            # Store user activity
            await self._record_user_activity(user_id)
            
        except Exception as e:
            logger.error("stats_error", user_id=user_id, error=str(e))
            
        return stats
    
    async def _record_user_activity(self, user_id: int):
        """Record user activity for analytics"""
        try:
            # Track unique users
            today = datetime.now().strftime('%Y%m%d')
            await self.redis.sadd(f"users:active:{today}", user_id)
            await self.redis.expire(f"users:active:{today}", 86400 * 7)  # Keep for 7 days
            
            # Track user last seen
            await self.redis.hset("users:last_seen", str(user_id), int(time.time()))
            
        except Exception as e:
            logger.error("activity_recording_error", user_id=user_id, error=str(e))
    
    async def reset_user_limits(self, user_id: int, limit_type: str = 'daily'):
        """Reset user limits (admin function)"""
        now = datetime.now()
        
        if limit_type == 'daily':
            key = f"rate:daily:{user_id}:{now.strftime('%Y%m%d')}"
            await self.redis.delete(key)
        elif limit_type == 'minute':
            key = f"rate:minute:{user_id}:{now.strftime('%Y%m%d%H%M')}"
            await self.redis.delete(key)
        
        logger.info("limits_reset", user_id=user_id, limit_type=limit_type)