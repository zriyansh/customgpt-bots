import asyncio
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import redis.asyncio as redis
import json
import structlog

logger = structlog.get_logger()


class ConversationManager:
    """Manages conversation sessions and history for users"""
    
    def __init__(self, redis_client: redis.Redis, 
                 session_timeout_minutes: int = 30,
                 max_history: int = 10):
        self.redis = redis_client
        self.session_timeout = session_timeout_minutes
        self.max_history = max_history
    
    async def get_or_create_session(self, user_id: int) -> Optional[str]:
        """Get existing session or return None if expired"""
        session_key = f"session:{user_id}"
        session_id = await self.redis.get(session_key)
        
        if session_id:
            # Extend session timeout
            await self.redis.expire(session_key, self.session_timeout * 60)
            return session_id.decode('utf-8')
        
        return None
    
    async def save_session(self, user_id: int, session_id: str):
        """Save session ID for a user"""
        session_key = f"session:{user_id}"
        await self.redis.setex(
            session_key, 
            self.session_timeout * 60,
            session_id
        )
        logger.info("session_saved", user_id=user_id, session_id=session_id)
    
    async def clear_session(self, user_id: int):
        """Clear user's session"""
        session_key = f"session:{user_id}"
        await self.redis.delete(session_key)
        
        # Also clear conversation history
        history_key = f"history:{user_id}"
        await self.redis.delete(history_key)
        
        logger.info("session_cleared", user_id=user_id)
    
    async def add_to_history(self, user_id: int, message: Dict):
        """Add message to conversation history"""
        history_key = f"history:{user_id}"
        
        # Get current history
        history = await self.redis.lrange(history_key, 0, -1)
        history = [json.loads(h.decode('utf-8')) for h in history]
        
        # Add new message
        history.append({
            'timestamp': datetime.now().isoformat(),
            'user_message': message.get('user_message'),
            'bot_response': message.get('bot_response'),
            'message_id': message.get('message_id')
        })
        
        # Keep only recent messages
        if len(history) > self.max_history:
            history = history[-self.max_history:]
        
        # Save back to Redis
        await self.redis.delete(history_key)
        for msg in history:
            await self.redis.rpush(history_key, json.dumps(msg))
        
        # Set expiry
        await self.redis.expire(history_key, self.session_timeout * 60)
    
    async def get_history(self, user_id: int) -> List[Dict]:
        """Get conversation history for a user"""
        history_key = f"history:{user_id}"
        history = await self.redis.lrange(history_key, 0, -1)
        
        return [json.loads(h.decode('utf-8')) for h in history]
    
    async def get_context_messages(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get recent messages for context"""
        history = await self.get_history(user_id)
        
        # Get last N messages for context
        recent = history[-limit:] if len(history) > limit else history
        
        # Format for CustomGPT API
        context_messages = []
        for msg in recent:
            if msg.get('user_message'):
                context_messages.append({
                    'role': 'user',
                    'content': msg['user_message']
                })
            if msg.get('bot_response'):
                context_messages.append({
                    'role': 'assistant',
                    'content': msg['bot_response']
                })
        
        return context_messages
    
    async def store_user_preference(self, user_id: int, key: str, value: str):
        """Store user preferences (language, etc.)"""
        pref_key = f"pref:{user_id}:{key}"
        await self.redis.setex(pref_key, 86400 * 30, value)  # 30 days
    
    async def get_user_preference(self, user_id: int, key: str, default: str = None) -> Optional[str]:
        """Get user preference"""
        pref_key = f"pref:{user_id}:{key}"
        value = await self.redis.get(pref_key)
        return value.decode('utf-8') if value else default
    
    async def get_active_users_count(self) -> int:
        """Get count of active users in last 24 hours"""
        today = datetime.now().strftime('%Y%m%d')
        count = await self.redis.scard(f"users:active:{today}")
        return count or 0