"""
Conversation Manager for CustomGPT Slack Bot
Manages conversation state and context
"""

import time
import logging
from typing import Dict, Optional, List, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import uuid

from config import Config

logger = logging.getLogger(__name__)

class ConversationManager:
    """Manages conversation sessions and context"""
    
    def __init__(self):
        # Map of (user_id, channel_id, thread_ts) -> session_id
        self.conversations: Dict[str, Dict[str, Any]] = {}
        # Map of session_id -> conversation data
        self.session_data: Dict[str, Dict[str, Any]] = {}
        # Map of user_id -> list of session_ids
        self.user_sessions: Dict[str, List[str]] = defaultdict(list)
        # Map of thread_key (channel_id:thread_ts) -> thread participation info
        self.thread_participation: Dict[str, Dict[str, Any]] = {}
    
    def get_or_create_conversation(self, user_id: str, channel_id: str, thread_ts: Optional[str] = None) -> str:
        """
        Get existing conversation session or create new one
        
        Args:
            user_id: Slack user ID
            channel_id: Slack channel ID
            thread_ts: Thread timestamp (for threaded conversations)
        
        Returns:
            session_id: CustomGPT session ID
        """
        # Create conversation key
        conv_key = self._create_conversation_key(user_id, channel_id, thread_ts)
        
        # Check if conversation exists and is not expired
        if conv_key in self.conversations:
            session_info = self.conversations[conv_key]
            if self._is_conversation_valid(session_info):
                # Update last activity
                session_info['last_activity'] = time.time()
                return session_info['session_id']
            else:
                # Clean up expired conversation
                self._remove_conversation(conv_key)
        
        # Create new conversation
        session_id = self._create_session_id()
        session_info = {
            'session_id': session_id,
            'user_id': user_id,
            'channel_id': channel_id,
            'thread_ts': thread_ts,
            'created_at': time.time(),
            'last_activity': time.time(),
            'message_count': 0
        }
        
        # Store conversation
        self.conversations[conv_key] = session_info
        self.session_data[session_id] = {
            'conversation_key': conv_key,
            'context': [],
            'metadata': {}
        }
        self.user_sessions[user_id].append(session_id)
        
        logger.info(f"Created new conversation: {session_id} for user {user_id} in channel {channel_id}")
        return session_id
    
    def add_message_to_context(self, session_id: str, role: str, content: str):
        """Add a message to conversation context"""
        if session_id not in self.session_data:
            logger.warning(f"Session {session_id} not found")
            return
        
        context = self.session_data[session_id]['context']
        context.append({
            'role': role,
            'content': content,
            'timestamp': time.time()
        })
        
        # Limit context size
        if len(context) > Config.MAX_CONTEXT_MESSAGES * 2:
            # Keep system messages and recent messages
            system_messages = [m for m in context if m['role'] == 'system']
            other_messages = [m for m in context if m['role'] != 'system']
            context = system_messages + other_messages[-(Config.MAX_CONTEXT_MESSAGES * 2 - len(system_messages)):]
            self.session_data[session_id]['context'] = context
    
    def get_conversation_context(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation context for API calls"""
        if session_id not in self.session_data:
            return []
        
        context = self.session_data[session_id]['context']
        
        # Format for API
        formatted_context = []
        for message in context[-Config.MAX_CONTEXT_MESSAGES:]:
            formatted_context.append({
                'role': message['role'],
                'content': message['content']
            })
        
        return formatted_context
    
    def get_conversation_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation information"""
        if session_id not in self.session_data:
            return None
        
        conv_key = self.session_data[session_id]['conversation_key']
        if conv_key not in self.conversations:
            return None
        
        return self.conversations[conv_key]
    
    def update_conversation_metadata(self, session_id: str, metadata: Dict[str, Any]):
        """Update conversation metadata"""
        if session_id in self.session_data:
            self.session_data[session_id]['metadata'].update(metadata)
    
    def clear_channel_conversations(self, channel_id: str):
        """Clear all conversations for a channel"""
        to_remove = []
        
        for conv_key, session_info in self.conversations.items():
            if session_info['channel_id'] == channel_id:
                to_remove.append(conv_key)
        
        for conv_key in to_remove:
            self._remove_conversation(conv_key)
        
        logger.info(f"Cleared {len(to_remove)} conversations for channel {channel_id}")
    
    def clear_user_conversations(self, user_id: str):
        """Clear all conversations for a user"""
        if user_id in self.user_sessions:
            sessions = self.user_sessions[user_id].copy()
            for session_id in sessions:
                if session_id in self.session_data:
                    conv_key = self.session_data[session_id]['conversation_key']
                    self._remove_conversation(conv_key)
            
            logger.info(f"Cleared {len(sessions)} conversations for user {user_id}")
    
    def cleanup_expired_conversations(self):
        """Remove expired conversations"""
        current_time = time.time()
        expired = []
        
        for conv_key, session_info in self.conversations.items():
            if not self._is_conversation_valid(session_info):
                expired.append(conv_key)
        
        for conv_key in expired:
            self._remove_conversation(conv_key)
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired conversations")
    
    def get_active_conversation_count(self) -> Dict[str, int]:
        """Get statistics about active conversations"""
        stats = {
            'total': len(self.conversations),
            'by_channel': defaultdict(int),
            'by_user': defaultdict(int)
        }
        
        for session_info in self.conversations.values():
            stats['by_channel'][session_info['channel_id']] += 1
            stats['by_user'][session_info['user_id']] += 1
        
        return stats
    
    def _create_conversation_key(self, user_id: str, channel_id: str, thread_ts: Optional[str]) -> str:
        """Create a unique conversation key"""
        if Config.ENABLE_THREADING and thread_ts:
            return f"{user_id}:{channel_id}:{thread_ts}"
        else:
            return f"{user_id}:{channel_id}"
    
    def _create_session_id(self) -> str:
        """Create a unique session ID"""
        # Use UUID4 for CustomGPT session ID
        return str(uuid.uuid4())
    
    def _is_conversation_valid(self, session_info: Dict[str, Any]) -> bool:
        """Check if conversation is still valid (not expired)"""
        current_time = time.time()
        last_activity = session_info.get('last_activity', 0)
        return (current_time - last_activity) < Config.CONVERSATION_TIMEOUT
    
    def _remove_conversation(self, conv_key: str):
        """Remove a conversation and clean up references"""
        if conv_key not in self.conversations:
            return
        
        session_info = self.conversations[conv_key]
        session_id = session_info['session_id']
        user_id = session_info['user_id']
        
        # Remove from conversations
        del self.conversations[conv_key]
        
        # Remove session data
        if session_id in self.session_data:
            del self.session_data[session_id]
        
        # Remove from user sessions
        if user_id in self.user_sessions and session_id in self.user_sessions[user_id]:
            self.user_sessions[user_id].remove(session_id)
            if not self.user_sessions[user_id]:
                del self.user_sessions[user_id]
    
    def mark_thread_participation(self, channel_id: str, thread_ts: str):
        """Mark that the bot has participated in a thread"""
        if not Config.THREAD_FOLLOW_UP_ENABLED or not thread_ts:
            return
        
        thread_key = f"{channel_id}:{thread_ts}"
        self.thread_participation[thread_key] = {
            'first_participation': time.time(),
            'last_activity': time.time(),
            'message_count': 1,
            'channel_id': channel_id,
            'thread_ts': thread_ts
        }
        logger.info(f"Marked thread participation: {thread_key}")
    
    def update_thread_activity(self, channel_id: str, thread_ts: str):
        """Update thread activity timestamp and message count"""
        if not thread_ts:
            return
        
        thread_key = f"{channel_id}:{thread_ts}"
        if thread_key in self.thread_participation:
            self.thread_participation[thread_key]['last_activity'] = time.time()
            self.thread_participation[thread_key]['message_count'] += 1
    
    def should_respond_to_thread(self, channel_id: str, thread_ts: str) -> Tuple[bool, str]:
        """
        Check if bot should respond to a message in a thread
        
        Returns:
            Tuple of (should_respond, reason)
        """
        if not Config.THREAD_FOLLOW_UP_ENABLED:
            return False, "Thread follow-up is disabled"
        
        if not thread_ts:
            return False, "Not a thread message"
        
        thread_key = f"{channel_id}:{thread_ts}"
        
        # Check if bot has participated in this thread
        if thread_key not in self.thread_participation:
            return False, "Bot has not participated in this thread"
        
        thread_info = self.thread_participation[thread_key]
        current_time = time.time()
        
        # Check if thread participation has expired
        if current_time - thread_info['last_activity'] > Config.THREAD_FOLLOW_UP_TIMEOUT:
            # Clean up expired participation
            del self.thread_participation[thread_key]
            return False, "Thread participation has expired"
        
        # Check message count limit
        if thread_info['message_count'] >= Config.THREAD_FOLLOW_UP_MAX_MESSAGES:
            return False, "Thread message limit reached"
        
        return True, "Bot should respond to thread follow-up"
    
    def cleanup_expired_thread_participation(self):
        """Remove expired thread participations"""
        current_time = time.time()
        expired = []
        
        for thread_key, thread_info in self.thread_participation.items():
            if current_time - thread_info['last_activity'] > Config.THREAD_FOLLOW_UP_TIMEOUT:
                expired.append(thread_key)
        
        for thread_key in expired:
            del self.thread_participation[thread_key]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired thread participations")