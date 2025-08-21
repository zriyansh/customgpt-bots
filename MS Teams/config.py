"""
Configuration for CustomGPT Microsoft Teams Bot
"""

import os
from typing import Optional, List

class Config:
    """Bot configuration"""
    
    # Microsoft Teams Configuration
    TEAMS_APP_ID: str = os.environ.get('TEAMS_APP_ID', '')
    TEAMS_APP_PASSWORD: str = os.environ.get('TEAMS_APP_PASSWORD', '')
    TEAMS_APP_TYPE: str = os.environ.get('TEAMS_APP_TYPE', 'MultiTenant')  # MultiTenant, SingleTenant, or Managed
    TEAMS_TENANT_ID: Optional[str] = os.environ.get('TEAMS_TENANT_ID')  # Required for SingleTenant
    
    # Bot Framework Configuration
    BOT_OPENID_METADATA: str = os.environ.get(
        'BOT_OPENID_METADATA',
        'https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration'
    )
    
    # CustomGPT Configuration
    CUSTOMGPT_API_KEY: str = os.environ.get('CUSTOMGPT_API_KEY', '')
    CUSTOMGPT_PROJECT_ID: str = os.environ.get('CUSTOMGPT_PROJECT_ID', '')
    CUSTOMGPT_API_BASE_URL: str = os.environ.get('CUSTOMGPT_API_BASE_URL', 'https://app.customgpt.ai/api/v1')
    
    # Rate Limiting Configuration
    RATE_LIMIT_PER_USER: int = int(os.environ.get('RATE_LIMIT_PER_USER', '20'))  # per minute
    RATE_LIMIT_PER_CHANNEL: int = int(os.environ.get('RATE_LIMIT_PER_CHANNEL', '100'))  # per hour
    RATE_LIMIT_PER_TENANT: int = int(os.environ.get('RATE_LIMIT_PER_TENANT', '500'))  # per hour
    RATE_LIMIT_WINDOW_USER: int = 60  # seconds
    RATE_LIMIT_WINDOW_CHANNEL: int = 3600  # seconds
    RATE_LIMIT_WINDOW_TENANT: int = 3600  # seconds
    
    # Redis Configuration (optional, for distributed rate limiting)
    REDIS_URL: Optional[str] = os.environ.get('REDIS_URL')
    REDIS_SSL: bool = os.environ.get('REDIS_SSL', 'false').lower() == 'true'
    
    # Bot Behavior Configuration
    MAX_MESSAGE_LENGTH: int = int(os.environ.get('MAX_MESSAGE_LENGTH', '4000'))
    SHOW_CITATIONS: bool = os.environ.get('SHOW_CITATIONS', 'true').lower() == 'true'
    ENABLE_THREADING: bool = os.environ.get('ENABLE_THREADING', 'true').lower() == 'true'
    DEFAULT_LANGUAGE: str = os.environ.get('DEFAULT_LANGUAGE', 'en')
    RESPONSE_TIMEOUT: int = int(os.environ.get('RESPONSE_TIMEOUT', '30'))  # seconds
    
    # Teams-Specific Configuration
    REQUIRE_MENTION_IN_CHANNELS: bool = os.environ.get('REQUIRE_MENTION_IN_CHANNELS', 'true').lower() == 'true'
    RESPOND_TO_OTHER_BOTS: bool = os.environ.get('RESPOND_TO_OTHER_BOTS', 'false').lower() == 'true'
    ENABLE_ADAPTIVE_CARDS: bool = os.environ.get('ENABLE_ADAPTIVE_CARDS', 'true').lower() == 'true'
    ENABLE_MEETING_SUPPORT: bool = os.environ.get('ENABLE_MEETING_SUPPORT', 'false').lower() == 'true'
    ENABLE_FILE_ATTACHMENTS: bool = os.environ.get('ENABLE_FILE_ATTACHMENTS', 'true').lower() == 'true'
    MAX_ATTACHMENT_SIZE: int = int(os.environ.get('MAX_ATTACHMENT_SIZE', '10485760'))  # 10MB in bytes
    
    # Security Configuration
    ALLOWED_TENANTS: Optional[str] = os.environ.get('ALLOWED_TENANTS')  # Comma-separated list
    ALLOWED_CHANNELS: Optional[str] = os.environ.get('ALLOWED_CHANNELS')  # Comma-separated list
    BLOCKED_USERS: Optional[str] = os.environ.get('BLOCKED_USERS')  # Comma-separated list
    ENABLE_AUDIT_LOGGING: bool = os.environ.get('ENABLE_AUDIT_LOGGING', 'true').lower() == 'true'
    
    # Conversation Management
    CONVERSATION_TIMEOUT: int = int(os.environ.get('CONVERSATION_TIMEOUT', '86400'))  # 24 hours
    MAX_CONTEXT_MESSAGES: int = int(os.environ.get('MAX_CONTEXT_MESSAGES', '10'))
    ENABLE_CONVERSATION_HISTORY: bool = os.environ.get('ENABLE_CONVERSATION_HISTORY', 'true').lower() == 'true'
    
    # Proactive Messaging Configuration
    ENABLE_PROACTIVE_MESSAGES: bool = os.environ.get('ENABLE_PROACTIVE_MESSAGES', 'false').lower() == 'true'
    PROACTIVE_MESSAGE_DELAY: int = int(os.environ.get('PROACTIVE_MESSAGE_DELAY', '5'))  # seconds
    
    # Analytics Configuration
    ENABLE_ANALYTICS: bool = os.environ.get('ENABLE_ANALYTICS', 'true').lower() == 'true'
    ANALYTICS_ENDPOINT: Optional[str] = os.environ.get('ANALYTICS_ENDPOINT')
    APPLICATION_INSIGHTS_KEY: Optional[str] = os.environ.get('APPLICATION_INSIGHTS_KEY')
    
    # Logging Configuration
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Server Configuration
    PORT: int = int(os.environ.get('PORT', '3978'))
    HOST: str = os.environ.get('HOST', '0.0.0.0')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_fields = [
            'TEAMS_APP_ID',
            'TEAMS_APP_PASSWORD',
            'CUSTOMGPT_API_KEY',
            'CUSTOMGPT_PROJECT_ID'
        ]
        
        # Additional validation for SingleTenant apps
        if cls.TEAMS_APP_TYPE == 'SingleTenant' and not cls.TEAMS_TENANT_ID:
            raise ValueError("TEAMS_TENANT_ID is required for SingleTenant apps")
        
        missing = []
        for field in required_fields:
            if not getattr(cls, field):
                missing.append(field)
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True
    
    @classmethod
    def get_allowed_tenants(cls) -> Optional[List[str]]:
        """Get list of allowed tenants"""
        if cls.ALLOWED_TENANTS:
            return [t.strip() for t in cls.ALLOWED_TENANTS.split(',')]
        return None
    
    @classmethod
    def get_allowed_channels(cls) -> Optional[List[str]]:
        """Get list of allowed channels"""
        if cls.ALLOWED_CHANNELS:
            return [ch.strip() for ch in cls.ALLOWED_CHANNELS.split(',')]
        return None
    
    @classmethod
    def get_blocked_users(cls) -> Optional[List[str]]:
        """Get list of blocked users"""
        if cls.BLOCKED_USERS:
            return [u.strip() for u in cls.BLOCKED_USERS.split(',')]
        return None
    
    @classmethod
    def is_tenant_allowed(cls, tenant_id: str) -> bool:
        """Check if tenant is allowed"""
        allowed_tenants = cls.get_allowed_tenants()
        if not allowed_tenants:
            return True
        return tenant_id in allowed_tenants
    
    @classmethod
    def is_channel_allowed(cls, channel_id: str) -> bool:
        """Check if channel is allowed"""
        allowed_channels = cls.get_allowed_channels()
        if not allowed_channels:
            return True
        return channel_id in allowed_channels
    
    @classmethod
    def is_user_blocked(cls, user_id: str) -> bool:
        """Check if user is blocked"""
        blocked_users = cls.get_blocked_users()
        if not blocked_users:
            return False
        return user_id in blocked_users