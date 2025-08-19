# Telegram Bot for CustomGPT - Vercel Deployment

This is a webhook-based Telegram bot that integrates with CustomGPT.ai, designed to run on Vercel's serverless platform.

## Features

- 🤖 AI-powered responses using CustomGPT knowledge base
- 🚀 Serverless deployment on Vercel (free tier)
- ⚡ Fast webhook-based message handling
- 💬 Conversation context maintained during session
- 🎯 Example starter questions
- 🔄 Clear conversation command

## Limitations

### Vercel's 10-Second Timeout
Vercel serverless functions have a **10-second execution timeout** on the free tier. This means:
- Each webhook request (Telegram message) must complete within 10 seconds
- This includes: receiving message → calling CustomGPT API → sending response
- If CustomGPT takes too long to respond, the function will timeout
- The bot uses 8-second timeouts for API calls to stay within limits

### Other Limitations
- **No persistent storage**: Sessions reset on cold starts
- **No rate limiting**: Each request is independent
- **Cold starts**: First message after inactivity may be slower
- **No background tasks**: Can't do async processing

## Setup Instructions

### 1. Prerequisites
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- CustomGPT API Key and Project ID
- Vercel account (free at [vercel.com](https://vercel.com))
- Git installed locally

### 2. Clone/Download the Project
```bash
# Clone or download this folder
cd telegram/vercel-bot
```

### 3. Deploy to Vercel

#### Option A: Deploy via Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy (follow prompts)
vercel

# Set environment variables
vercel env add TELEGRAM_BOT_TOKEN production
vercel env add CUSTOMGPT_API_KEY production
vercel env add CUSTOMGPT_PROJECT_ID production

# Redeploy to apply env vars
vercel --prod
```

#### Option B: Deploy via GitHub
1. Push code to GitHub repository
2. Connect repository to Vercel
3. Add environment variables in Vercel dashboard
4. Deploy

### 4. Set Telegram Webhook
After deployment, set your bot's webhook:

```python
import requests

BOT_TOKEN = "your_bot_token_here"
WEBHOOK_URL = "https://your-project.vercel.app/api/webhook"

response = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    json={"url": WEBHOOK_URL}
)
print(response.json())
```

Or use curl:
```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-project.vercel.app/api/webhook"}'
```

### 5. Test Your Bot
1. Open Telegram and search for your bot
2. Send `/start` to begin
3. Ask any question!

## Environment Variables

Set these in Vercel dashboard or via CLI:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `CUSTOMGPT_API_KEY`: Your CustomGPT API key  
- `CUSTOMGPT_PROJECT_ID`: Your CustomGPT project ID

## Commands

- `/start` - Welcome message with example questions
- `/help` - Show available commands
- `/clear` - Clear conversation history

## How It Works

1. **Webhook Reception**: Telegram sends updates to `/api/webhook`
2. **Message Processing**: Bot processes commands or forwards to CustomGPT
3. **Session Management**: Maintains conversation context in memory
4. **Response Delivery**: Sends CustomGPT response back to user

## Development

### Local Testing
```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="your_token"
export CUSTOMGPT_API_KEY="your_key"
export CUSTOMGPT_PROJECT_ID="your_project_id"

# Run locally
python api/webhook.py
```

### Project Structure
```
vercel-bot/
├── api/
│   └── webhook.py      # Main webhook handler
├── vercel.json         # Vercel configuration
├── requirements.txt    # Python dependencies (none needed)
└── README.md          # This file
```

## Troubleshooting

### Bot not responding
1. Check webhook is set correctly: `https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
2. Verify environment variables in Vercel dashboard
3. Check Vercel function logs for errors

### Timeout errors
- CustomGPT API might be slow - the bot has 8-second timeout
- Consider implementing a "thinking..." message for long responses
- For complex queries, responses might timeout

### Sessions reset frequently
- This is normal behavior on serverless platforms
- Each cold start resets the in-memory session cache
- Consider using a database for persistent sessions (requires paid tier)

## Alternatives

If you need:
- **Persistent sessions**: Use Railway or Render with a database
- **No timeout limits**: Use a VPS or dedicated hosting
- **Rate limiting**: Deploy the full Python bot with polling
- **Background tasks**: Consider AWS Lambda with SQS

## License

MIT

## Support

For issues with:
- Telegram Bot API: Check [Telegram Bot Documentation](https://core.telegram.org/bots/api)
- CustomGPT API: Refer to CustomGPT documentation
- Vercel deployment: See [Vercel Documentation](https://vercel.com/docs)