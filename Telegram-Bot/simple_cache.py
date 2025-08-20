from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Tuple
import asyncio
from collections import defaultdict


class SimpleCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self):
        self.data: Dict[str, Dict[str, Any]] = {}
        self.rate_limits = defaultdict(lambda: {'minute': 0, 'daily': 0, 'last_reset': datetime.now()})
        self.lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self.lock:
            if key in self.data:
                item = self.data[key]
                if item['expires_at'] > datetime.now():
                    return item['value']
                else:
                    del self.data[key]
            return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set value in cache with TTL"""
        async with self.lock:
            self.data[key] = {
                'value': value,
                'expires_at': datetime.now() + timedelta(seconds=ttl_seconds)
            }
    
    async def delete(self, key: str):
        """Delete key from cache"""
        async with self.lock:
            if key in self.data:
                del self.data[key]
    
    async def check_rate_limit(self, user_id: int, daily_limit: int = 100, minute_limit: int = 5) -> Tuple[bool, Optional[str], Dict]:
        """Check rate limits for user"""
        async with self.lock:
            now = datetime.now()
            user_limits = self.rate_limits[user_id]
            
            # Reset counters if needed
            if user_limits['last_reset'].date() < now.date():
                user_limits['daily'] = 0
                user_limits['last_reset'] = now
            
            if (now - user_limits['last_reset']).seconds >= 60:
                user_limits['minute'] = 0
            
            # Check limits
            if user_limits['minute'] >= minute_limit:
                return False, "Please wait a minute before sending more messages.", {
                    'daily_used': user_limits['daily'],
                    'minute_used': user_limits['minute']
                }
            
            if user_limits['daily'] >= daily_limit:
                return False, f"Daily limit of {daily_limit} messages reached.", {
                    'daily_used': user_limits['daily'],
                    'daily_limit': daily_limit
                }
            
            # Increment counters
            user_limits['minute'] += 1
            user_limits['daily'] += 1
            user_limits['last_reset'] = now
            
            return True, None, {
                'daily_used': user_limits['daily'],
                'daily_remaining': daily_limit - user_limits['daily'],
                'minute_used': user_limits['minute']
            }
    
    async def cleanup_expired(self):
        """Remove expired entries"""
        async with self.lock:
            now = datetime.now()
            expired_keys = [k for k, v in self.data.items() if v['expires_at'] <= now]
            for key in expired_keys:
                del self.data[key]