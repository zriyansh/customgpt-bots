"""
Configuration for CustomGPT Slack Bot
"""

import os
from typing import Optional

class Config:
    """Bot configuration"""
    
    # Slack Configuration
    SLACK_BOT_TOKEN: str = os.environ.get('SLACK_BOT_TOKEN', '')
    SLACK_SIGNING_SECRET: str = os.environ.get('SLACK_SIGNING_SECRET', '')
    SLACK_APP_TOKEN: Optional[str] = os.environ.get('SLACK_APP_TOKEN')  # For Socket Mode
    
    # CustomGPT Configuration
    CUSTOMGPT_API_KEY: str = os.environ.get('CUSTOMGPT_API_KEY', '')
    CUSTOMGPT_PROJECT_ID: str = os.environ.get('CUSTOMGPT_PROJECT_ID', '')
    CUSTOMGPT_API_BASE_URL: str = os.environ.get('CUSTOMGPT_API_BASE_URL', 'https://app.customgpt.ai/api/v1')
    
    # Rate Limiting Configuration
    RATE_LIMIT_PER_USER: int = int(os.environ.get('RATE_LIMIT_PER_USER', '20'))  # per minute
    RATE_LIMIT_PER_CHANNEL: int = int(os.environ.get('RATE_LIMIT_PER_CHANNEL', '100'))  # per hour
    RATE_LIMIT_WINDOW_USER: int = 60  # seconds
    RATE_LIMIT_WINDOW_CHANNEL: int = 3600  # seconds
    
    # Redis Configuration (optional, for distributed rate limiting)
    REDIS_URL: Optional[str] = os.environ.get('REDIS_URL')
    
    # Bot Behavior Configuration
    MAX_MESSAGE_LENGTH: int = int(os.environ.get('MAX_MESSAGE_LENGTH', '4000'))
    SHOW_CITATIONS: bool = os.environ.get('SHOW_CITATIONS', 'true').lower() == 'true'
    ENABLE_THREADING: bool = os.environ.get('ENABLE_THREADING', 'true').lower() == 'true'
    DEFAULT_LANGUAGE: str = os.environ.get('DEFAULT_LANGUAGE', 'en')
    
    # Security Configuration
    ALLOWED_CHANNELS: Optional[str] = os.environ.get('ALLOWED_CHANNELS')  # Comma-separated list
    BLOCKED_USERS: Optional[str] = os.environ.get('BLOCKED_USERS')  # Comma-separated list
    REQUIRE_MENTION: bool = os.environ.get('REQUIRE_MENTION', 'true').lower() == 'true'
    
    # Logging Configuration
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Analytics Configuration
    ENABLE_ANALYTICS: bool = os.environ.get('ENABLE_ANALYTICS', 'true').lower() == 'true'
    ANALYTICS_ENDPOINT: Optional[str] = os.environ.get('ANALYTICS_ENDPOINT')
    
    # Conversation Management
    CONVERSATION_TIMEOUT: int = int(os.environ.get('CONVERSATION_TIMEOUT', '86400'))  # 24 hours
    MAX_CONTEXT_MESSAGES: int = int(os.environ.get('MAX_CONTEXT_MESSAGES', '10'))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_fields = [
            'SLACK_BOT_TOKEN',
            'SLACK_SIGNING_SECRET',
            'CUSTOMGPT_API_KEY',
            'CUSTOMGPT_PROJECT_ID'
        ]
        
        missing = []
        for field in required_fields:
            if not getattr(cls, field):
                missing.append(field)
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True
    
    @classmethod
    def get_allowed_channels(cls) -> Optional[list]:
        """Get list of allowed channels"""
        if cls.ALLOWED_CHANNELS:
            return [ch.strip() for ch in cls.ALLOWED_CHANNELS.split(',')]
        return None
    
    @classmethod
    def get_blocked_users(cls) -> Optional[list]:
        """Get list of blocked users"""
        if cls.BLOCKED_USERS:
            return [u.strip() for u in cls.BLOCKED_USERS.split(',')]
        return None