#!/usr/bin/env python3
"""
CustomGPT Slack Bot
A Slack bot that integrates with CustomGPT's RAG platform
"""

import os
import re
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Optional, List, Any

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_sdk.web.async_client import AsyncWebClient

from config import Config
from customgpt_client import CustomGPTClient
from rate_limiter import RateLimiter
from conversation_manager import ConversationManager
from security_manager import SecurityManager
from starter_questions import StarterQuestionsManager
from analytics import Analytics

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components
app = AsyncApp(
    token=Config.SLACK_BOT_TOKEN,
    signing_secret=Config.SLACK_SIGNING_SECRET
)
customgpt_client = CustomGPTClient(Config.CUSTOMGPT_API_KEY)
rate_limiter = RateLimiter()
conversation_manager = ConversationManager()
security_manager = SecurityManager()
starter_questions_manager = StarterQuestionsManager(customgpt_client)
analytics = Analytics()

# Store active agent IDs per channel/user
agent_registry: Dict[str, str] = {}

def get_agent_id(channel_id: str, user_id: str) -> str:
    """Get the active agent ID for a channel or user"""
    # Check channel-specific agent first, then user-specific, then default
    return (agent_registry.get(f"channel:{channel_id}") or 
            agent_registry.get(f"user:{user_id}") or 
            Config.CUSTOMGPT_PROJECT_ID)

def set_agent_id(context_type: str, context_id: str, agent_id: str):
    """Set the active agent ID for a channel or user"""
    agent_registry[f"{context_type}:{context_id}"] = agent_id

async def format_response_with_citations(response: Dict[str, Any]) -> Dict[str, Any]:
    """Format CustomGPT response with citations for Slack"""
    blocks = []
    
    # Main response
    response_text = response.get('openai_response', response.get('response', ''))
    blocks.append({
        "type": "section",
        "text": {"type": "mrkdwn", "text": response_text}
    })
    
    # Citations if available
    citations = response.get('citations', [])
    if citations and Config.SHOW_CITATIONS:
        citation_text = "\n*Sources:*\n"
        for i, citation in enumerate(citations[:5], 1):  # Limit to 5 citations
            citation_text += f"{i}. <{citation.get('url', '#')}|{citation.get('title', 'Source')}>\n"
        
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": citation_text}
        })
    
    # Add feedback buttons
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "👍 Helpful"},
                "action_id": "feedback_positive",
                "value": str(response.get('id', ''))
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "👎 Not Helpful"},
                "action_id": "feedback_negative",
                "value": str(response.get('id', ''))
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "📋 Show Sources"},
                "action_id": "show_sources",
                "value": json.dumps(citations[:5])
            }
        ]
    })
    
    return {
        "text": response_text,
        "blocks": blocks
    }

@app.event("app_mention")
async def handle_app_mention(event: Dict[str, Any], client: AsyncWebClient, say):
    """Handle when the bot is mentioned"""
    try:
        user_id = event['user']
        channel_id = event['channel']
        text = event['text']
        thread_ts = event.get('thread_ts') or event['ts']
        
        # Security checks
        if not await security_manager.is_user_allowed(user_id):
            await say("Sorry, you don't have permission to use this bot.", thread_ts=thread_ts)
            return
        
        # Rate limiting
        if not await rate_limiter.check_rate_limit(user_id, channel_id):
            await say(
                "You've reached the rate limit. Please wait a moment before trying again.",
                thread_ts=thread_ts
            )
            return
        
        # Extract query (remove bot mention)
        query = re.sub(r'<@[A-Z0-9]+>', '', text).strip()
        
        if not query:
            # Show starter questions
            agent_id = get_agent_id(channel_id, user_id)
            starter_questions = await starter_questions_manager.get_questions(agent_id)
            await show_starter_questions(say, thread_ts, starter_questions)
            return
        
        # Log analytics
        await analytics.track_query(user_id, channel_id, query)
        
        # Send typing indicator
        await client.chat_postMessage(
            channel=channel_id,
            text="Thinking...",
            thread_ts=thread_ts
        )
        
        # Get agent ID and send query to CustomGPT
        agent_id = get_agent_id(channel_id, user_id)
        conversation_id = conversation_manager.get_or_create_conversation(
            user_id, channel_id, thread_ts
        )
        
        try:
            response = await customgpt_client.send_message(
                project_id=agent_id,
                session_id=conversation_id,
                message=query,
                stream=False
            )
            
            # Format and send response
            formatted_response = await format_response_with_citations(response)
            await say(**formatted_response, thread_ts=thread_ts)
            
            # Log successful response
            await analytics.track_response(user_id, channel_id, agent_id, success=True)
            
        except Exception as e:
            logger.error(f"CustomGPT API error: {str(e)}")
            await say(
                "Sorry, I encountered an error while processing your request. Please try again later.",
                thread_ts=thread_ts
            )
            await analytics.track_response(user_id, channel_id, agent_id, success=False)
    
    except Exception as e:
        logger.error(f"Error handling app mention: {str(e)}")
        await say("An unexpected error occurred. Please try again later.")

@app.event("message")
async def handle_direct_message(event: Dict[str, Any], client: AsyncWebClient, say):
    """Handle direct messages to the bot"""
    # Only process direct messages (not channel messages)
    if event.get('channel_type') == 'im' and not event.get('bot_id'):
        # Reuse app_mention handler logic
        await handle_app_mention(event, client, say)

async def show_starter_questions(say, thread_ts: str, questions: List[str]):
    """Display starter questions with interactive buttons"""
    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*Here are some questions you can ask:*"}
        }
    ]
    
    # Add question buttons
    for i, question in enumerate(questions[:5]):  # Limit to 5 questions
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"• {question}"},
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "Ask this"},
                "action_id": f"ask_question_{i}",
                "value": question
            }
        })
    
    # Add help text
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "You can also ask me anything else about the knowledge base!"
            }
        ]
    })
    
    await say(blocks=blocks, thread_ts=thread_ts)

@app.command("/customgpt")
async def handle_customgpt_command(ack, command, say):
    """Handle /customgpt slash command"""
    await ack()
    
    user_id = command['user_id']
    channel_id = command['channel_id']
    query = command['text']
    
    if not query:
        await say("Please provide a question. Usage: `/customgpt [your question]`")
        return
    
    # Create a fake event to reuse app_mention handler
    fake_event = {
        'user': user_id,
        'channel': channel_id,
        'text': query,
        'ts': str(datetime.now(timezone.utc).timestamp())
    }
    
    await handle_app_mention(fake_event, app.client, say)

@app.command("/customgpt-agent")
async def handle_agent_command(ack, command, say):
    """Handle /customgpt-agent command to switch agents"""
    await ack()
    
    user_id = command['user_id']
    channel_id = command['channel_id']
    agent_id = command['text'].strip()
    
    if not agent_id:
        current_agent = get_agent_id(channel_id, user_id)
        await say(f"Current agent ID: `{current_agent}`\nTo change: `/customgpt-agent [agent_id]`")
        return
    
    # Validate agent ID (must be numeric)
    if not agent_id.isdigit():
        await say("Invalid agent ID. Agent IDs must be numeric.")
        return
    
    # Set agent for channel
    set_agent_id('channel', channel_id, agent_id)
    await say(f"✅ Switched to agent `{agent_id}` for this channel.")
    
    # Clear conversation cache for this channel
    conversation_manager.clear_channel_conversations(channel_id)

@app.command("/customgpt-help")
async def handle_help_command(ack, command, say):
    """Handle /customgpt-help command"""
    await ack()
    
    help_text = """
*CustomGPT Bot Help*

*Basic Usage:*
• Mention me in a channel: `@CustomGPT your question`
• Direct message me with your question
• Use slash command: `/customgpt your question`

*Commands:*
• `/customgpt [question]` - Ask a question
• `/customgpt-agent [agent_id]` - Switch to a different agent/knowledge base
• `/customgpt-help` - Show this help message

*Features:*
• 🧵 Thread support - I maintain context within threads
• 📚 Multiple agents - Switch between different knowledge bases
• 👍 Feedback - Use the reaction buttons to rate responses
• 📋 Citations - Click "Show Sources" to see where information came from
• 🚀 Starter questions - Type "help" or mention me without a question

*Tips:*
• Be specific with your questions for better answers
• Use threads for follow-up questions
• Check the agent ID if you're not getting expected answers

Need more help? Contact your administrator.
    """
    
    await say(help_text)

@app.action("feedback_positive")
async def handle_positive_feedback(ack, body, client):
    """Handle positive feedback button"""
    await ack()
    
    user_id = body['user']['id']
    message_id = body['actions'][0]['value']
    
    # Log feedback
    await analytics.track_feedback(user_id, message_id, 'positive')
    
    # Update button to show it was clicked
    await client.chat_update(
        channel=body['channel']['id'],
        ts=body['message']['ts'],
        text=body['message']['text'],
        blocks=body['message']['blocks'][:-1] + [{
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": "✅ Thanks for your feedback!"}]
        }]
    )

@app.action("feedback_negative")
async def handle_negative_feedback(ack, body, client):
    """Handle negative feedback button"""
    await ack()
    
    user_id = body['user']['id']
    message_id = body['actions'][0]['value']
    
    # Log feedback
    await analytics.track_feedback(user_id, message_id, 'negative')
    
    # Update button to show it was clicked
    await client.chat_update(
        channel=body['channel']['id'],
        ts=body['message']['ts'],
        text=body['message']['text'],
        blocks=body['message']['blocks'][:-1] + [{
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": "Thanks for your feedback. We'll work on improving!"}]
        }]
    )

@app.action("show_sources")
async def handle_show_sources(ack, body, client):
    """Handle show sources button"""
    await ack()
    
    citations = json.loads(body['actions'][0]['value'])
    
    # Create a detailed sources message
    sources_blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "📚 Sources"}
        }
    ]
    
    for i, citation in enumerate(citations, 1):
        sources_blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{i}. {citation.get('title', 'Source')}*\n{citation.get('description', '')}\n<{citation.get('url', '#')}|View Source>"
            }
        })
    
    # Send as ephemeral message
    await client.chat_postEphemeral(
        channel=body['channel']['id'],
        user=body['user']['id'],
        blocks=sources_blocks,
        text="Sources"
    )

@app.action(re.compile("ask_question_.*"))
async def handle_ask_question(ack, body, say):
    """Handle starter question button clicks"""
    await ack()
    
    question = body['actions'][0]['value']
    user_id = body['user']['id']
    channel_id = body['channel']['id']
    thread_ts = body['message'].get('thread_ts') or body['message']['ts']
    
    # Create event and process question
    fake_event = {
        'user': user_id,
        'channel': channel_id,
        'text': question,
        'ts': str(datetime.now(timezone.utc).timestamp()),
        'thread_ts': thread_ts
    }
    
    await handle_app_mention(fake_event, app.client, say)

@app.error
async def global_error_handler(error, body, logger):
    """Global error handler"""
    logger.error(f"Error: {error}")
    logger.error(f"Request body: {body}")

async def main():
    """Main function to start the bot"""
    try:
        # Start the bot
        if Config.SLACK_APP_TOKEN:
            # Socket Mode (for development)
            handler = AsyncSocketModeHandler(app, Config.SLACK_APP_TOKEN)
            await handler.start_async()
        else:
            # HTTP Mode (for production)
            await app.start(port=int(os.environ.get("PORT", 3000)))
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())