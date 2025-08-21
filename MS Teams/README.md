# CustomGPT Microsoft Teams Bot

> ⚠️ **WORK IN PROGRESS**: This Microsoft Teams integration is currently under development. Some features may not be fully implemented or tested. Please check back for updates or contribute to the development.

A production-ready Microsoft Teams bot that integrates with CustomGPT API to bring your knowledge base directly into Teams conversations.

## Features

### Core Functionality
- 🤖 **Intelligent Q&A**: Access your CustomGPT knowledge base directly in Teams
- 💬 **Natural Conversations**: Maintains context across messages
- 🧵 **Threading Support**: Continues conversations in threads
- 📎 **File Attachments**: Process documents and images
- 🌐 **Multi-language Support**: Responds in user's preferred language

### Teams-Specific Features
- 🎯 **@Mentions**: Responds to mentions in channels
- 💼 **Meeting Integration**: Works in Teams meetings
- 🃏 **Adaptive Cards**: Rich, interactive UI elements
- 👥 **Multi-scope**: Works in personal chats, group chats, and channels
- ⚡ **Slash Commands**: Quick actions like `/help`, `/reset`, `/status`

### Security & Compliance
- 🔐 **Azure AD Authentication**: Secure bot authentication
- 🚦 **Rate Limiting**: Per-user, per-channel, and per-tenant limits
- 📋 **Audit Logging**: Track all interactions
- 🛡️ **Access Control**: Tenant, channel, and user allowlists/blocklists
- 🔒 **Data Privacy**: No message storage, conversation timeout

### Enterprise Features
- 📊 **Analytics Integration**: Application Insights support
- 🌍 **Multi-tenant Support**: Works across organizations
- 🔄 **Distributed Rate Limiting**: Redis support for scale
- 📈 **Performance Monitoring**: Built-in health checks
- 🚀 **Auto-scaling Ready**: Containerized deployment

## Prerequisites

1. **Microsoft Teams Admin Access**: To install and manage the bot
2. **Azure Account**: For bot registration (free tier available)
3. **CustomGPT Account**: API key and Project ID
4. **Python 3.9+**: For running the bot
5. **Optional**: Redis for distributed deployments

## Quick Start

### 1. Bot Registration in Azure

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new "Bot Channels Registration" resource
3. Configure the bot:
   - **Name**: Your bot name
   - **Subscription**: Your Azure subscription
   - **Resource group**: Create new or use existing
   - **Pricing tier**: F0 (free) for testing
   - **Messaging endpoint**: `https://your-domain.com/api/messages`
   - **App type**: Multi Tenant (recommended)

4. After creation, go to "Configuration" and note:
   - **Microsoft App ID** (TEAMS_APP_ID)
   - Click "Manage" next to App ID
   - Create new client secret and note it (TEAMS_APP_PASSWORD)

### 2. Configure the Bot

1. Clone the repository:
```bash
git clone <your-repo>
cd customgpt-integrations/MS Teams
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Edit `.env` with your values:
```env
TEAMS_APP_ID=your-app-id
TEAMS_APP_PASSWORD=your-app-password
CUSTOMGPT_API_KEY=your-customgpt-api-key
CUSTOMGPT_PROJECT_ID=your-customgpt-project-id
```

### 3. Local Development

#### Option A: Python Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python app.py
```

#### Option B: Docker
```bash
# Build and run with Docker Compose
docker-compose up

# Or with Redis for distributed rate limiting
docker-compose --profile with-redis up
```

#### Option C: Development with Ngrok
```bash
# Install ngrok
# Then run:
docker-compose --profile dev up

# Your public URL will be shown in ngrok output
# Update Azure bot messaging endpoint with the ngrok URL
```

### 4. Create Teams App Package

1. Update `deployment/manifest.json`:
   - Replace `YOUR-APP-ID-HERE` with your bot's App ID
   - Replace `YOUR-BOT-ID-HERE` with the same App ID
   - Update other placeholders as needed

2. Create app icons:
   - `color.png`: 192x192px color icon
   - `outline.png`: 32x32px outline icon

3. Create the package:
```bash
cd deployment
zip -r customgpt-bot.zip manifest.json color.png outline.png
```

### 5. Install in Teams

1. Open Microsoft Teams
2. Go to Apps → Manage your apps → Upload an app
3. Upload `customgpt-bot.zip`
4. Add the bot to teams and channels as needed

## Deployment Options

### 1. Azure Bot Service (Recommended)

**Pros**: Native Teams integration, built-in scaling, monitoring
**Best for**: Production deployments

1. Create Azure Web App
2. Configure deployment from GitHub/Azure DevOps
3. Set environment variables in App Settings
4. Enable Application Insights for monitoring

See [deployment/azure-deploy.md](deployment/azure-deploy.md) for detailed instructions.

### 2. Docker Container

**Pros**: Portable, consistent environments
**Best for**: Self-hosted deployments

```bash
# Build image
docker build -f deployment/docker/Dockerfile -t customgpt-teams-bot .

# Run container
docker run -p 3978:3978 --env-file .env customgpt-teams-bot
```

### 3. Kubernetes

**Pros**: Scalable, resilient
**Best for**: Enterprise deployments

```yaml
# See deployment/k8s/deployment.yaml for full example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: customgpt-teams-bot
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: bot
        image: customgpt-teams-bot:latest
        ports:
        - containerPort: 3978
```

### 4. Free Hosting Options

#### Railway.app
1. Connect GitHub repo
2. Add environment variables
3. Deploy with one click
4. Free tier: 500 hours/month

#### Render.com
1. Create new Web Service
2. Connect GitHub repo
3. Set environment variables
4. Free tier: 750 hours/month

#### Google Cloud Run
1. Build container image
2. Push to Container Registry
3. Deploy to Cloud Run
4. Free tier: 2 million requests/month

## Configuration Guide

### Rate Limiting

Configure limits in `.env`:
```env
RATE_LIMIT_PER_USER=20      # Messages per minute per user
RATE_LIMIT_PER_CHANNEL=100  # Messages per hour per channel
RATE_LIMIT_PER_TENANT=500   # Messages per hour per organization
```

### Security

Restrict access by tenant, channel, or user:
```env
ALLOWED_TENANTS=tenant-id-1,tenant-id-2
ALLOWED_CHANNELS=channel-id-1,channel-id-2
BLOCKED_USERS=user-id-1,user-id-2
```

### Conversation Management

Control conversation behavior:
```env
CONVERSATION_TIMEOUT=86400  # 24 hours
MAX_CONTEXT_MESSAGES=10     # Context window
ENABLE_THREADING=true       # Thread support
```

### Advanced Features

Enable additional capabilities:
```env
ENABLE_ADAPTIVE_CARDS=true
ENABLE_FILE_ATTACHMENTS=true
ENABLE_MEETING_SUPPORT=true
ENABLE_ANALYTICS=true
APPLICATION_INSIGHTS_KEY=your-key
```

## Usage

### Basic Commands

- `/help` - Show available commands and usage
- `/start` - Start a new conversation
- `/reset` - Clear conversation context
- `/status` - Check rate limits and bot status
- `/feedback` - Provide feedback

### Interacting with the Bot

#### Personal Chat
Simply type your question directly.

#### Channels
Mention the bot: `@CustomGPT Bot what is our refund policy?`

#### Threads
Reply to a bot message to continue the conversation.

### Adaptive Cards

The bot uses rich Adaptive Cards for:
- Welcome messages with starter questions
- Responses with citations
- Feedback collection
- Error messages

## Monitoring & Troubleshooting

### Health Check
```bash
curl http://localhost:3978/health
```

### Logs
```bash
# Docker logs
docker logs customgpt-teams-bot

# Application logs
tail -f logs/bot.log
```

### Common Issues

#### Bot not responding
1. Check Azure bot configuration
2. Verify messaging endpoint is correct
3. Check application logs for errors
4. Ensure bot is added to team/channel

#### Rate limit errors
1. Check current limits: `/status`
2. Adjust limits in configuration
3. Consider Redis for distributed limiting

#### Authentication errors
1. Verify App ID and Password
2. Check tenant configuration
3. Ensure bot has proper permissions

## Development

### Project Structure
```
MS Teams/
├── app.py                  # Flask application entry point
├── bot.py                  # Main bot logic
├── config.py              # Configuration management
├── customgpt_client.py    # CustomGPT API client
├── rate_limiter.py        # Rate limiting implementation
├── conversation_manager.py # Conversation state management
├── adaptive_cards.py      # Teams UI components
├── auth_handler.py        # Authentication handling
├── requirements.txt       # Python dependencies
├── deployment/           # Deployment configurations
│   ├── manifest.json     # Teams app manifest
│   └── docker/          # Docker configurations
└── tests/               # Unit and integration tests
```

### Testing

Run tests:
```bash
# All tests
pytest

# With coverage
pytest --cov=.

# Specific test
pytest tests/test_bot.py -v
```

### Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## Security Considerations

1. **API Keys**: Never commit API keys. Use environment variables.
2. **Rate Limiting**: Always enable to prevent abuse.
3. **Access Control**: Use allowlists in production.
4. **Audit Logging**: Enable for compliance.
5. **Data Privacy**: Bot doesn't store messages by default.
6. **Network Security**: Use HTTPS, configure firewalls.

## Support

- **Documentation**: See `/docs` folder
- **Issues**: GitHub Issues
- **CustomGPT Support**: support@customgpt.ai

## License

[Your License]

## Development Status

### Completed ✅
- Core bot architecture
- CustomGPT API integration
- Rate limiting system
- Adaptive Cards UI
- Authentication handling
- Conversation management
- Deployment configurations
- Documentation

### In Progress 🚧
- End-to-end testing
- Production deployment validation
- Performance optimization
- Advanced Teams features integration

### Planned 📋
- Voice message support
- Advanced analytics dashboard
- Multi-language UI
- Custom AI model selection
- Webhook notifications

## Contributing

This integration is currently in development. Contributions are welcome! Please:

1. Check existing issues and PRs
2. Test thoroughly before submitting
3. Follow the existing code style
4. Add tests for new features
5. Update documentation

## Acknowledgments

- Microsoft Bot Framework team
- CustomGPT team
- Contributors and testers