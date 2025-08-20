# Facebook Messenger Bot with CustomGPT Integration

A Facebook Messenger bot that uses CustomGPT's RAG API to answer questions from your agent's knowledge base.

## Features
- 🤖 Responds using CustomGPT agent knowledge
- 🚀 Multiple deployment options (Vercel, Replit, Glitch)
- 🛡️ Built-in rate limiting and security
- 💬 Starter questions and typing indicators
- 📊 Conversation management
- 🔐 Secure webhook verification

## Prerequisites
1. Facebook Page and App
2. CustomGPT API key and Agent ID
3. Node.js 16+ (for local development)

## Quick Start

### 1. Facebook App Setup
1. Go to [Facebook Developers](https://developers.facebook.com)
2. Create a new app (Business type)
3. Add Messenger product
4. Generate Page Access Token
5. Subscribe to webhook events: `messages`, `messaging_postbacks`

### 2. CustomGPT Setup
1. Get your API key from [CustomGPT](https://app.customgpt.ai)
2. Note your Agent ID (project ID)

### 3. Environment Variables
```env
# Facebook
FB_VERIFY_TOKEN=your-random-verify-token
FB_PAGE_ACCESS_TOKEN=your-page-access-token

# CustomGPT
CUSTOMGPT_API_KEY=your-api-key
CUSTOMGPT_AGENT_ID=your-agent-id

# Security
RATE_LIMIT_REQUESTS=20
RATE_LIMIT_WINDOW_MS=60000
```

### 4. Deploy (Choose One)

#### Option A: Vercel (Recommended - Free)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/customgpt-fb-messenger)

#### Option B: Replit (Free with limitations)
1. Fork on Replit
2. Add environment variables
3. Run the bot

#### Option C: Glitch (Free)
1. Remix on Glitch
2. Add .env file
3. Your bot URL: `https://your-project.glitch.me`

### 5. Connect Webhook
1. In Facebook App Dashboard
2. Add webhook URL: `https://your-domain.com/webhook`
3. Verify token: Use your `FB_VERIFY_TOKEN`
4. Subscribe to your page

## Usage

### Basic Chat
Users can message your Facebook page and receive responses from your CustomGPT agent.

### Starter Questions
Type "help" or click "Get Started" to see starter questions.

### Commands
- `help` - Show starter questions
- `reset` - Start new conversation
- `about` - Bot information

## Configuration

### Rate Limiting
Adjust in environment variables:
- `RATE_LIMIT_REQUESTS`: Max requests per window
- `RATE_LIMIT_WINDOW_MS`: Time window in milliseconds

### Customize Responses
Edit `config.js` to modify:
- Welcome message
- Starter questions
- Error messages
- Typing delay

## Security Features
- ✅ Webhook signature verification
- ✅ Rate limiting per user
- ✅ Input sanitization
- ✅ API key encryption
- ✅ Request validation

## Monitoring
- Check logs in your hosting platform
- Monitor rate limit hits
- Track API usage in CustomGPT dashboard

## Troubleshooting
- **Bot not responding**: Check webhook subscription
- **Rate limit errors**: Adjust limits or upgrade plan
- **API errors**: Verify API key and agent ID

## Advanced Features
- Persistent menu with quick actions
- Rich media responses (when available)
- Conversation context management
- Multi-language support

## Support
- CustomGPT Documentation: https://docs.customgpt.ai
- Facebook Messenger Platform: https://developers.facebook.com/docs/messenger-platform