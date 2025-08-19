"""
Command handler for WhatsApp bot
"""

from typing import Optional
from datetime import datetime
import structlog

from config import Config, RESPONSE_TEMPLATES, STARTER_QUESTIONS, SUPPORTED_LANGUAGES
from customgpt_client import CustomGPTClient
from session_manager import SessionManager
from rate_limiter import RateLimiter

logger = structlog.get_logger()


class CommandHandler:
    def __init__(self, customgpt: CustomGPTClient, 
                 session_manager: SessionManager,
                 rate_limiter: RateLimiter,
                 config: Config):
        self.customgpt = customgpt
        self.session_manager = session_manager
        self.rate_limiter = rate_limiter
        self.config = config
        
        # Command mapping
        self.commands = {
            '/start': self.handle_start,
            '/help': self.handle_help,
            '/examples': self.handle_examples,
            '/stats': self.handle_stats,
            '/language': self.handle_language,
            '/clear': self.handle_clear,
            '/feedback': self.handle_feedback,
            '/about': self.handle_about,
            '/settings': self.handle_settings
        }
    
    async def handle_command(self, user_id: str, message: str) -> str:
        """Handle bot commands"""
        parts = message.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Check if command exists
        handler = self.commands.get(command)
        if not handler:
            return f"❌ Unknown command: {command}\n\nType /help to see available commands."
        
        # Execute command handler
        try:
            return await handler(user_id, args)
        except Exception as e:
            logger.error("command_error", command=command, error=str(e))
            return "❌ An error occurred while processing the command. Please try again."
    
    async def handle_start(self, user_id: str, args: str) -> str:
        """Handle /start command"""
        # Create new session
        session_id = await self.customgpt.create_conversation()
        if session_id:
            await self.session_manager.create_session(user_id, session_id)
        
        # Get agent info
        agent_info = await self.customgpt.get_agent_info()
        agent_name = agent_info.get('project_name', 'CustomGPT') if agent_info else 'CustomGPT'
        
        # Format welcome message
        welcome_msg = RESPONSE_TEMPLATES['welcome'].format(
            bot_name="WhatsApp Bot",
            agent_name=agent_name
        )
        
        # Add starter questions
        welcome_msg += "\n\n💡 *Try these questions:*\n"
        for i, question in enumerate(STARTER_QUESTIONS['general'][:3]):
            welcome_msg += f"{i+1}. {question}\n"
        
        return welcome_msg
    
    async def handle_help(self, user_id: str, args: str) -> str:
        """Handle /help command"""
        # Get user stats for context
        stats = await self.rate_limiter.get_user_stats(user_id)
        daily_limit = self.config.RATE_LIMIT_DAILY
        
        return RESPONSE_TEMPLATES['help'].format(daily_limit=daily_limit)
    
    async def handle_examples(self, user_id: str, args: str) -> str:
        """Handle /examples command"""
        examples_text = "📚 *Example Questions*\n\n"
        
        # Show specific category if provided
        if args and args.lower() in STARTER_QUESTIONS:
            category = args.lower()
            examples_text += f"*{category.title()} Questions:*\n"
            for i, question in enumerate(STARTER_QUESTIONS[category]):
                examples_text += f"{i+1}. {question}\n"
        else:
            # Show all categories
            for category, questions in STARTER_QUESTIONS.items():
                examples_text += f"\n*{category.title()}:*\n"
                for i, question in enumerate(questions[:2]):  # Show first 2 from each
                    examples_text += f"• {question}\n"
            
            examples_text += "\n💡 Use `/examples [category]` to see more from a specific category."
        
        return examples_text
    
    async def handle_stats(self, user_id: str, args: str) -> str:
        """Handle /stats command"""
        # Get user statistics
        stats = await self.rate_limiter.get_user_stats(user_id)
        
        # Get session info
        session = await self.session_manager.get_session(user_id)
        
        # Calculate member since
        if session and 'created_at' in session:
            created_at = datetime.fromisoformat(session['created_at'])
            member_since = created_at.strftime("%Y-%m-%d")
        else:
            member_since = "Today"
        
        # Format stats message
        return RESPONSE_TEMPLATES['stats'].format(
            daily_used=stats['daily']['used'],
            daily_limit=stats['daily']['limit'],
            hourly_used=stats.get('hourly', {}).get('used', 0),
            hourly_limit=self.config.RATE_LIMIT_HOUR,
            total_messages=stats.get('monthly', {}).get('used', 0),
            member_since=member_since,
            active_hours="9 AM - 5 PM",  # TODO: Calculate from analytics
            avg_response_time="1.2"  # TODO: Calculate from analytics
        )
    
    async def handle_language(self, user_id: str, args: str) -> str:
        """Handle /language command"""
        if not args:
            # Show current language and available options
            current_lang = await self.session_manager.get_user_language(user_id)
            lang_list = "\n".join([f"• {code} - {name}" for code, name in SUPPORTED_LANGUAGES.items()])
            
            return f"🌍 *Current language:* {SUPPORTED_LANGUAGES.get(current_lang, current_lang)}\n\n" \
                   f"*Available languages:*\n{lang_list}\n\n" \
                   f"To change: `/language [code]`\n" \
                   f"Example: `/language es` for Spanish"
        
        # Change language
        lang_code = args.lower().strip()
        if lang_code not in SUPPORTED_LANGUAGES:
            return f"❌ Unsupported language: {lang_code}\n\n" \
                   f"Available: {', '.join(SUPPORTED_LANGUAGES.keys())}"
        
        # Update session language
        success = await self.session_manager.set_language(user_id, lang_code)
        
        if success:
            return RESPONSE_TEMPLATES['language_changed'].format(
                language=lang_code,
                language_name=SUPPORTED_LANGUAGES[lang_code]
            )
        else:
            return "❌ Failed to change language. Please try again."
    
    async def handle_clear(self, user_id: str, args: str) -> str:
        """Handle /clear command"""
        # Clear session
        success = await self.session_manager.clear_session(user_id)
        
        if success:
            # Create new session
            session_id = await self.customgpt.create_conversation()
            if session_id:
                await self.session_manager.create_session(user_id, session_id)
            
            return "✅ Conversation cleared! Starting fresh.\n\nHow can I help you?"
        else:
            return "❌ Failed to clear conversation. Please try again."
    
    async def handle_feedback(self, user_id: str, args: str) -> str:
        """Handle /feedback command"""
        if not args:
            return "💬 *Send Feedback*\n\n" \
                   "Please provide your feedback after the command.\n" \
                   "Example: `/feedback The bot is very helpful!`\n\n" \
                   "Your feedback helps us improve!"
        
        # Log feedback (you can implement actual feedback storage)
        logger.info("user_feedback", user_id=user_id, feedback=args)
        
        return RESPONSE_TEMPLATES['feedback_received']
    
    async def handle_about(self, user_id: str, args: str) -> str:
        """Handle /about command"""
        # Get agent info
        agent_info = await self.customgpt.get_agent_info()
        
        if agent_info:
            about_text = f"ℹ️ *About This Bot*\n\n"
            about_text += f"*Agent:* {agent_info.get('project_name', 'CustomGPT')}\n"
            
            if agent_info.get('chatbot_prompt'):
                about_text += f"\n*Description:*\n{agent_info['chatbot_prompt'][:200]}...\n"
            
            stats = agent_info.get('stats', {})
            if stats:
                about_text += f"\n*Statistics:*\n"
                about_text += f"• Pages indexed: {stats.get('total_pages', 0)}\n"
                about_text += f"• Last updated: {stats.get('last_update', 'N/A')}\n"
            
            return about_text
        else:
            return "ℹ️ *About This Bot*\n\n" \
                   "I'm powered by CustomGPT to answer your questions based on a specialized knowledge base.\n\n" \
                   "Type /help to see what I can do!"
    
    async def handle_settings(self, user_id: str, args: str) -> str:
        """Handle /settings command"""
        # Get current settings
        session = await self.session_manager.get_session(user_id)
        current_lang = session.get('language', 'en') if session else 'en'
        
        # Get user stats
        stats = await self.rate_limiter.get_user_stats(user_id)
        
        settings_text = "⚙️ *Your Settings*\n\n"
        settings_text += f"*Language:* {SUPPORTED_LANGUAGES.get(current_lang, current_lang)}\n"
        settings_text += f"*Daily limit:* {stats['daily']['used']}/{self.config.RATE_LIMIT_DAILY}\n"
        settings_text += f"*Session timeout:* {self.config.SESSION_TIMEOUT_MINUTES} minutes\n"
        
        settings_text += "\n*Available Settings:*\n"
        settings_text += "• `/language [code]` - Change language\n"
        settings_text += "• `/clear` - Clear conversation history\n"
        settings_text += "• `/feedback [message]` - Send feedback\n"
        
        return settings_text