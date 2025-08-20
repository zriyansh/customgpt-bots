# WhatsApp Bot for CustomGPT

A WhatsApp bot that integrates with CustomGPT's API to provide intelligent responses from your agent's knowledge base.

![CustomGPT WhatsApp Bot](../images/customgpt_whatsapp.jpeg)

## 📚 Documentation

- [🚀 **Deployment Guide**](DEPLOYMENT.md) - Deploy to Railway, Render, Fly.io, or Google Apps Script
- [🌐 **ngrok Setup Guide**](NGROK_SETUP.md) - Detailed instructions for local testing with ngrok
- [❓ **Why Twilio & Redis?**](WHY_TWILIO_REDIS.md) - Explanation of technology choices and alternatives
- [👩‍💻 **Developer Guide**](CLAUDE.md) - Technical documentation for developers
- [📱 **Google Apps Script**](google-apps-script/README.md) - Alternative free hosting option

## Features

- 🤖 **AI-Powered Responses**: Uses CustomGPT's knowledge base
- 🔒 **Security**: Rate limiting, user authentication, query validation
- 💬 **Rich Interactions**: Starter questions, inline buttons, media support
- 📊 **Analytics**: Usage tracking and statistics
- 🌍 **Multi-language Support**: Configurable response language
- ⚡ **Performance**: Response caching, session management
- 🚀 **Easy Deployment**: Multiple free hosting options

## Prerequisites

- Python 3.8+ 
- CustomGPT API credentials (API key and Agent ID)
- Twilio account with WhatsApp sandbox access

## Quick Start

### 1. Clone and Install

```bash
cd whatsapp
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file:

```env
# CustomGPT Configuration
CUSTOMGPT_API_KEY=your_api_key_here
CUSTOMGPT_PROJECT_ID=your_agent_id_here
CUSTOMGPT_API_URL=https://app.customgpt.ai

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Rate Limiting
RATE_LIMIT_DAILY=100
RATE_LIMIT_MINUTE=5
RATE_LIMIT_HOUR=30

# Security
ALLOWED_NUMBERS=+1234567890,+0987654321  # Optional: Whitelist specific numbers
BLOCKED_NUMBERS=+1111111111              # Optional: Block specific numbers
MAX_MESSAGE_LENGTH=500

# Redis (for production)
REDIS_URL=redis://localhost:6379         # Optional: For persistent rate limiting

# Features
ENABLE_VOICE_MESSAGES=true
ENABLE_MEDIA_RESPONSES=true
ENABLE_LOCATION_SHARING=false
DEFAULT_LANGUAGE=en
```

### 3. Run the Bot

**Important**: You need TWO terminal windows for local development:

**Terminal 1 - Run the bot**:
```bash
# Development mode
python bot.py

# OR Production mode with uvicorn
uvicorn bot:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Run ngrok** (for local testing):
```bash
# First time: Sign up at https://dashboard.ngrok.com and get your authtoken
ngrok config add-authtoken YOUR_AUTH_TOKEN

# Then expose your local server
ngrok http 8000
```

📌 **Both must be running simultaneously** for the bot to work!

### 4. Configure Twilio Webhook

1. Copy the HTTPS URL from ngrok (e.g., `https://abc123.ngrok-free.app`)
2. In [Twilio Console](https://console.twilio.com), go to Messaging → Try it out → Send a WhatsApp message
3. Set the webhook URL to: `https://YOUR-NGROK-URL.ngrok-free.app/webhook/whatsapp`
4. Save the configuration
5. Join the sandbox by sending "join [your-keyword]" to the Twilio WhatsApp number
6. Test by sending a message!

⚠️ **Note**: ngrok URL changes each time you restart it. Update Twilio webhook accordingly.

📖 **Detailed setup guide**: See [NGROK_SETUP.md](NGROK_SETUP.md)

### 5. Important: WhatsApp Sandbox Limitations

**You're currently using the FREE Twilio WhatsApp Sandbox**, which has these limitations:

- **Join Required**: Users must first send "join [your-keyword]" to activate
- **24-Hour Window**: You can only reply within 24 hours of receiving a message
- **Shared Number**: Messages come from Twilio's number, not your own
- **Development Only**: Not suitable for production use

**After 24 hours of inactivity**, you can only send pre-approved template messages (requires paid account).

**To get your own WhatsApp Business number** (Required for production):
1. **Upgrade to paid Twilio account** (trial accounts can't register WhatsApp senders)
2. Register your WhatsApp Business Profile
3. Get Facebook Business verification
4. Submit message templates for approval
5. Monthly fees apply + per-message costs

Learn more: [Twilio WhatsApp API Docs](https://www.twilio.com/docs/whatsapp/api)

### Sandbox vs Production Comparison

| Feature | Sandbox (Free) | Production (Paid) |
|---------|---------------|-------------------|
| **Cost** | Free | ~$15/month + $0.005/message |
| **Phone Number** | Twilio's shared number | Your own business number |
| **User Onboarding** | Must send "join [keyword]" | Direct messaging |
| **Message Window** | 24 hours after user message | 24 hours + templates |
| **Business Profile** | Twilio's profile | Your verified business |
| **Suitable For** | Development & testing | Real customers |
| **Account Type** | Trial account OK | Paid account required |
| **Setup Time** | 5 minutes | 2-5 days (verification) |

## Implementation Options

### Option 1: Twilio WhatsApp API (Currently Implemented) ✅

- **Pros**: Official API, reliable, quick setup, free sandbox
- **Cons**: Costs for production, requires Twilio account
- **Best for**: Rapid development, business use, production deployments

### Option 2: Meta WhatsApp Business API (Direct)

- **Pros**: Direct integration, no middleman fees
- **Cons**: Complex setup, business verification required, longer approval
- **Best for**: Large enterprises with dedicated infrastructure

### Option 3: Google Apps Script (Alternative Implementation)

- **Pros**: Free hosting, easy deployment, no server needed
- **Cons**: Limited features, requires Twilio, **may timeout on long responses**
- **Best for**: Simple bots, testing, short responses
- **⚠️ Warning**: May timeout with complex queries (only "Thinking..." message sent)

## Free Hosting Options

📖 **Full deployment guide with step-by-step instructions**: [DEPLOYMENT.md](DEPLOYMENT.md)

### 1. Railway.app (Recommended)
- Free tier: $5 credit/month
- Easy deployment with GitHub
- Persistent storage support
- [Quick Deploy Guide](DEPLOYMENT.md#railway-recommended)

### 2. Render.com
- Free tier: 750 hours/month
- Automatic deploys from GitHub
- Good for web services
- [Quick Deploy Guide](DEPLOYMENT.md#render)

### 3. Fly.io
- Free tier: 3 shared VMs
- Global deployment
- Good performance
- [Quick Deploy Guide](DEPLOYMENT.md#flyio)

### 4. Google Apps Script
- Always free (with quotas)
- No server needed
- Simple implementation
- [Full Guide](google-apps-script/README.md)

### 5. Other Free Options
- **Koyeb**: 2 apps free
- **Cyclic.sh**: Generous free tier
- **Deta Space**: Always free
- [See all options](DEPLOYMENT.md#other-free-alternatives)

## Deployment Guide

### Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Deploy to Render

1. Push code to GitHub
2. Connect GitHub repo in Render dashboard
3. Set environment variables
4. Deploy

### Deploy to Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

## Security Features

1. **Rate Limiting**
   - Per-user daily/hourly/minute limits
   - Automatic reset at midnight
   - Customizable limits per user tier

2. **Message Validation**
   - Maximum message length enforcement
   - Spam detection
   - SQL injection prevention
   - Profanity filtering (optional)

3. **User Authentication**
   - Phone number whitelist/blacklist
   - Admin commands protection
   - Session management

4. **Data Protection**
   - No message logging by default
   - Encrypted session storage
   - GDPR compliance ready

## Bot Commands

- `/start` - Start conversation and show menu
- `/help` - Show available commands
- `/examples` - Show example questions
- `/stats` - View usage statistics
- `/language [code]` - Change response language
- `/clear` - Clear conversation history
- `/feedback` - Submit feedback

## Advanced Features

### Starter Questions
The bot automatically suggests relevant questions based on:
- Your CustomGPT agent's knowledge base
- User's previous queries
- Popular questions

### Rich Media Support
- Send and receive images
- Voice message transcription
- Document handling
- Location-based queries

### Multi-turn Conversations
- Context retention across messages
- Session management
- Conversation history

### Analytics Dashboard
- User engagement metrics
- Popular queries
- Response times
- Error tracking

## Google Apps Script Alternative

For a simpler implementation using Google Apps Script:

1. Uses Twilio for WhatsApp integration
2. Free Google hosting
3. Limited to 6 minutes execution time
4. See `google-apps-script/` folder for implementation

## Quick Setup Checklist

Before troubleshooting, ensure:
- [ ] Bot is running (`python bot.py`) - Terminal 1
- [ ] ngrok is running (`ngrok http 8000`) - Terminal 2
- [ ] Webhook URL is updated in Twilio Console
- [ ] You've joined the sandbox (sent "join [keyword]")
- [ ] Your phone number is in `ALLOWED_NUMBERS` in `.env`

## Troubleshooting

### Common Issues

1. **Webhook not receiving messages**
   - Verify webhook URL in Twilio console
   - Check ngrok tunnel if testing locally
   - Ensure bot is running and accessible

2. **Authentication Error - Invalid Username**
   - Your Account SID should start with "AC" (not "US" or other prefixes)
   - Verify credentials in Twilio Console
   - Test with curl command below

3. **Rate limit errors**
   - Check Redis connection (optional)
   - Verify rate limit settings
   - Admin numbers get 10x higher limits

4. **CustomGPT API errors**
   - Verify API credentials
   - Check agent ID
   - Ensure agent is active

### Testing Twilio Credentials

Test your Twilio setup with this curl command:

```bash
curl 'https://api.twilio.com/2010-04-01/Accounts/YOUR_ACCOUNT_SID/Messages.json' -X POST \
--data-urlencode 'To=whatsapp:+1234567890' \
--data-urlencode 'From=whatsapp:+14155238886' \
--data-urlencode 'Body=Your appointment is coming up on July 21 at 3PM' \
-u YOUR_ACCOUNT_SID:YOUR_AUTH_TOKEN
```

Replace:
- `YOUR_ACCOUNT_SID`: Your Twilio Account SID (starts with AC)
- `YOUR_AUTH_TOKEN`: Your Twilio Auth Token
- `+1234567890`: Your WhatsApp number (recipient)
- `+14155238886`: Your Twilio sandbox number (or your WhatsApp Business number)

**Example Request**:
```bash
curl 'https://api.twilio.com/2010-04-01/Accounts/ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/Messages.json' -X POST \
--data-urlencode 'To=whatsapp:+917978307903' \
--data-urlencode 'From=whatsapp:+14155238886' \
--data-urlencode 'Body=Your appointment is coming up on July 21 at 3PM' \
-u ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:your_auth_token_here
```

**Example Response** (201 - CREATED):
```json
{
  "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "api_version": "2010-04-01",
  "body": "Your appointment is coming up on July 21 at 3PM",
  "date_created": "Tue, 19 Aug 2025 10:11:51 +0000",
  "date_sent": null,
  "date_updated": "Tue, 19 Aug 2025 10:11:51 +0000",
  "direction": "outbound-api",
  "error_code": null,
  "error_message": null,
  "from": "whatsapp:+14155238886",
  "num_media": "0",
  "num_segments": "1",
  "price": null,
  "price_unit": null,
  "sid": "SM13a915bc4fc70addfd159d4cba2b67d8",
  "status": "queued",
  "subresource_uris": {
    "media": "/2010-04-01/Accounts/.../Messages/.../Media.json"
  },
  "to": "whatsapp:+917978307903",
  "uri": "/2010-04-01/Accounts/.../Messages/SM13a915bc4fc70addfd159d4cba2b67d8.json"
}
```

**Status Codes**:
- `201 Created`: Message successfully queued for delivery
- `400 Bad Request`: Invalid parameters (check phone number format)
- `401 Unauthorized`: Invalid credentials
- `429 Too Many Requests`: Rate limit exceeded

### Debugging Tips

1. **Check logs**: The bot logs all incoming messages
2. **Test health endpoint**: `curl http://localhost:8000/health`
3. **Verify webhook**: Messages should appear in terminal
4. **Check Twilio Console**: Look for webhook logs and errors

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT