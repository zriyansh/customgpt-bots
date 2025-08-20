"""
Analytics tracking for WhatsApp bot
"""

import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import structlog

logger = structlog.get_logger()


class Analytics:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self.redis = None
        
        # In-memory storage as fallback
        self.memory_stats = defaultdict(lambda: {
            'response_times': [],
            'responses_success': 0,
            'responses_failure': 0,
            'total_messages': 0
        })
        self.message_log = []
        
        if redis_url:
            try:
                import redis.asyncio as redis
                self.redis_available = True
            except ImportError:
                logger.warning("Redis not available for analytics, using in-memory storage")
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
                logger.info("Redis connected for analytics")
            except Exception as e:
                logger.error("Redis connection failed for analytics", error=str(e))
                self.redis_available = False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
    
    async def log_message(self, user_id: str, message: str, 
                         message_type: str = 'user'):
        """Log a message for analytics"""
        timestamp = datetime.utcnow()
        
        # Create log entry
        log_entry = {
            'user_id': user_id,
            'message': message[:100],  # Truncate for privacy
            'message_type': message_type,
            'timestamp': timestamp.isoformat(),
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'word_count': len(message.split())
        }
        
        try:
            if self.redis_available and self.redis:
                # Store in Redis
                daily_key = f"analytics:messages:{timestamp.strftime('%Y%m%d')}"
                await self.redis.lpush(daily_key, json.dumps(log_entry))
                await self.redis.expire(daily_key, 86400 * 30)  # Keep for 30 days
                
                # Update counters
                await self._update_redis_counters(user_id, timestamp)
            else:
                # Store in memory
                self.message_log.append(log_entry)
                # Keep only last 1000 messages in memory
                if len(self.message_log) > 1000:
                    self.message_log = self.message_log[-1000:]
                
                # Update memory counters
                self._update_memory_counters(user_id, timestamp)
                
        except Exception as e:
            logger.error("analytics_log_error", error=str(e))
    
    async def log_response(self, user_id: str, success: bool, 
                          response_time: Optional[float] = None):
        """Log bot response metrics"""
        timestamp = datetime.utcnow()
        
        try:
            if self.redis_available and self.redis:
                # Update success counter
                success_key = f"analytics:responses:{timestamp.strftime('%Y%m%d')}:{'success' if success else 'failure'}"
                await self.redis.incr(success_key)
                await self.redis.expire(success_key, 86400 * 30)
                
                # Store response time
                if response_time:
                    rt_key = f"analytics:response_times:{timestamp.strftime('%Y%m%d')}"
                    await self.redis.lpush(rt_key, str(response_time))
                    await self.redis.expire(rt_key, 86400 * 7)  # Keep for 7 days
            else:
                # Update memory stats
                date_key = timestamp.strftime('%Y%m%d')
                status_key = 'success' if success else 'failure'
                self.memory_stats[date_key][f'responses_{status_key}'] += 1
                
                if response_time:
                    self.memory_stats[date_key]['response_times'].append(response_time)
                    
        except Exception as e:
            logger.error("analytics_response_error", error=str(e))
    
    async def log_error(self, user_id: str, error_message: str):
        """Log error for analytics"""
        timestamp = datetime.utcnow()
        
        error_entry = {
            'user_id': user_id,
            'error': error_message[:200],
            'timestamp': timestamp.isoformat()
        }
        
        try:
            if self.redis_available and self.redis:
                error_key = f"analytics:errors:{timestamp.strftime('%Y%m%d')}"
                await self.redis.lpush(error_key, json.dumps(error_entry))
                await self.redis.expire(error_key, 86400 * 7)  # Keep for 7 days
            else:
                # Just log to logger in memory mode
                logger.error("user_error", **error_entry)
                
        except Exception as e:
            logger.error("analytics_error_log_error", error=str(e))
    
    async def get_user_stats(self, user_id: str) -> Dict:
        """Get detailed statistics for a user"""
        stats = {
            'user_id': user_id,
            'messages_today': 0,
            'messages_this_week': 0,
            'messages_this_month': 0,
            'most_active_hour': None,
            'average_message_length': 0,
            'first_seen': None,
            'last_seen': None
        }
        
        try:
            now = datetime.utcnow()
            
            if self.redis_available and self.redis:
                # Get message counts
                for i in range(30):  # Last 30 days
                    date = now - timedelta(days=i)
                    count_key = f"analytics:user:{user_id}:{date.strftime('%Y%m%d')}:messages"
                    count = await self.redis.get(count_key)
                    if count:
                        count = int(count)
                        if i == 0:
                            stats['messages_today'] = count
                        if i < 7:
                            stats['messages_this_week'] += count
                        stats['messages_this_month'] += count
                
                # Get activity patterns
                hour_counts = defaultdict(int)
                for i in range(7):  # Last 7 days
                    date = now - timedelta(days=i)
                    for hour in range(24):
                        hour_key = f"analytics:user:{user_id}:{date.strftime('%Y%m%d')}:hour:{hour}"
                        count = await self.redis.get(hour_key)
                        if count:
                            hour_counts[hour] += int(count)
                
                if hour_counts:
                    stats['most_active_hour'] = max(hour_counts, key=hour_counts.get)
                
                # Get first/last seen
                first_key = f"analytics:user:{user_id}:first_seen"
                last_key = f"analytics:user:{user_id}:last_seen"
                stats['first_seen'] = await self.redis.get(first_key)
                stats['last_seen'] = await self.redis.get(last_key)
            else:
                # Use memory stats
                for log in self.message_log:
                    if log['user_id'] == user_id:
                        log_date = datetime.fromisoformat(log['timestamp'])
                        days_ago = (now - log_date).days
                        
                        if days_ago == 0:
                            stats['messages_today'] += 1
                        if days_ago < 7:
                            stats['messages_this_week'] += 1
                        if days_ago < 30:
                            stats['messages_this_month'] += 1
                
        except Exception as e:
            logger.error("user_stats_error", error=str(e))
            
        return stats
    
    async def get_global_stats(self) -> Dict:
        """Get global bot statistics"""
        stats = {
            'total_users': 0,
            'active_users_today': 0,
            'active_users_week': 0,
            'messages_today': 0,
            'messages_week': 0,
            'success_rate_today': 0,
            'average_response_time': 0,
            'popular_hours': [],
            'error_count_today': 0
        }
        
        try:
            now = datetime.utcnow()
            
            if self.redis_available and self.redis:
                # Get user counts
                users_today = await self.redis.smembers(f"analytics:active_users:{now.strftime('%Y%m%d')}")
                stats['active_users_today'] = len(users_today)
                
                # Weekly active users
                weekly_users = set()
                for i in range(7):
                    date = now - timedelta(days=i)
                    daily_users = await self.redis.smembers(f"analytics:active_users:{date.strftime('%Y%m%d')}")
                    weekly_users.update(daily_users)
                stats['active_users_week'] = len(weekly_users)
                
                # Message counts
                for i in range(7):
                    date = now - timedelta(days=i)
                    messages_key = f"analytics:messages:{date.strftime('%Y%m%d')}"
                    count = await self.redis.llen(messages_key)
                    if i == 0:
                        stats['messages_today'] = count
                    stats['messages_week'] += count
                
                # Success rate
                success_key = f"analytics:responses:{now.strftime('%Y%m%d')}:success"
                failure_key = f"analytics:responses:{now.strftime('%Y%m%d')}:failure"
                success_count = int(await self.redis.get(success_key) or 0)
                failure_count = int(await self.redis.get(failure_key) or 0)
                total_responses = success_count + failure_count
                if total_responses > 0:
                    stats['success_rate_today'] = round(success_count / total_responses * 100, 2)
                
                # Average response time
                rt_key = f"analytics:response_times:{now.strftime('%Y%m%d')}"
                response_times = await self.redis.lrange(rt_key, 0, -1)
                if response_times:
                    times = [float(t) for t in response_times]
                    stats['average_response_time'] = round(sum(times) / len(times), 2)
                
                # Error count
                error_key = f"analytics:errors:{now.strftime('%Y%m%d')}"
                stats['error_count_today'] = await self.redis.llen(error_key)
            else:
                # Use memory stats
                unique_users = set()
                for log in self.message_log:
                    unique_users.add(log['user_id'])
                    log_date = datetime.fromisoformat(log['timestamp'])
                    days_ago = (now - log_date).days
                    
                    if days_ago == 0:
                        stats['messages_today'] += 1
                    if days_ago < 7:
                        stats['messages_week'] += 1
                
                stats['total_users'] = len(unique_users)
                
        except Exception as e:
            logger.error("global_stats_error", error=str(e))
            
        return stats
    
    async def _update_redis_counters(self, user_id: str, timestamp: datetime):
        """Update Redis counters"""
        date_str = timestamp.strftime('%Y%m%d')
        
        # Update daily active users
        await self.redis.sadd(f"analytics:active_users:{date_str}", user_id)
        await self.redis.expire(f"analytics:active_users:{date_str}", 86400 * 30)
        
        # Update user message count
        user_count_key = f"analytics:user:{user_id}:{date_str}:messages"
        await self.redis.incr(user_count_key)
        await self.redis.expire(user_count_key, 86400 * 30)
        
        # Update hourly count
        hour_key = f"analytics:user:{user_id}:{date_str}:hour:{timestamp.hour}"
        await self.redis.incr(hour_key)
        await self.redis.expire(hour_key, 86400 * 7)
        
        # Update first/last seen
        first_key = f"analytics:user:{user_id}:first_seen"
        last_key = f"analytics:user:{user_id}:last_seen"
        
        if not await self.redis.exists(first_key):
            await self.redis.set(first_key, timestamp.isoformat())
        await self.redis.set(last_key, timestamp.isoformat())
    
    def _update_memory_counters(self, user_id: str, timestamp: datetime):
        """Update in-memory counters"""
        date_str = timestamp.strftime('%Y%m%d')
        if date_str not in self.memory_stats:
            self.memory_stats[date_str] = {
                'response_times': [],
                'responses_success': 0,
                'responses_failure': 0,
                'total_messages': 0
            }
        self.memory_stats[date_str]['total_messages'] += 1
        # Store user-specific stats separately if needed
        self.memory_stats[date_str][f'user_{user_id}_messages'] = self.memory_stats[date_str].get(f'user_{user_id}_messages', 0) + 1
        self.memory_stats[date_str][f'hour_{timestamp.hour}'] = self.memory_stats[date_str].get(f'hour_{timestamp.hour}', 0) + 1