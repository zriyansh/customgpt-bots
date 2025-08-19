import os
from dotenv import load_dotenv

load_dotenv()

# Discord Configuration
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_COMMAND_PREFIX = os.getenv('DISCORD_COMMAND_PREFIX', '!')

# CustomGPT Configuration
CUSTOMGPT_API_KEY = os.getenv('CUSTOMGPT_API_KEY')
CUSTOMGPT_API_URL = "https://app.customgpt.ai/api/v1"
CUSTOMGPT_AGENT_ID = os.getenv('CUSTOMGPT_AGENT_ID')  # Your project/agent ID

# Rate Limiting Configuration
RATE_LIMIT_PER_USER = int(os.getenv('RATE_LIMIT_PER_USER', '10'))  # queries per minute
RATE_LIMIT_PER_CHANNEL = int(os.getenv('RATE_LIMIT_PER_CHANNEL', '30'))  # queries per minute
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '60'))  # seconds

# Redis Configuration (for rate limiting)
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# Security Configuration
ALLOWED_CHANNELS = os.getenv('ALLOWED_CHANNELS', '').split(',') if os.getenv('ALLOWED_CHANNELS') else []
ALLOWED_ROLES = os.getenv('ALLOWED_ROLES', '').split(',') if os.getenv('ALLOWED_ROLES') else []
MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '2000'))

# Bot Configuration
ENABLE_STARTER_QUESTIONS = os.getenv('ENABLE_STARTER_QUESTIONS', 'True').lower() == 'true'
TYPING_INDICATOR = os.getenv('TYPING_INDICATOR', 'True').lower() == 'true'
ENABLE_CITATIONS = os.getenv('ENABLE_CITATIONS', 'True').lower() == 'true'
ERROR_MESSAGES = {
    'rate_limit': "⏱️ You've reached your query limit. Please wait a moment before asking again.",
    'api_error': "😕 Sorry, I couldn't process your request. Please try again later.",
    'unauthorized': "🚫 You don't have permission to use this bot.",
    'invalid_input': "❌ Please provide a valid question."
}

# Starter Questions
STARTER_QUESTIONS = [
    "What can you help me with?",
    "Tell me about your capabilities",
    "How do I get started?",
    "What information do you have access to?"
]