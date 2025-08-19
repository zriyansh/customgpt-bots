"""
Configuration for WhatsApp Bot
"""

import os
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    """Bot configuration"""
    
    # CustomGPT settings
    CUSTOMGPT_API_KEY: str
    CUSTOMGPT_PROJECT_ID: str
    CUSTOMGPT_API_URL: str = "https://app.customgpt.ai"
    
    # Twilio settings
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_WHATSAPP_NUMBER: str  # Format: whatsapp:+14155238886
    
    # Rate limiting
    RATE_LIMIT_DAILY: int = 100
    RATE_LIMIT_MINUTE: int = 5
    RATE_LIMIT_HOUR: int = 30
    
    # Security
    ALLOWED_NUMBERS: Optional[List[str]] = None  # Comma-separated list
    BLOCKED_NUMBERS: Optional[List[str]] = None  # Comma-separated list
    MAX_MESSAGE_LENGTH: int = 500
    ENABLE_PROFANITY_FILTER: bool = False
    
    # Features
    ENABLE_VOICE_MESSAGES: bool = True
    ENABLE_MEDIA_RESPONSES: bool = True
    ENABLE_LOCATION_SHARING: bool = False
    ENABLE_THINKING_MESSAGE: bool = False  # Show "Thinking..." message
    DEFAULT_LANGUAGE: str = "en"
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # Admin
    ADMIN_API_KEY: Optional[str] = None
    ADMIN_NUMBERS: Optional[List[str]] = None  # Comma-separated admin numbers
    
    # Session
    SESSION_TIMEOUT_MINUTES: int = 30
    SESSION_CONTEXT_MESSAGES: int = 10
    
    # Analytics
    ENABLE_ANALYTICS: bool = True
    ANALYTICS_RETENTION_DAYS: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Server
    PORT: int = 8000
    DEBUG: bool = False
    
    @field_validator('ALLOWED_NUMBERS', 'BLOCKED_NUMBERS', 'ADMIN_NUMBERS', mode='before')
    @classmethod
    def split_numbers(cls, v):
        if v:
            return [num.strip() for num in v.split(',')]
        return []
    
    @field_validator('TWILIO_WHATSAPP_NUMBER', mode='before')
    @classmethod
    def validate_whatsapp_number(cls, v):
        if v and not v.startswith('whatsapp:'):
            return f'whatsapp:{v}'
        return v
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


# Starter questions configuration
STARTER_QUESTIONS = {
    "general": [
        "What can you help me with?",
        "Tell me about your capabilities",
        "How do I get started?",
        "What kind of questions can I ask?"
    ],
    "technical": [
        "How do I use the API?",
        "What are the best practices?",
        "Can you show me some examples?",
        "How do I integrate with my system?"
    ],
    "support": [
        "I need help with a problem",
        "How do I troubleshoot issues?",
        "Where can I find documentation?",
        "How do I contact support?"
    ],
    "features": [
        "What features are available?",
        "How do I customize responses?",
        "Can you explain the pricing?",
        "What are the limitations?"
    ]
}

# Response templates
RESPONSE_TEMPLATES = {
    "welcome": """🤖 Welcome to {bot_name}!

I'm here to help you with questions about {agent_name}.

You can:
• Ask me anything about our knowledge base
• Use /help to see available commands
• Send /examples for sample questions

How can I assist you today?""",
    
    "help": """📚 *Available Commands:*

/start - Start a new conversation
/help - Show this help message
/examples - Show example questions
/stats - View your usage statistics
/language [code] - Change language (en, es, fr, etc.)
/clear - Clear conversation history
/feedback [message] - Send feedback

*Tips:*
• Just type your question naturally
• I remember our conversation context
• Your daily limit is {daily_limit} messages

Need help? Just ask!""",
    
    "rate_limit_daily": """⏳ Daily limit reached ({daily_limit} messages).

Your limit resets at midnight. Consider upgrading for higher limits!

Stats: {daily_used}/{daily_limit} messages used today.""",
    
    "rate_limit_minute": """⏰ Slow down! You've sent too many messages.

Please wait {seconds} seconds before sending another message.

Current rate: {minute_used}/{minute_limit} messages per minute.""",
    
    "error": """❌ Sorry, something went wrong.

Please try again. If the problem persists, contact support with error code: {error_code}""",
    
    "no_response": """😕 I couldn't find an answer to that question.

Try rephrasing or asking something else. Type /examples to see what I can help with.""",
    
    "session_expired": """⏱️ Your session has expired.

Starting a new conversation. Your previous context has been cleared.""",
    
    "feedback_received": """✅ Thank you for your feedback!

Your message has been recorded and will help us improve.""",
    
    "language_changed": """🌍 Language changed to {language}.

All my responses will now be in {language_name}.""",
    
    "stats": """📊 *Your Usage Statistics*

*Today:* {daily_used}/{daily_limit} messages
*This hour:* {hourly_used}/{hourly_limit} messages
*Total messages:* {total_messages}
*Member since:* {member_since}

*Most active hours:* {active_hours}
*Average response time:* {avg_response_time}s"""
}

# Language codes and names
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "hi": "Hindi",
    "id": "Indonesian",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "th": "Thai",
    "sv": "Swedish",
    "da": "Danish"
}

# Error messages
ERROR_MESSAGES = {
    "unauthorized": "You are not authorized to use this bot.",
    "blocked": "Your number has been blocked.",
    "invalid_message": "Invalid message format.",
    "message_too_long": "Message too long. Maximum 500 characters.",
    "profanity_detected": "Please keep the conversation respectful.",
    "invalid_command": "Unknown command. Type /help for available commands.",
    "invalid_language": "Unsupported language. Available: " + ", ".join(SUPPORTED_LANGUAGES.keys()),
    "session_error": "Could not create session. Please try again.",
    "api_error": "API error occurred. Please try again later.",
    "media_not_supported": "Media files are not supported. Please send text only.",
    "voice_not_supported": "Voice messages are not supported. Please send text.",
    "location_not_supported": "Location sharing is not supported."
}