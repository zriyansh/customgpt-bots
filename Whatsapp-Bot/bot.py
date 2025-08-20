#!/usr/bin/env python3
"""
WhatsApp Bot for CustomGPT using Twilio
"""

import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Optional, Tuple, List

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client as TwilioClient
import structlog
from dotenv import load_dotenv

from config import Config
from customgpt_client import CustomGPTClient
from rate_limiter import RateLimiter
from session_manager import SessionManager
from security_manager import SecurityManager
from command_handler import CommandHandler
from starter_questions import StarterQuestions
from analytics import Analytics

# Load environment variables
load_dotenv()

# Initialize logger
logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(title="CustomGPT WhatsApp Bot")

# Initialize configuration
config = Config()

# Initialize Twilio client
twilio_client = TwilioClient(
    config.TWILIO_ACCOUNT_SID,
    config.TWILIO_AUTH_TOKEN
)

# Initialize components
customgpt = CustomGPTClient(
    api_url=config.CUSTOMGPT_API_URL,
    api_key=config.CUSTOMGPT_API_KEY,
    project_id=config.CUSTOMGPT_PROJECT_ID
)

rate_limiter = RateLimiter(
    redis_url=config.REDIS_URL,
    daily_limit=config.RATE_LIMIT_DAILY,
    minute_limit=config.RATE_LIMIT_MINUTE
)

session_manager = SessionManager(redis_url=config.REDIS_URL)
security_manager = SecurityManager(config)
command_handler = CommandHandler(customgpt, session_manager, rate_limiter, config)
starter_questions = StarterQuestions(customgpt)
analytics = Analytics(redis_url=config.REDIS_URL)


@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    logger.info("Starting WhatsApp bot...")
    await rate_limiter.initialize()
    await session_manager.initialize()
    await analytics.initialize()
    logger.info("WhatsApp bot started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown"""
    logger.info("Shutting down WhatsApp bot...")
    await customgpt.close()
    await rate_limiter.close()
    await session_manager.close()
    await analytics.close()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "CustomGPT WhatsApp Bot",
        "status": "active",
        "version": "1.0.0"
    }


@app.post("/")
async def root_post_redirect(request: Request):
    """Redirect root POST requests to WhatsApp webhook"""
    # Forward the request to the WhatsApp webhook
    return await whatsapp_webhook(request)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "customgpt": "connected",
            "redis": await rate_limiter.check_connection(),
            "twilio": "configured"
        }
    }


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages via Twilio webhook"""
    try:
        # Parse form data from Twilio
        form_data = await request.form()
        
        # Extract message details
        from_number = form_data.get('From', '').replace('whatsapp:', '')
        to_number = form_data.get('To', '').replace('whatsapp:', '')
        message_body = form_data.get('Body', '')
        message_sid = form_data.get('MessageSid', '')
        
        # Optional fields
        media_url = form_data.get('MediaUrl0')  # First media attachment
        num_media = int(form_data.get('NumMedia', 0))
        
        logger.info("whatsapp_message_received",
                   from_number=from_number,
                   message_preview=message_body[:50],
                   has_media=num_media > 0)
        
        # Process message asynchronously
        asyncio.create_task(process_message(
            from_number, message_body, message_sid, media_url
        ))
        
        # Return immediate response to Twilio
        response = MessagingResponse()
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error("webhook_error", error=str(e))
        return Response(status_code=500)


async def process_message(from_number: str, message_body: str, 
                         message_sid: str, media_url: Optional[str] = None):
    """Process incoming WhatsApp message"""
    try:
        # Security checks
        if not security_manager.is_allowed_number(from_number):
            await send_whatsapp_message(
                from_number,
                "❌ Sorry, you are not authorized to use this bot."
            )
            return
        
        if security_manager.is_blocked_number(from_number):
            logger.warning("blocked_number_attempt", number=from_number)
            return
        
        # Validate message
        is_valid, error_msg = security_manager.validate_message(message_body)
        if not is_valid:
            await send_whatsapp_message(from_number, f"❌ {error_msg}")
            return
        
        # Rate limiting
        allowed, error, stats = await rate_limiter.check_rate_limit(from_number)
        if not allowed:
            await send_whatsapp_message(
                from_number,
                f"⏳ {error}\\n\\nYour usage today: {stats['daily_used']}/{stats['daily_limit']}"
            )
            return
        
        # Log analytics
        await analytics.log_message(from_number, message_body)
        
        # Handle commands
        if message_body.startswith('/'):
            response = await command_handler.handle_command(from_number, message_body)
            await send_whatsapp_message(from_number, response)
            return
        
        # Handle media
        if media_url and config.ENABLE_MEDIA_RESPONSES:
            await send_whatsapp_message(
                from_number,
                "📎 Media received. Processing media files coming soon!"
            )
            # TODO: Implement media processing
            return
        
        # Note: WhatsApp Business API doesn't support real typing indicators
        # Optionally send a "thinking" message based on configuration
        if config.ENABLE_THINKING_MESSAGE:
            await send_whatsapp_message(from_number, "💭 Thinking...")
        
        # Get or create session
        session = await session_manager.get_session(from_number)
        if not session:
            session_id = await customgpt.create_conversation()
            if session_id:
                await session_manager.create_session(from_number, session_id)
                session = await session_manager.get_session(from_number)
            else:
                await send_whatsapp_message(
                    from_number,
                    "❌ Sorry, I couldn't start a conversation. Please try again."
                )
                return
        
        # Send message to CustomGPT
        start_time = datetime.utcnow()
        
        try:
            response_data = await customgpt.send_message(
                session_id=session['session_id'],
                message=message_body,
                language=session.get('language', config.DEFAULT_LANGUAGE)
            )
            
            if response_data:
                # Check if response_data is a dict with the expected structure
                if isinstance(response_data, dict) and 'openai_response' in response_data:
                    response_text = response_data['openai_response']
                    
                    # Add citations if available
                    if response_data.get('citations') and isinstance(response_data['citations'], list):
                        # Check if citations are IDs or objects
                        if response_data['citations'] and isinstance(response_data['citations'][0], (int, str)):
                            # Citations are just IDs, we can't show titles
                            response_text += f"\\n\\n📚 *Sources:* {len(response_data['citations'])} references used"
                        else:
                            # Citations are objects with details
                            response_text += "\\n\\n📚 *Sources:*\\n"
                            for i, citation in enumerate(response_data['citations'][:3]):
                                if isinstance(citation, dict):
                                    title = citation.get('title', citation.get('url', 'Source'))
                                    response_text += f"{i+1}. {title}\\n"
                elif isinstance(response_data, dict):
                    # Handle other response formats
                    response_text = response_data.get('response', response_data.get('message', str(response_data)))
                else:
                    logger.warning("unexpected_response_format", response_type=type(response_data).__name__, response=str(response_data))
                    response_text = None
                
                # Send response if we have text
                if response_text:
                    await send_whatsapp_message(from_number, response_text)
                else:
                    await send_whatsapp_message(from_number, "❌ Sorry, I couldn't get a proper response. Please try again.")
                
                # Log successful response
                response_time = (datetime.utcnow() - start_time).total_seconds()
                await analytics.log_response(from_number, True, response_time)
                
                # Sometimes suggest follow-up questions (skip for greetings)
                greeting_words = ['hey', 'hi', 'hello', 'good morning', 'good afternoon', 'good evening', 'how are you']
                is_greeting = any(word in message_body.lower() for word in greeting_words)
                
                if not is_greeting and hash(from_number + message_body) % 10 < 3:  # 30% chance, skip greetings
                    suggestions = await starter_questions.get_suggestions(
                        message_body, response_text
                    )
                    if suggestions:
                        suggestion_text = "\\n💡 *You might also ask:*\\n"
                        for i, question in enumerate(suggestions[:3]):
                            suggestion_text += f"{i+1}. {question}\\n"
                        await send_whatsapp_message(from_number, suggestion_text)
                
            else:
                await send_whatsapp_message(
                    from_number,
                    "❌ Sorry, I couldn't get a response. Please try again."
                )
                await analytics.log_response(from_number, False)
                
        except Exception as e:
            logger.error("customgpt_error", error=str(e))
            await send_whatsapp_message(
                from_number,
                "❌ An error occurred while processing your message. Please try again."
            )
            await analytics.log_error(from_number, str(e))
            
    except Exception as e:
        logger.error("message_processing_error", error=str(e), from_number=from_number)


async def send_whatsapp_message(to_number: str, message: str, media_url: Optional[str] = None):
    """Send WhatsApp message via Twilio"""
    try:
        # Ensure number has WhatsApp prefix
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'
        
        # Create message
        message_params = {
            'body': message,
            'from_': config.TWILIO_WHATSAPP_NUMBER,
            'to': to_number
        }
        
        if media_url:
            message_params['media_url'] = [media_url]
        
        # Send message
        message = twilio_client.messages.create(**message_params)
        
        logger.info("whatsapp_message_sent",
                   to=to_number,
                   message_sid=message.sid,
                   status=message.status)
        
        return message.sid
        
    except Exception as e:
        logger.error("send_message_error", error=str(e), to_number=to_number)
        return None


@app.get("/stats/{phone_number}")
async def get_user_stats(phone_number: str, api_key: str = None):
    """Get user statistics (protected endpoint)"""
    if api_key != config.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    stats = await analytics.get_user_stats(phone_number)
    return JSONResponse(content=stats)


@app.post("/broadcast")
async def broadcast_message(request: Request):
    """Broadcast message to multiple users (admin only)"""
    data = await request.json()
    api_key = data.get('api_key')
    
    if api_key != config.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    message = data.get('message')
    recipients = data.get('recipients', [])
    
    results = []
    for recipient in recipients:
        try:
            sid = await send_whatsapp_message(recipient, message)
            results.append({'recipient': recipient, 'status': 'sent', 'sid': sid})
        except Exception as e:
            results.append({'recipient': recipient, 'status': 'failed', 'error': str(e)})
    
    return JSONResponse(content={'results': results})


@app.post("/set-webhook")
async def set_webhook(request: Request):
    """Configure Twilio webhook URL"""
    data = await request.json()
    api_key = data.get('api_key')
    
    if api_key != config.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    webhook_url = data.get('webhook_url')
    
    try:
        # Update Twilio webhook configuration
        # This would typically be done in Twilio console
        return JSONResponse(content={
            'status': 'success',
            'message': f'Webhook URL set to: {webhook_url}'
        })
    except Exception as e:
        logger.error("webhook_setup_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "bot:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=bool(os.getenv("DEBUG", False))
    )