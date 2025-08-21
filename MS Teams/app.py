"""
Flask application for Microsoft Teams CustomGPT Bot
"""

import asyncio
import logging
import sys
from flask import Flask, request, Response
from botbuilder.core import TurnContext, BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from bot import CustomGPTBot
from config import Config
from auth_handler import TeamsAuthHandler

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Validate configuration
try:
    Config.validate()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    sys.exit(1)

# Create adapter
settings = BotFrameworkAdapterSettings(
    app_id=Config.TEAMS_APP_ID,
    app_password=Config.TEAMS_APP_PASSWORD,
    channel_auth_tenant=Config.TEAMS_TENANT_ID,
    openid_metadata=Config.BOT_OPENID_METADATA
)

adapter = BotFrameworkAdapter(settings)

# Create auth handler
auth_handler = TeamsAuthHandler(
    app_id=Config.TEAMS_APP_ID,
    app_password=Config.TEAMS_APP_PASSWORD,
    app_type=Config.TEAMS_APP_TYPE,
    tenant_id=Config.TEAMS_TENANT_ID
)

# Create bot instance
bot = CustomGPTBot()

# Error handler
async def on_error(context: TurnContext, error: Exception):
    """Handle errors"""
    logger.error(f"Error in bot: {error}", exc_info=True)
    
    # Send error message to user
    error_message = (
        "Sorry, an error occurred while processing your request. "
        "Please try again later."
    )
    
    try:
        await context.send_activity(error_message)
    except Exception as e:
        logger.error(f"Error sending error message: {e}")

adapter.on_turn_error = on_error

# Main messaging endpoint
@app.route("/api/messages", methods=["POST"])
def messages():
    """Handle incoming messages from Teams"""
    if "application/json" in request.headers.get("Content-Type", ""):
        body = request.json
    else:
        return Response(status=415)
    
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")
    
    # Process the activity
    async def aux_func(turn_context):
        await bot.on_message_activity(turn_context)
    
    try:
        task = asyncio.create_task(
            adapter.process_activity(activity, auth_header, aux_func)
        )
        asyncio.get_event_loop().run_until_complete(task)
        return Response(status=201)
    except Exception as e:
        logger.error(f"Error processing activity: {e}")
        return Response(status=500)

# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return {"status": "healthy", "bot": "CustomGPT Teams Bot"}

# Home page
@app.route("/", methods=["GET"])
def home():
    """Home page"""
    return """
    <html>
        <head>
            <title>CustomGPT Teams Bot</title>
        </head>
        <body>
            <h1>CustomGPT Teams Bot</h1>
            <p>Bot is running!</p>
            <p>To interact with the bot, please add it to your Microsoft Teams.</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    logger.info(f"Starting bot on {Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT)