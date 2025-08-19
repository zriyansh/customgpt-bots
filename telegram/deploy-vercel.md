# Deploy Telegram Bot to Vercel (Webhook Only)

⚠️ **Note**: Vercel is designed for serverless functions with 10-second timeout. Only suitable for webhook-based bots.

## Step 1: Modify Bot for Webhooks

Create `api/webhook.py`:
```python
from http.server import BaseHTTPRequestHandler
import json
import os
import requests

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CUSTOMGPT_API_KEY = os.environ.get('CUSTOMGPT_API_KEY')
CUSTOMGPT_PROJECT_ID = os.environ.get('CUSTOMGPT_PROJECT_ID')

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update = json.loads(post_data.decode('utf-8'))
        
        # Process update
        if 'message' in update and 'text' in update['message']:
            chat_id = update['message']['chat']['id']
            text = update['message']['text']
            
            # Handle the message
            self.handle_message(chat_id, text)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def handle_message(self, chat_id, text):
        # Send typing action
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendChatAction',
            json={'chat_id': chat_id, 'action': 'typing'}
        )
        
        # Create CustomGPT conversation and get response
        # (simplified for brevity)
        
        # Send response
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={'chat_id': chat_id, 'text': 'Response from bot'}
        )
```

## Step 2: Create vercel.json
```json
{
  "functions": {
    "api/webhook.py": {
      "maxDuration": 10
    }
  },
  "rewrites": [
    { "source": "/api/webhook", "destination": "/api/webhook" }
  ]
}
```

## Step 3: Create requirements.txt
```
requests==2.31.0
```

## Step 4: Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables
vercel env add TELEGRAM_BOT_TOKEN
vercel env add CUSTOMGPT_API_KEY
vercel env add CUSTOMGPT_PROJECT_ID
```

## Step 5: Set Webhook
```python
import requests

BOT_TOKEN = "your_bot_token"
WEBHOOK_URL = "https://your-app.vercel.app/api/webhook"

response = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    json={"url": WEBHOOK_URL}
)
print(response.json())
```

## Limitations on Vercel:
- 10-second execution limit
- No persistent storage
- Cold starts (first request slower)
- No background jobs
- Webhooks only (no polling)