import os
import json
import logging
from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
from datetime import datetime
import hashlib
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CUSTOMGPT_API_KEY = os.environ.get('CUSTOMGPT_API_KEY')
CUSTOMGPT_PROJECT_ID = os.environ.get('CUSTOMGPT_PROJECT_ID')

# Simple in-memory cache for sessions (resets on each cold start)
session_cache = {}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update = json.loads(post_data.decode('utf-8'))
            
            # Log the update
            logger.info(f"Received update: {update.get('update_id')}")
            
            # Process the update
            self.process_update(update)
            
            # Always return 200 OK
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            
        except Exception as e:
            logger.error(f"Error in webhook: {str(e)}")
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
    
    def process_update(self, update):
        """Process incoming Telegram update"""
        # Handle message
        if 'message' in update and 'text' in update['message']:
            message = update['message']
            chat_id = message['chat']['id']
            text = message['text']
            user_id = message['from']['id']
            
            # Handle commands
            if text.startswith('/'):
                self.handle_command(chat_id, text)
            else:
                # Handle regular message
                self.handle_message(chat_id, user_id, text)
        
        # Handle callback queries
        elif 'callback_query' in update:
            callback = update['callback_query']
            self.answer_callback_query(callback['id'])
            
            if callback['data'].startswith('ask_'):
                question = callback['data'][4:]
                chat_id = callback['message']['chat']['id']
                user_id = callback['from']['id']
                
                # Delete the keyboard message
                self.delete_message(chat_id, callback['message']['message_id'])
                
                # Send the question
                self.send_message(chat_id, f"You asked: _{question}_", parse_mode='Markdown')
                
                # Process the question
                self.handle_message(chat_id, user_id, question)
    
    def handle_command(self, chat_id, command):
        """Handle bot commands"""
        cmd = command.split()[0].lower()
        
        if cmd == '/start':
            keyboard = {
                'inline_keyboard': [
                    [{'text': '🎯 General Questions', 'callback_data': 'examples_general'}],
                    [{'text': '💻 Technical Questions', 'callback_data': 'examples_technical'}],
                    [{'text': '🆘 Support Questions', 'callback_data': 'examples_support'}]
                ]
            }
            
            welcome_text = """🤖 Welcome to CustomGPT Bot!

I'm powered by AI and ready to help you with your questions.

You can:
• Ask me questions directly
• Use /help to see available commands
• Click the buttons below for example questions
• Use /stats to see your usage

How can I assist you today?"""
            
            self.send_message(chat_id, welcome_text, reply_markup=keyboard)
            
        elif cmd == '/help':
            help_text = """📚 **Available Commands:**

/start - Start a new conversation
/help - Show this help message
/clear - Clear conversation history

**Tips:**
• Just type your question naturally
• I'll remember our conversation context

Need more help? Just ask!"""
            
            self.send_message(chat_id, help_text, parse_mode='Markdown')
            
        elif cmd == '/clear':
            # Clear session from cache
            session_cache.pop(str(chat_id), None)
            self.send_message(chat_id, "✅ Conversation cleared! Start fresh by sending me a message.")
            
        else:
            self.send_message(chat_id, "Unknown command. Try /help")
    
    def handle_message(self, chat_id, user_id, text):
        """Handle regular messages"""
        try:
            # Send typing action
            self.send_chat_action(chat_id, 'typing')
            
            # Get or create session
            session_id = session_cache.get(str(user_id))
            
            if not session_id:
                # Create new conversation
                session_id = self.create_conversation()
                if not session_id:
                    self.send_message(chat_id, "❌ Sorry, I couldn't start a conversation. Please try again later.")
                    return
                
                # Cache the session
                session_cache[str(user_id)] = session_id
            
            # Send message to CustomGPT
            response = self.send_to_customgpt(session_id, text)
            
            if response and 'openai_response' in response:
                self.send_message(chat_id, response['openai_response'], parse_mode='Markdown')
            else:
                self.send_message(chat_id, "❌ I couldn't get a response. Please try again.")
                
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            self.send_message(chat_id, "❌ An error occurred. Please try again later.")
    
    def create_conversation(self):
        """Create a new CustomGPT conversation"""
        url = f"https://app.customgpt.ai/api/v1/projects/{CUSTOMGPT_PROJECT_ID}/conversations"
        
        data = json.dumps({
            'name': f'Telegram Chat {datetime.now().isoformat()}'
        }).encode('utf-8')
        
        headers = {
            'Authorization': f'Bearer {CUSTOMGPT_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=8) as response:
                result = json.loads(response.read().decode('utf-8'))
                session_id = result.get('data', {}).get('session_id')
                logger.info(f"Created conversation: {session_id}")
                return session_id
        except Exception as e:
            logger.error(f"Create conversation error: {str(e)}")
            return None
    
    def send_to_customgpt(self, session_id, message):
        """Send message to CustomGPT"""
        url = f"https://app.customgpt.ai/api/v1/projects/{CUSTOMGPT_PROJECT_ID}/conversations/{session_id}/messages"
        
        params = urllib.parse.urlencode({
            'stream': 'false',
            'lang': 'en'
        })
        
        full_url = f"{url}?{params}"
        
        data = json.dumps({
            'prompt': message,
            'response_source': 'default'
        }).encode('utf-8')
        
        headers = {
            'Authorization': f'Bearer {CUSTOMGPT_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        try:
            req = urllib.request.Request(full_url, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=8) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('data')
        except Exception as e:
            logger.error(f"CustomGPT error: {str(e)}")
            return None
    
    def send_message(self, chat_id, text, reply_markup=None, parse_mode=None):
        """Send message to Telegram"""
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        
        data = {
            'chat_id': chat_id,
            'text': text
        }
        
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        
        if parse_mode:
            data['parse_mode'] = parse_mode
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                logger.info(f"Message sent to {chat_id}")
        except Exception as e:
            logger.error(f"Send message error: {str(e)}")
    
    def send_chat_action(self, chat_id, action):
        """Send chat action to Telegram"""
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendChatAction"
        
        data = json.dumps({
            'chat_id': chat_id,
            'action': action
        }).encode('utf-8')
        
        try:
            req = urllib.request.Request(
                url,
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            urllib.request.urlopen(req, timeout=2)
        except:
            pass  # Don't fail if action doesn't send
    
    def answer_callback_query(self, callback_query_id):
        """Answer callback query"""
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
        
        data = json.dumps({
            'callback_query_id': callback_query_id
        }).encode('utf-8')
        
        try:
            req = urllib.request.Request(
                url,
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            urllib.request.urlopen(req, timeout=2)
        except:
            pass
    
    def delete_message(self, chat_id, message_id):
        """Delete a message"""
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
        
        data = json.dumps({
            'chat_id': chat_id,
            'message_id': message_id
        }).encode('utf-8')
        
        try:
            req = urllib.request.Request(
                url,
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            urllib.request.urlopen(req, timeout=2)
        except:
            pass

# For local testing
if __name__ == '__main__':
    from http.server import HTTPServer
    server = HTTPServer(('localhost', 8000), handler)
    print('Starting server at http://localhost:8000')
    server.serve_forever()