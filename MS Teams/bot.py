"""
Microsoft Teams Bot Implementation for CustomGPT
"""

import asyncio
import logging
import re
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from botbuilder.core import (
    TurnContext,
    MessageFactory,
    CardFactory,
    ActivityHandler,
    BotFrameworkAdapter
)
from botbuilder.schema import (
    Activity,
    ActivityTypes,
    ChannelAccount,
    ConversationReference,
    Mention,
    CardAction,
    ActionTypes,
    SuggestedActions,
    CardImage,
    HeroCard,
    ThumbnailCard,
    Attachment
)
from botbuilder.core.conversation_state import ConversationState
from botbuilder.core.user_state import UserState

from config import Config
from customgpt_client import CustomGPTClient
from rate_limiter import RateLimiter
from conversation_manager import ConversationManager
from adaptive_cards import AdaptiveCardBuilder

logger = logging.getLogger(__name__)

class TeamsBot(ActivityHandler):
    """Microsoft Teams bot implementation"""
    
    def __init__(
        self,
        conversation_state: ConversationState,
        user_state: UserState
    ):
        super().__init__()
        
        # Initialize components
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.customgpt_client = CustomGPTClient(Config.CUSTOMGPT_API_KEY)
        self.rate_limiter = RateLimiter(self.customgpt_client)
        self.conversation_manager = ConversationManager()
        
        # Cache for starter questions
        self._starter_questions_cache = None
        self._starter_questions_timestamp = None
        self._starter_questions_ttl = 3600  # 1 hour cache
        
        # Command patterns
        self.command_patterns = {
            '/help': self._handle_help_command,
            '/clear': self._handle_clear_command,
            '/status': self._handle_status_command
        }
    
    async def on_message_activity(self, turn_context: TurnContext) -> None:
        """Handle incoming messages"""
        try:
            # Extract message details
            activity = turn_context.activity
            text = activity.text.strip() if activity.text else ""
            
            # Handle adaptive card actions
            if activity.value:
                await self._handle_card_action(turn_context, activity.value)
                return
            
            # Skip empty messages
            if not text:
                return
            
            # Get conversation details
            user_id = activity.from_property.id
            user_name = activity.from_property.name
            channel_id = activity.channel_data.get("channel", {}).get("id", activity.conversation.id)
            tenant_id = activity.channel_data.get("tenant", {}).get("id", "default")
            thread_id = activity.conversation.conversation_type if activity.conversation.is_group else None
            
            # Check if bot was mentioned in a channel
            is_channel = activity.conversation.is_group
            bot_mentioned = False
            
            if is_channel:
                # Remove bot mentions from text
                text, bot_mentioned = self._remove_mentions(activity)
                
                # Skip if bot wasn't mentioned and mentions are required
                if Config.REQUIRE_MENTION_IN_CHANNELS and not bot_mentioned:
                    return
            
            # Check if sender is a bot and we should ignore
            if activity.from_property.properties.get("isBot") and not Config.RESPOND_TO_OTHER_BOTS:
                return
            
            # Security checks
            if Config.is_user_blocked(user_id):
                await turn_context.send_activity("Sorry, you don't have permission to use this bot.")
                return
            
            if not Config.is_tenant_allowed(tenant_id):
                await turn_context.send_activity("Sorry, this bot is not available for your organization.")
                return
            
            if not Config.is_channel_allowed(channel_id):
                await turn_context.send_activity("Sorry, this bot is not enabled for this channel.")
                return
            
            # Check for commands
            command = text.lower().split()[0] if text else ""
            if command in self.command_patterns:
                await self.command_patterns[command](turn_context)
                return
            
            # Rate limiting
            is_allowed, error_message = await self.rate_limiter.check_rate_limit(
                user_id,
                channel_id,
                tenant_id
            )
            
            if not is_allowed:
                # Get remaining quota
                quota_info = await self.rate_limiter.get_remaining_quota(user_id, tenant_id)
                
                # Send rate limit card
                card = AdaptiveCardBuilder.create_rate_limit_card(
                    reset_time=60,  # Default to 60 seconds
                    user_remaining=quota_info.get("user_remaining"),
                    api_remaining=quota_info.get("api_remaining")
                )
                await turn_context.send_activity(MessageFactory.attachment(card))
                return
            
            # Send typing indicator
            await self._send_typing_indicator(turn_context)
            
            # Get or create conversation context
            conversation = await self.conversation_manager.get_or_create_conversation(
                channel_id=channel_id,
                tenant_id=tenant_id,
                user_id=user_id,
                thread_id=thread_id,
                metadata={
                    "user_name": user_name,
                    "is_channel": is_channel,
                    "teams_conversation_id": activity.conversation.id
                }
            )
            
            # Send message to CustomGPT
            try:
                # Get context messages if threading is enabled
                context_messages = []
                if Config.ENABLE_THREADING and Config.ENABLE_CONVERSATION_HISTORY:
                    context_messages = await self.conversation_manager.get_context_messages(
                        channel_id,
                        user_id,
                        thread_id,
                        limit=Config.MAX_CONTEXT_MESSAGES
                    )
                
                # Prepare user info for API
                user_info = {
                    "id": user_id,
                    "name": user_name,
                    "tenant": tenant_id,
                    "channel": channel_id
                }
                
                # Send message
                if context_messages:
                    # Use OpenAI format with context
                    messages = context_messages + [{"role": "user", "content": text}]
                    response_data = await self.customgpt_client.send_message_openai_format(
                        project_id=Config.CUSTOMGPT_PROJECT_ID,
                        messages=messages,
                        lang=Config.DEFAULT_LANGUAGE,
                        session_id=conversation.session_id
                    )
                    
                    # Extract response
                    response_text = response_data['choices'][0]['message']['content']
                    citations = response_data.get('citations', [])
                    session_id = response_data.get('session_id', conversation.session_id)
                    message_id = response_data.get('id')
                else:
                    # Use standard format
                    response_data = await self.customgpt_client.send_message(
                        project_id=Config.CUSTOMGPT_PROJECT_ID,
                        session_id=conversation.session_id,
                        message=text,
                        lang=Config.DEFAULT_LANGUAGE,
                        user_info=user_info
                    )
                    
                    response_text = response_data['openai_response']
                    citations = response_data.get('citations', [])
                    session_id = response_data['session_id']
                    message_id = response_data['id']
                
                # Update session ID if it changed
                if session_id != conversation.session_id:
                    await self.conversation_manager.update_session_id(
                        channel_id,
                        user_id,
                        session_id,
                        thread_id
                    )
                
                # Add messages to context
                await self.conversation_manager.add_message_to_context(
                    channel_id,
                    user_id,
                    "user",
                    text,
                    thread_id
                )
                
                await self.conversation_manager.add_message_to_context(
                    channel_id,
                    user_id,
                    "assistant",
                    response_text,
                    thread_id
                )
                
                # Send response
                if Config.ENABLE_ADAPTIVE_CARDS:
                    # Create adaptive card response
                    card = AdaptiveCardBuilder.create_response_card(
                        response=response_text,
                        citations=citations if Config.SHOW_CITATIONS else None,
                        session_id=session_id,
                        message_id=message_id,
                        show_feedback=True
                    )
                    await turn_context.send_activity(MessageFactory.attachment(card))
                else:
                    # Send plain text response
                    await turn_context.send_activity(MessageFactory.text(response_text))
                
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                
                # Send error card
                error_card = AdaptiveCardBuilder.create_error_card(
                    error_message="I encountered an error while processing your request.",
                    details=str(e) if Config.LOG_LEVEL == "DEBUG" else None,
                    retry_available=True
                )
                await turn_context.send_activity(MessageFactory.attachment(error_card))
        
        except Exception as e:
            logger.error(f"Unexpected error in message handler: {str(e)}")
            await turn_context.send_activity("An unexpected error occurred. Please try again later.")
    
    async def on_members_added_activity(
        self,
        members_added: List[ChannelAccount],
        turn_context: TurnContext
    ) -> None:
        """Handle new members joining"""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                # New user joined, send welcome message
                await self._send_welcome_message(turn_context)
    
    async def _send_welcome_message(self, turn_context: TurnContext) -> None:
        """Send welcome message to new users"""
        try:
            # Get starter questions
            starter_questions = await self._get_starter_questions()
            
            # Create welcome card
            welcome_card = AdaptiveCardBuilder.create_welcome_card(
                bot_name="CustomGPT",
                starter_questions=starter_questions
            )
            
            await turn_context.send_activity(MessageFactory.attachment(welcome_card))
        except Exception as e:
            logger.error(f"Error sending welcome message: {str(e)}")
            await turn_context.send_activity(
                "Welcome! I'm CustomGPT Bot. Ask me anything or type /help for more information."
            )
    
    async def _handle_card_action(self, turn_context: TurnContext, value: Dict[str, Any]) -> None:
        """Handle adaptive card actions"""
        action = value.get("action")
        
        if action == "ask_question":
            # Handle starter question selection
            question = value.get("question")
            if question:
                # Update activity text and process as normal message
                turn_context.activity.text = question
                await self.on_message_activity(turn_context)
        
        elif action == "feedback":
            # Handle feedback
            reaction = value.get("reaction")
            session_id = value.get("session_id")
            message_id = value.get("message_id")
            
            if reaction and session_id and message_id:
                try:
                    await self.customgpt_client.update_message_feedback(
                        Config.CUSTOMGPT_PROJECT_ID,
                        session_id,
                        message_id,
                        reaction
                    )
                    
                    # Send confirmation
                    confirmation_card = AdaptiveCardBuilder.create_feedback_confirmation_card(reaction)
                    await turn_context.send_activity(MessageFactory.attachment(confirmation_card))
                except Exception as e:
                    logger.error(f"Error updating feedback: {str(e)}")
        
        elif action == "copy":
            # Handle copy action (client-side handling needed)
            await turn_context.send_activity("Please select and copy the text above.")
        
        elif action == "retry":
            # Handle retry action
            await turn_context.send_activity("Please try your question again.")
    
    async def _handle_help_command(self, turn_context: TurnContext) -> None:
        """Handle /help command"""
        help_card = AdaptiveCardBuilder.create_help_card()
        await turn_context.send_activity(MessageFactory.attachment(help_card))
    
    async def _handle_clear_command(self, turn_context: TurnContext) -> None:
        """Handle /clear command"""
        activity = turn_context.activity
        user_id = activity.from_property.id
        channel_id = activity.channel_data.get("channel", {}).get("id", activity.conversation.id)
        thread_id = activity.conversation.conversation_type if activity.conversation.is_group else None
        
        # Clear conversation
        await self.conversation_manager.clear_conversation(
            channel_id,
            user_id,
            thread_id
        )
        
        await turn_context.send_activity("✅ Conversation history cleared. Starting fresh!")
    
    async def _handle_status_command(self, turn_context: TurnContext) -> None:
        """Handle /status command"""
        activity = turn_context.activity
        user_id = activity.from_property.id
        tenant_id = activity.channel_data.get("tenant", {}).get("id", "default")
        
        # Get quota information
        quota_info = await self.rate_limiter.get_remaining_quota(user_id, tenant_id)
        
        # Get conversation info
        conversation_count = await self.conversation_manager.get_active_conversations_count(tenant_id)
        
        status_text = f"""**Bot Status**
        
**Rate Limits:**
• User messages remaining: {quota_info['user_remaining']}/{quota_info['user_limit']} (per minute)
• API queries remaining: {quota_info['api_remaining']}/{quota_info['api_limit']} if quota_info['api_remaining'] else 'N/A'

**Active Conversations:** {conversation_count}

**Configuration:**
• Language: {Config.DEFAULT_LANGUAGE}
• Threading: {'Enabled' if Config.ENABLE_THREADING else 'Disabled'}
• Citations: {'Shown' if Config.SHOW_CITATIONS else 'Hidden'}
"""
        
        await turn_context.send_activity(MessageFactory.text(status_text))
    
    async def _send_typing_indicator(self, turn_context: TurnContext) -> None:
        """Send typing indicator"""
        typing_activity = MessageFactory.text("")
        typing_activity.type = ActivityTypes.typing
        await turn_context.send_activity(typing_activity)
    
    def _remove_mentions(self, activity: Activity) -> tuple[str, bool]:
        """Remove bot mentions from text and check if bot was mentioned"""
        text = activity.text or ""
        bot_mentioned = False
        
        if activity.entities:
            for entity in activity.entities:
                if entity.type == "mention":
                    mentioned = entity.properties.get("mentioned", {})
                    if mentioned.get("id") == activity.recipient.id:
                        bot_mentioned = True
                        # Remove mention text
                        mention_text = entity.properties.get("text", "")
                        text = text.replace(mention_text, "").strip()
        
        return text, bot_mentioned
    
    async def _get_starter_questions(self) -> List[str]:
        """Get starter questions from agent settings"""
        try:
            # Check cache
            now = datetime.now(timezone.utc)
            if self._starter_questions_cache and self._starter_questions_timestamp:
                cache_age = (now - self._starter_questions_timestamp).total_seconds()
                if cache_age < self._starter_questions_ttl:
                    return self._starter_questions_cache
            
            # Get fresh data
            settings = await self.customgpt_client.get_agent_settings(Config.CUSTOMGPT_PROJECT_ID)
            starter_questions = settings.get('starter_questions', [])
            
            # Update cache
            self._starter_questions_cache = starter_questions
            self._starter_questions_timestamp = now
            
            return starter_questions
        except Exception as e:
            logger.error(f"Error getting starter questions: {str(e)}")
            return [
                "What can you help me with?",
                "Tell me about your capabilities",
                "How do I get started?"
            ]
    
    async def on_turn_error(self, context: TurnContext, error: Exception) -> None:
        """Handle errors"""
        logger.error(f"Turn error: {str(error)}")
        
        try:
            # Send error message
            await context.send_activity(
                "Sorry, an error occurred while processing your request. Please try again."
            )
        except Exception:
            pass