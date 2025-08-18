import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    # Telegram Configuration
    telegram_bot_token: str = Field(..., env='TELEGRAM_BOT_TOKEN')
    
    # CustomGPT Configuration
    customgpt_api_url: str = Field('https://app.customgpt.ai', env='CUSTOMGPT_API_URL')
    customgpt_api_key: str = Field(..., env='CUSTOMGPT_API_KEY')
    customgpt_project_id: str = Field(..., env='CUSTOMGPT_PROJECT_ID')
    
    # Redis Configuration
    redis_url: str = Field('redis://localhost:6379', env='REDIS_URL')
    redis_db: int = Field(0, env='REDIS_DB')
    
    # MongoDB Configuration
    mongodb_url: Optional[str] = Field(None, env='MONGODB_URL')
    mongodb_db_name: str = Field('customgpt_telegram_bot', env='MONGODB_DB_NAME')
    
    # Rate Limiting
    rate_limit_per_user_per_day: int = Field(100, env='RATE_LIMIT_PER_USER_PER_DAY')
    rate_limit_per_user_per_minute: int = Field(5, env='RATE_LIMIT_PER_USER_PER_MINUTE')
    
    # Security
    max_message_length: int = Field(4000, env='MAX_MESSAGE_LENGTH')
    allowed_users: Optional[List[int]] = Field(None, env='ALLOWED_USERS')
    webhook_secret: Optional[str] = Field(None, env='WEBHOOK_SECRET')
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(None, env='SENTRY_DSN')
    log_level: str = Field('INFO', env='LOG_LEVEL')
    
    # Bot Settings
    default_language: str = Field('en', env='DEFAULT_LANGUAGE')
    session_timeout_minutes: int = Field(30, env='SESSION_TIMEOUT_MINUTES')
    max_conversation_history: int = Field(10, env='MAX_CONVERSATION_HISTORY')
    
    # Environment
    environment: str = Field('development', env='ENVIRONMENT')
    
    @validator('allowed_users', pre=True)
    def parse_allowed_users(cls, v):
        if isinstance(v, str) and v:
            return [int(user_id.strip()) for user_id in v.split(',')]
        return None
    
    class Config:
        env_file = '.env'
        case_sensitive = False


# Starter questions for different categories
STARTER_QUESTIONS = {
    'general': [
        "What can you help me with?",
        "Tell me about your capabilities",
        "How do I get started?"
    ],
    'technical': [
        "Explain how to use the API",
        "What are the best practices?",
        "Show me some examples"
    ],
    'support': [
        "I'm having trouble with...",
        "How do I troubleshoot?",
        "Where can I find documentation?"
    ]
}

# Error messages
ERROR_MESSAGES = {
    'rate_limit': "⚠️ You've reached your message limit. Please try again later.",
    'unauthorized': "🚫 Sorry, you're not authorized to use this bot.",
    'api_error': "❌ Something went wrong. Please try again later.",
    'message_too_long': f"📏 Your message is too long. Please keep it under {{max_length}} characters.",
    'session_expired': "⏰ Your session has expired. Please start a new conversation with /start"
}

# Success messages
SUCCESS_MESSAGES = {
    'welcome': """
🤖 Welcome to CustomGPT Bot!

I'm powered by the {agent_name} knowledge base and I'm here to help you.

You can:
• Ask me questions directly
• Use /help to see available commands
• Use /examples to see starter questions
• Use /stats to see your usage statistics

How can I assist you today?
""",
    'help': """
📚 **Available Commands:**

/start - Start a new conversation
/help - Show this help message
/examples - Show example questions
/stats - View your usage statistics
/clear - Clear conversation history
/language [code] - Change language (en, es, fr, etc.)
/feedback [message] - Send feedback
/agent [id] - Switch to a different agent

**Tips:**
• Just type your question naturally
• Use reply to continue a conversation thread
• Your conversation history is preserved for {timeout} minutes
""",
    'examples_intro': "Here are some questions you can ask:"
}


def get_settings() -> Settings:
    return Settings()