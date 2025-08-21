# CustomGPT Slack Bot Integration

A Slack bot that integrates with CustomGPT's RAG (Retrieval-Augmented Generation) platform to provide intelligent responses based on your agent's knowledge base.

![CustomGPT Slack Bot](../images/customgpt_slack.jpeg)
![CustomGPT Slack Bot Interface](../images/customgpt_slack2.jpeg)

## Features

- **Multi-Agent Support**: Specify different agent IDs to access different knowledge bases
- **Starter Questions**: Display helpful starter questions to guide users
- **Rate Limiting**: Prevent abuse with configurable rate limits per user/channel
- **Security**: API key management, user authentication, and input validation
- **Conversation Management**: Maintain conversation context across messages
- **Interactive UI**: Buttons, modals, and rich formatting
- **Thread Support**: Keep conversations organized in threads with automatic follow-up responses
- **Thread Follow-ups**: Once mentioned in a thread, bot responds to all messages without requiring mentions
- **Error Handling**: Graceful error messages and retry logic
- **Analytics**: Track usage and performance metrics

## Prerequisites

- Python 3.8+
- Slack Workspace with admin access
- CustomGPT account with API access
- API Key from CustomGPT
- Agent/Project ID from CustomGPT

## Step-by-Step Slack App Setup

### 1. Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App"
3. Choose "From scratch"
4. Enter app name (e.g., "CustomGPT Bot")
5. Select your workspace
6. Click "Create App"

### 2. Configure Bot Permissions

Navigate to "OAuth & Permissions" and add these scopes:

**Bot Token Scopes:**
- `app_mentions:read` - Read mentions of the bot
- `channels:history` - View messages in public channels
- `channels:read` - View basic channel info
- `chat:write` - Send messages
- `commands` - Add slash commands
- `groups:history` - View messages in private channels
- `groups:read` - View basic private channel info
- `im:history` - View direct messages
- `im:read` - View basic DM info
- `im:write` - Send direct messages
- `users:read` - View user info

### 3. Enable Event Subscriptions

1. Go to "Event Subscriptions"
2. Turn on "Enable Events"
3. Add these bot events:
   - `app_mention` - When someone mentions the bot
   - `message.im` - Direct messages to the bot
   - `message.channels` - Messages in channels (optional)
4. You'll need your Request URL later (after deploying)

### 4. Create Slash Commands (Optional)

Go to "Slash Commands" and create:
- `/customgpt [query]` - Query the bot directly
- `/customgpt-agent [agent_id]` - Switch between agents
- `/customgpt-help` - Show help information

### 5. Install App to Workspace

1. Go to "OAuth & Permissions"
2. Click "Install to Workspace"
3. Authorize the permissions
4. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

## Installation & Setup

### Option 1: Traditional Python Deployment

```bash
# Clone or create the project
cd /path/to/customgpt-integrations/slack

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_SIGNING_SECRET="your-signing-secret"
export CUSTOMGPT_API_KEY="your-customgpt-api-key"
export CUSTOMGPT_PROJECT_ID="your-default-project-id"

# Run the bot
python bot.py
```

### Option 2: Google Apps Script Deployment

Google Apps Script provides a free, serverless option for hosting the bot:

1. Go to [script.google.com](https://script.google.com)
2. Create a new project
3. Copy the Google Apps Script code (see `google-apps-script/Code.gs`)
4. Set up script properties:
   - `SLACK_BOT_TOKEN`
   - `SLACK_SIGNING_SECRET`
   - `CUSTOMGPT_API_KEY`
   - `CUSTOMGPT_PROJECT_ID`
5. Deploy as Web App
6. Use the Web App URL as your Slack Request URL

### Option 3: Docker Deployment

```bash
# Build the image
docker build -t customgpt-slack-bot .

# Run with environment variables
docker run -d \
  -e SLACK_BOT_TOKEN="xoxb-your-token" \
  -e SLACK_SIGNING_SECRET="your-secret" \
  -e CUSTOMGPT_API_KEY="your-api-key" \
  -e CUSTOMGPT_PROJECT_ID="your-project-id" \
  -p 3000:3000 \
  customgpt-slack-bot
```

## Free Hosting Options

### 1. **Google Apps Script** (Recommended for simple bots)
- ✅ Completely free
- ✅ No credit card required
- ✅ Auto-scaling
- ⚠️ 6-minute execution time limit
- ⚠️ Limited to 20MB for responses

### 2. **Railway.app**
- ✅ $5 free credit monthly
- ✅ Easy deployment from GitHub
- ✅ Auto-SSL
- ✅ Environment variable management

### 3. **Fly.io**
- ✅ Free tier available
- ✅ Global deployment
- ✅ Auto-scaling
- ⚠️ Requires credit card

### 4. **Render.com**
- ✅ Free tier for web services
- ✅ Auto-deploy from GitHub
- ⚠️ Spins down after 15 minutes of inactivity

### 5. **Glitch.com**
- ✅ Free hosting
- ✅ Online code editor
- ⚠️ Project sleeps after 5 minutes
- ⚠️ Limited resources

## Bot Usage

### Basic Commands

**Direct Message:**
```
Hey @CustomGPT, what is your refund policy?
```

**Slash Command:**
```
/customgpt How do I get started with your product?
```

**Switch Agent:**
```
/customgpt-agent 12345
```

### Advanced Features

**1. Starter Questions**
The bot automatically displays relevant starter questions when:
- A user starts a new conversation
- A user types "help" or "start"
- Configured in the agent settings

**2. Thread Conversations**
The bot maintains context within threads, allowing for follow-up questions.

**3. Rate Limiting**
Default limits:
- 20 requests per user per minute
- 100 requests per channel per hour
- Configurable in `config.py`

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SLACK_BOT_TOKEN` | Bot User OAuth Token | Yes | - |
| `SLACK_SIGNING_SECRET` | For verifying requests | Yes | - |
| `CUSTOMGPT_API_KEY` | Your CustomGPT API key | Yes | - |
| `CUSTOMGPT_PROJECT_ID` | Default agent/project ID | Yes | - |
| `REDIS_URL` | Redis URL for caching | No | - |
| `LOG_LEVEL` | Logging level (INFO, DEBUG) | No | INFO |
| `RATE_LIMIT_PER_USER` | Requests per user per minute | No | 20 |
| `RATE_LIMIT_PER_CHANNEL` | Requests per channel per hour | No | 100 |
| `THREAD_FOLLOW_UP_ENABLED` | Enable thread follow-up responses | No | true |
| `THREAD_FOLLOW_UP_TIMEOUT` | Thread follow-up timeout (seconds) | No | 3600 |
| `THREAD_FOLLOW_UP_MAX_MESSAGES` | Max messages per thread | No | 50 |
| `IGNORE_BOT_MESSAGES` | Ignore messages from bots | No | true |

### Thread Follow-up Feature

The bot can automatically respond to follow-up messages in threads without requiring mentions:

1. **How it works**: When someone mentions the bot in a thread, it "joins" the conversation
2. **Follow-ups**: Users can continue asking questions without @mentioning the bot
3. **Timeout**: Bot stops responding after `THREAD_FOLLOW_UP_TIMEOUT` seconds of inactivity
4. **Message limit**: Bot stops after `THREAD_FOLLOW_UP_MAX_MESSAGES` messages
5. **Bot protection**: Ignores messages from other bots to prevent loops

**Example:**
```
User: @CustomGPT what is the weather?
Bot: The weather is sunny today.
User: What about tomorrow?  (no @mention needed)
Bot: Tomorrow will be cloudy with a chance of rain.
```

### Security Best Practices

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables or secret management
   - Rotate keys regularly

2. **Input Validation**
   - Sanitize all user inputs
   - Implement message length limits
   - Filter potentially harmful content

3. **Rate Limiting**
   - Implement per-user limits
   - Add channel-wide limits
   - Use exponential backoff for repeat offenders

4. **Access Control**
   - Restrict bot to specific channels
   - Implement user allowlists/blocklists
   - Log all interactions for audit

## Extending Functionality

### 1. Add Custom Commands

```python
@app.command("/customgpt-search")
async def handle_search_command(ack, command, client):
    await ack()
    # Implementation
```

### 2. Interactive Components

Add buttons and modals for better UX:

```python
# Add feedback buttons
await client.chat_postMessage(
    channel=channel,
    text=response_text,
    blocks=[
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": response_text}
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "👍"},
                    "action_id": "feedback_positive"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "👎"},
                    "action_id": "feedback_negative"
                }
            ]
        }
    ]
)
```

### 3. Analytics Integration

Track usage patterns:

```python
# Log to analytics service
analytics.track(
    user_id=user_id,
    event="query_submitted",
    properties={
        "agent_id": agent_id,
        "query_length": len(query),
        "channel_type": channel_type
    }
)
```

### 4. Multi-language Support

```python
# Detect user language preference
user_lang = detect_user_language(user_id)

# Query with language parameter
response = await customgpt_client.send_message(
    project_id=agent_id,
    message=query,
    lang=user_lang
)
```

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check bot is in the channel/conversation
   - Verify event subscriptions are enabled
   - Check Request URL is correct

2. **Authentication errors**
   - Verify all tokens are correct
   - Check OAuth scopes
   - Ensure bot is installed to workspace

3. **Rate limiting**
   - Check CustomGPT API limits
   - Verify rate limiter configuration
   - Check Redis connection (if using)

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python bot.py
```

## Support

- CustomGPT Documentation: [customgpt.ai/docs](https://customgpt.ai/docs)
- Slack API Documentation: [api.slack.com](https://api.slack.com)
- Issues: Create an issue in this repository

## License

MIT License - see LICENSE file for details