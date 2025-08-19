#!/usr/bin/env python3
import os
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode, ChatAction
import structlog

from customgpt_client import CustomGPTClient
from simple_cache import SimpleCache

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = structlog.get_logger()

# Initialize cache
cache = SimpleCache()

# Bot configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CUSTOMGPT_API_URL = os.getenv('CUSTOMGPT_API_URL', 'https://app.customgpt.ai')
CUSTOMGPT_API_KEY = os.getenv('CUSTOMGPT_API_KEY')
CUSTOMGPT_PROJECT_ID = os.getenv('CUSTOMGPT_PROJECT_ID')

# Rate limiting
DAILY_LIMIT = int(os.getenv('RATE_LIMIT_PER_USER_PER_DAY', '100'))
MINUTE_LIMIT = int(os.getenv('RATE_LIMIT_PER_USER_PER_MINUTE', '5'))

# Initialize CustomGPT client
customgpt = CustomGPTClient(CUSTOMGPT_API_URL, CUSTOMGPT_API_KEY, CUSTOMGPT_PROJECT_ID)

# Starter questions
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
        "I need help with a problem",
        "How do I troubleshoot issues?",
        "Where can I find documentation?"
    ]
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    
    # Clear any existing session
    await cache.delete(f"session:{user_id}")
    
    keyboard = [
        [InlineKeyboardButton("🎯 General Questions", callback_data="examples_general")],
        [InlineKeyboardButton("💻 Technical Questions", callback_data="examples_technical")],
        [InlineKeyboardButton("🆘 Support Questions", callback_data="examples_support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = f"""
🤖 Welcome to CustomGPT Bot!

I'm powered by AI and ready to help you with your questions.

You can:
• Ask me questions directly
• Use /help to see available commands
• Click the buttons below for example questions
• Use /stats to see your usage

How can I assist you today?
"""
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
📚 **Available Commands:**

/start - Start a new conversation
/help - Show this help message
/examples - Show example questions
/stats - View your usage statistics
/clear - Clear conversation history

**Tips:**
• Just type your question naturally
• I'll remember our conversation context
• Your daily limit is {} messages

**Need more help?** Just ask!
""".format(DAILY_LIMIT)
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def examples_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show example questions"""
    keyboard = [
        [InlineKeyboardButton("🎯 General", callback_data="examples_general")],
        [InlineKeyboardButton("💻 Technical", callback_data="examples_technical")],
        [InlineKeyboardButton("🆘 Support", callback_data="examples_support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Choose a category to see example questions:",
        reply_markup=reply_markup
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user statistics"""
    user_id = update.effective_user.id
    
    # Get current usage (this is a simplified version)
    _, _, stats = await cache.check_rate_limit(user_id, DAILY_LIMIT, MINUTE_LIMIT)
    
    stats_text = f"""
📊 **Your Usage Statistics**

Today's Usage: {stats.get('daily_used', 0)} / {DAILY_LIMIT}
Remaining Today: {stats.get('daily_remaining', DAILY_LIMIT)}

Keep in mind:
• Daily limit resets at midnight
• Rate limit: {MINUTE_LIMIT} messages per minute
"""
    
    await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear conversation history"""
    user_id = update.effective_user.id
    
    # Clear session
    await cache.delete(f"session:{user_id}")
    
    await update.message.reply_text(
        "✅ Conversation cleared! Start fresh by sending me a message.",
        parse_mode=ParseMode.MARKDOWN
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages"""
    await handle_message_text(
        update.effective_chat.id,
        update.effective_user.id,
        update.message.text,
        context
    )


async def handle_message_text(chat_id: int, user_id: int, user_message: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text message processing"""
    # Check rate limits
    allowed, error_msg, stats = await cache.check_rate_limit(user_id, DAILY_LIMIT, MINUTE_LIMIT)
    
    if not allowed:
        await context.bot.send_message(chat_id=chat_id, text=f"⚠️ {error_msg}")
        return
    
    # Send typing indicator
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    
    try:
        # Get or create session
        session_id = await cache.get(f"session:{user_id}")
        
        if not session_id:
            # Create new conversation
            session_id = await customgpt.create_conversation()
            if session_id:
                await cache.set(f"session:{user_id}", session_id, ttl_seconds=1800)  # 30 minutes
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Sorry, I couldn't start a conversation. Please try again later.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
        
        # Send message to CustomGPT
        response = await customgpt.send_message(
            session_id=session_id,
            message=user_message,
            stream=False
        )
        
        if response and response.get('openai_response'):
            bot_response = response['openai_response']
            
            # Send response with typing effect
            await context.bot.send_message(
                chat_id=chat_id,
                text=bot_response,
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Log successful interaction
            logger.info("message_handled", 
                       user_id=user_id, 
                       session_id=session_id,
                       message_length=len(user_message))
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ I couldn't get a response. Please try again.",
                parse_mode=ParseMode.MARKDOWN
            )
            
    except Exception as e:
        logger.error("message_handling_error", error=str(e), user_id=user_id)
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ An error occurred. Please try again later.",
            parse_mode=ParseMode.MARKDOWN
        )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("examples_"):
        category = query.data.replace("examples_", "")
        questions = STARTER_QUESTIONS.get(category, [])
        
        if questions:
            text = f"**{category.title()} Questions:**\n\n"
            for i, question in enumerate(questions, 1):
                text += f"{i}. {question}\n"
            text += "\nJust click on any question or type your own!"
            
            # Create inline keyboard with questions
            keyboard = []
            for question in questions:
                keyboard.append([InlineKeyboardButton(question, callback_data=f"ask_{question}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    
    elif query.data.startswith("ask_"):
        # Extract the question and send it as if user typed it
        question = query.data.replace("ask_", "")
        
        # Delete the button message
        await query.message.delete()
        
        # Send the question as a message
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"You asked: _{question}_",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Process the question
        await handle_message_text(query.message.chat.id, query.from_user.id, question, context)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and notify user"""
    logger.error("update_error", error=context.error, update=str(update))


async def post_init(application: Application) -> None:
    """Set up bot commands"""
    commands = [
        BotCommand("start", "Start a new conversation"),
        BotCommand("help", "Show help information"),
        BotCommand("examples", "Show example questions"),
        BotCommand("stats", "View your usage statistics"),
        BotCommand("clear", "Clear conversation history"),
    ]
    await application.bot.set_my_commands(commands)


def main() -> None:
    """Start the bot."""
    # Validate environment variables
    if not all([BOT_TOKEN, CUSTOMGPT_API_KEY, CUSTOMGPT_PROJECT_ID]):
        logger.error("Missing required environment variables")
        return
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("examples", examples_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("clear", clear_command))
    
    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Button handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("bot_starting", project_id=CUSTOMGPT_PROJECT_ID)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()