# CustomGPT Telegram Bot

A Telegram bot that integrates with CustomGPT.ai to provide AI-powered conversations through your agent's knowledge base.

## Features

- 🤖 **AI-Powered Conversations**: Uses your CustomGPT agent to answer questions
- 💬 **Context-Aware**: Maintains conversation context within sessions
- 🎯 **Starter Questions**: Pre-configured question categories for easy onboarding
- 🔒 **Rate Limiting**: Built-in protection against abuse (configurable limits)
- 📊 **Usage Statistics**: Track daily usage and remaining quota
- 🌐 **Simple Deployment**: Works on free hosting providers
- 🚀 **Lightweight**: No database required, uses in-memory caching

## Prerequisites

- Python 3.11+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- CustomGPT.ai API Key and Project ID

## Quick Start

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the prompts
3. Save the bot token you receive

### 2. Get CustomGPT Credentials

1. Log in to [CustomGPT.ai](https://app.customgpt.ai)
2. Go to your agent/project settings
3. Find your Project ID and API Key

### 3. Local Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd customgpt-integrations/telegram

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.simple .env

# Edit .env with your credentials
# TELEGRAM_BOT_TOKEN=your_bot_token
# CUSTOMGPT_API_KEY=your_api_key
# CUSTOMGPT_PROJECT_ID=your_project_id

# Run the bot
python bot.py
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Your Telegram bot token |
| `CUSTOMGPT_API_KEY` | Yes | - | Your CustomGPT API key |
| `CUSTOMGPT_PROJECT_ID` | Yes | - | Your CustomGPT project/agent ID |
| `CUSTOMGPT_API_URL` | No | https://app.customgpt.ai | API endpoint |
| `RATE_LIMIT_PER_USER_PER_DAY` | No | 100 | Daily message limit per user |
| `RATE_LIMIT_PER_USER_PER_MINUTE` | No | 5 | Per-minute message limit |

## Deployment

### Free Hosting Options

#### 1. Render.com (Recommended)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Click the button above or manually:
2. Create account at [render.com](https://render.com)
3. New > Background Worker
4. Connect your GitHub repo
5. Use `render.yaml` configuration
6. Add environment variables in dashboard
7. Deploy!

#### 2. Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

1. Click deploy button or go to [railway.app](https://railway.app)
2. New Project > Deploy from GitHub
3. Select your repository
4. Add environment variables
5. Deploy automatically

#### 3. Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Create app
flyctl launch

# Set secrets
flyctl secrets set TELEGRAM_BOT_TOKEN=xxx
flyctl secrets set CUSTOMGPT_API_KEY=xxx
flyctl secrets set CUSTOMGPT_PROJECT_ID=xxx

# Deploy
flyctl deploy
```

#### 4. Heroku

```bash
# Create app
heroku create your-bot-name

# Set environment
heroku config:set TELEGRAM_BOT_TOKEN=xxx
heroku config:set CUSTOMGPT_API_KEY=xxx
heroku config:set CUSTOMGPT_PROJECT_ID=xxx

# Deploy
git push heroku main
```

## Bot Commands

- `/start` - Start a new conversation
- `/help` - Show help information
- `/examples` - Show example questions
- `/stats` - View usage statistics
- `/clear` - Clear conversation history

## Extending the Bot

### Adding Custom Commands

```python
# In bot.py, add a new handler:
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Your custom response")

# Register it in main():
application.add_handler(CommandHandler("custom", custom_command))
```

### Customizing Rate Limits

Modify the environment variables or update the code:

```python
# In bot.py
DAILY_LIMIT = int(os.getenv('RATE_LIMIT_PER_USER_PER_DAY', '100'))
MINUTE_LIMIT = int(os.getenv('RATE_LIMIT_PER_USER_PER_MINUTE', '5'))
```

### Adding Webhooks (for production)

For better performance, you can use webhooks instead of polling:

```python
# Replace run_polling with:
application.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get('PORT', 8443)),
    url_path=BOT_TOKEN,
    webhook_url=f"https://your-app.com/{BOT_TOKEN}"
)
```

## Security Best Practices

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Use environment variables** for all sensitive data
3. **Enable rate limiting** to prevent abuse
4. **Validate user input** before sending to API
5. **Monitor usage** through stats and logs
6. **Set up allowed users** list if needed (modify code)

## Monitoring

The bot includes basic health check endpoints when deployed:

- `/health` - Basic health status
- `/metrics` - Usage metrics

## Troubleshooting

### Bot not responding

1. Check bot token is correct
2. Ensure bot is not already running elsewhere
3. Check logs for errors

### API errors

1. Verify API key and Project ID
2. Check rate limits on CustomGPT
3. Ensure API URL is correct

### Rate limit issues

1. Adjust limits in environment variables
2. Clear cache if testing locally
3. Check user statistics with `/stats`

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT