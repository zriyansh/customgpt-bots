"""
Conversation Manager for CustomGPT Microsoft Teams Bot
"""

import asyncio
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
import json

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from config import Config

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """Represents a conversation context"""
    session_id: str
    channel_id: str
    tenant_id: str
    user_id: str
    thread_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = 0
    context_messages: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'session_id': self.session_id,
            'channel_id': self.channel_id,
            'tenant_id': self.tenant_id,
            'user_id': self.user_id,
            'thread_id': self.thread_id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'message_count': self.message_count,
            'context_messages': self.context_messages,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        return cls(**data)

class ConversationManager:
    """Manages conversation contexts and history"""
    
    def __init__(self):
        self.local_storage: Dict[str, ConversationContext] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        if REDIS_AVAILABLE and Config.REDIS_URL:
            asyncio.create_task(self._init_redis())
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_conversations())
    
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
            logger.info("Redis connected for conversation management")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {str(e)}. Using local storage.")
            self.redis_client = None
    
    def _get_conversation_key(
        self,
        channel_id: str,
        user_id: str,
        thread_id: Optional[str] = None
    ) -> str:
        """Generate a unique key for a conversation"""
        if thread_id:
            return f"conv:{channel_id}:{thread_id}:{user_id}"
        return f"conv:{channel_id}:{user_id}"
    
    async def get_or_create_conversation(
        self,
        channel_id: str,
        tenant_id: str,
        user_id: str,
        thread_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationContext:
        """Get existing conversation or create a new one"""
        key = self._get_conversation_key(channel_id, user_id, thread_id)
        
        # Try to get existing conversation
        context = await self._get_conversation(key)
        
        if context:
            # Check if conversation has expired
            if self._is_expired(context):
                logger.info(f"Conversation {key} has expired, creating new one")
                await self._delete_conversation(key)
                context = None
            else:
                # Update last activity
                context.last_activity = datetime.now(timezone.utc)
                await self._save_conversation(key, context)
                return context
        
        # Create new conversation
        if not context:
            context = ConversationContext(
                session_id=session_id or "",
                channel_id=channel_id,
                tenant_id=tenant_id,
                user_id=user_id,
                thread_id=thread_id,
                metadata=metadata or {}
            )
            await self._save_conversation(key, context)
            logger.info(f"Created new conversation: {key}")
        
        return context
    
    async def update_session_id(
        self,
        channel_id: str,
        user_id: str,
        session_id: str,
        thread_id: Optional[str] = None
    ):
        """Update the session ID for a conversation"""
        key = self._get_conversation_key(channel_id, user_id, thread_id)
        context = await self._get_conversation(key)
        
        if context:
            context.session_id = session_id
            context.last_activity = datetime.now(timezone.utc)
            await self._save_conversation(key, context)
            logger.info(f"Updated session ID for conversation {key}")
    
    async def add_message_to_context(
        self,
        channel_id: str,
        user_id: str,
        role: str,
        content: str,
        thread_id: Optional[str] = None
    ):
        """Add a message to conversation context"""
        key = self._get_conversation_key(channel_id, user_id, thread_id)
        context = await self._get_conversation(key)
        
        if context:
            # Add message to context
            context.context_messages.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Trim context if it exceeds max messages
            if len(context.context_messages) > Config.MAX_CONTEXT_MESSAGES * 2:
                # Keep only the most recent messages
                context.context_messages = context.context_messages[-Config.MAX_CONTEXT_MESSAGES:]
            
            context.message_count += 1
            context.last_activity = datetime.now(timezone.utc)
            
            await self._save_conversation(key, context)
    
    async def get_context_messages(
        self,
        channel_id: str,
        user_id: str,
        thread_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Get context messages for a conversation"""
        key = self._get_conversation_key(channel_id, user_id, thread_id)
        context = await self._get_conversation(key)
        
        if not context:
            return []
        
        messages = context.context_messages
        if limit:
            messages = messages[-limit:]
        
        # Format for OpenAI API
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return formatted_messages
    
    async def get_conversation_info(
        self,
        channel_id: str,
        user_id: str,
        thread_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get conversation information"""
        key = self._get_conversation_key(channel_id, user_id, thread_id)
        context = await self._get_conversation(key)
        
        if not context:
            return None
        
        return {
            "session_id": context.session_id,
            "message_count": context.message_count,
            "created_at": context.created_at.isoformat(),
            "last_activity": context.last_activity.isoformat(),
            "is_expired": self._is_expired(context),
            "metadata": context.metadata
        }
    
    async def clear_conversation(
        self,
        channel_id: str,
        user_id: str,
        thread_id: Optional[str] = None
    ):
        """Clear a conversation"""
        key = self._get_conversation_key(channel_id, user_id, thread_id)
        await self._delete_conversation(key)
        logger.info(f"Cleared conversation: {key}")
    
    async def _get_conversation(self, key: str) -> Optional[ConversationContext]:
        """Get conversation from storage"""
        if self.redis_client:
            try:
                data = await self.redis_client.get(key)
                if data:
                    return ConversationContext.from_dict(json.loads(data))
            except Exception as e:
                logger.error(f"Redis error getting conversation: {str(e)}")
        
        # Fallback to local storage
        return self.local_storage.get(key)
    
    async def _save_conversation(self, key: str, context: ConversationContext):
        """Save conversation to storage"""
        if self.redis_client:
            try:
                data = json.dumps(context.to_dict())
                await self.redis_client.setex(
                    key,
                    Config.CONVERSATION_TIMEOUT,
                    data
                )
                return
            except Exception as e:
                logger.error(f"Redis error saving conversation: {str(e)}")
        
        # Fallback to local storage
        self.local_storage[key] = context
    
    async def _delete_conversation(self, key: str):
        """Delete conversation from storage"""
        if self.redis_client:
            try:
                await self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Redis error deleting conversation: {str(e)}")
        
        # Also delete from local storage
        if key in self.local_storage:
            del self.local_storage[key]
    
    def _is_expired(self, context: ConversationContext) -> bool:
        """Check if conversation has expired"""
        expiry_time = context.last_activity + timedelta(seconds=Config.CONVERSATION_TIMEOUT)
        return datetime.now(timezone.utc) > expiry_time
    
    async def _cleanup_expired_conversations(self):
        """Periodically clean up expired conversations"""
        while True:
            try:
                # Wait for cleanup interval (1 hour)
                await asyncio.sleep(3600)
                
                # Clean up local storage
                expired_keys = []
                for key, context in self.local_storage.items():
                    if self._is_expired(context):
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.local_storage[key]
                
                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired conversations from local storage")
                
                # Redis handles expiration automatically via TTL
                
            except Exception as e:
                logger.error(f"Error in conversation cleanup: {str(e)}")
    
    async def get_active_conversations_count(self, tenant_id: Optional[str] = None) -> int:
        """Get count of active conversations"""
        count = 0
        
        if self.redis_client:
            try:
                if tenant_id:
                    # Count conversations for specific tenant
                    cursor = b'0'
                    pattern = f"conv:*:*"
                    while cursor:
                        cursor, keys = await self.redis_client.scan(
                            cursor,
                            match=pattern,
                            count=100
                        )
                        for key in keys:
                            data = await self.redis_client.get(key)
                            if data:
                                context = ConversationContext.from_dict(json.loads(data))
                                if context.tenant_id == tenant_id and not self._is_expired(context):
                                    count += 1
                else:
                    # Count all conversations
                    cursor = b'0'
                    pattern = "conv:*"
                    while cursor:
                        cursor, keys = await self.redis_client.scan(
                            cursor,
                            match=pattern,
                            count=100
                        )
                        count += len(keys)
                return count
            except Exception as e:
                logger.error(f"Redis error counting conversations: {str(e)}")
        
        # Fallback to local storage
        if tenant_id:
            count = sum(
                1 for context in self.local_storage.values()
                if context.tenant_id == tenant_id and not self._is_expired(context)
            )
        else:
            count = sum(1 for context in self.local_storage.values() if not self._is_expired(context))
        
        return count
    
    async def close(self):
        """Cleanup resources"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        if self.redis_client:
            await self.redis_client.close()