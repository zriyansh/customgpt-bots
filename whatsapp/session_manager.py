"""
Session management for WhatsApp bot
"""

import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import structlog
from cachetools import TTLCache

logger = structlog.get_logger()


class SessionManager:
    def __init__(self, redis_url: Optional[str] = None, 
                 session_timeout_minutes: int = 30):
        self.redis_url = redis_url
        self.redis = None
        self.session_timeout = session_timeout_minutes * 60  # Convert to seconds
        
        # In-memory cache as fallback
        self.memory_sessions = TTLCache(maxsize=1000, ttl=self.session_timeout)
        
        if redis_url:
            try:
                import redis.asyncio as redis
                self.redis_available = True
            except ImportError:
                logger.warning("Redis not available for sessions, using in-memory cache")
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
                logger.info("Redis connected for session management")
            except Exception as e:
                logger.error("Redis connection failed for sessions", error=str(e))
                self.redis_available = False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
    
    async def create_session(self, user_id: str, session_id: str, 
                           language: str = 'en') -> Dict:
        """Create a new session for a user"""
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'language': language,
            'created_at': datetime.utcnow().isoformat(),
            'last_active': datetime.utcnow().isoformat(),
            'message_count': 0,
            'context': []  # Store recent messages for context
        }
        
        key = f"session:{user_id}"
        
        try:
            if self.redis_available and self.redis:
                await self.redis.setex(
                    key,
                    self.session_timeout,
                    json.dumps(session_data)
                )
            else:
                self.memory_sessions[key] = session_data
            
            logger.info("session_created", user_id=user_id, session_id=session_id)
            return session_data
            
        except Exception as e:
            logger.error("session_creation_error", error=str(e))
            # Fallback to memory
            self.memory_sessions[key] = session_data
            return session_data
    
    async def get_session(self, user_id: str) -> Optional[Dict]:
        """Get session data for a user"""
        key = f"session:{user_id}"
        
        try:
            if self.redis_available and self.redis:
                session_json = await self.redis.get(key)
                if session_json:
                    session_data = json.loads(session_json)
                    # Update last active time
                    session_data['last_active'] = datetime.utcnow().isoformat()
                    # Extend TTL
                    await self.redis.expire(key, self.session_timeout)
                    return session_data
            else:
                session_data = self.memory_sessions.get(key)
                if session_data:
                    # Update last active time
                    session_data['last_active'] = datetime.utcnow().isoformat()
                    return session_data
            
            return None
            
        except Exception as e:
            logger.error("session_get_error", error=str(e))
            # Fallback to memory
            return self.memory_sessions.get(key)
    
    async def update_session(self, user_id: str, updates: Dict) -> bool:
        """Update session data"""
        session = await self.get_session(user_id)
        if not session:
            return False
        
        # Apply updates
        session.update(updates)
        session['last_active'] = datetime.utcnow().isoformat()
        
        key = f"session:{user_id}"
        
        try:
            if self.redis_available and self.redis:
                await self.redis.setex(
                    key,
                    self.session_timeout,
                    json.dumps(session)
                )
            else:
                self.memory_sessions[key] = session
            
            return True
            
        except Exception as e:
            logger.error("session_update_error", error=str(e))
            return False
    
    async def add_message_to_context(self, user_id: str, role: str, 
                                   content: str, max_context: int = 10):
        """Add a message to session context"""
        session = await self.get_session(user_id)
        if not session:
            return
        
        # Add message to context
        context_message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        context = session.get('context', [])
        context.append(context_message)
        
        # Keep only last N messages
        if len(context) > max_context:
            context = context[-max_context:]
        
        # Update session
        await self.update_session(user_id, {
            'context': context,
            'message_count': session.get('message_count', 0) + 1
        })
    
    async def get_context(self, user_id: str) -> List[Dict]:
        """Get conversation context for a user"""
        session = await self.get_session(user_id)
        if session:
            return session.get('context', [])
        return []
    
    async def clear_session(self, user_id: str) -> bool:
        """Clear a user's session"""
        key = f"session:{user_id}"
        
        try:
            if self.redis_available and self.redis:
                result = await self.redis.delete(key)
                success = result > 0
            else:
                success = key in self.memory_sessions
                if success:
                    del self.memory_sessions[key]
            
            if success:
                logger.info("session_cleared", user_id=user_id)
            
            return success
            
        except Exception as e:
            logger.error("session_clear_error", error=str(e))
            return False
    
    async def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        try:
            if self.redis_available and self.redis:
                keys = await self.redis.keys("session:*")
                return len(keys)
            else:
                return len(self.memory_sessions)
        except Exception as e:
            logger.error("active_sessions_count_error", error=str(e))
            return 0
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions (for Redis)"""
        if not self.redis_available or not self.redis:
            # Memory cache handles expiry automatically
            return
        
        try:
            # Redis also handles expiry automatically with TTL
            # This method is here for any additional cleanup if needed
            logger.info("session_cleanup_completed")
        except Exception as e:
            logger.error("session_cleanup_error", error=str(e))
    
    async def set_language(self, user_id: str, language: str) -> bool:
        """Set user's preferred language"""
        return await self.update_session(user_id, {'language': language})
    
    async def get_user_language(self, user_id: str) -> str:
        """Get user's preferred language"""
        session = await self.get_session(user_id)
        if session:
            return session.get('language', 'en')
        return 'en'