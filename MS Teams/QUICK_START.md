# Quick Start Guide - CustomGPT Teams Bot

> ⚠️ **Note**: This Teams bot is currently a Work in Progress (WIP)

## 5-Minute Setup

### Prerequisites
- Microsoft Teams admin access
- Azure account (free tier OK)
- CustomGPT API credentials
- Python 3.9+ or Docker

### Fastest Deployment Path

#### Option 1: Local Testing with Ngrok (5 minutes)

1. **Clone and setup**:
```bash
git clone <repo>
cd customgpt-integrations/MS Teams
python setup.py  # Interactive setup
```

2. **Run with Docker + Ngrok**:
```bash
# Add your NGROK_AUTHTOKEN to .env
docker-compose --profile dev up
```

3. **Register bot** (while running):
- Go to [Azure Portal](https://portal.azure.com)
- Create "Bot Channels Registration"
- Use ngrok URL for messaging endpoint
- Note App ID and Password

4. **Update .env** and restart

5. **Install in Teams**:
- Update manifest.json with your App ID
- Zip manifest.json + icons
- Upload to Teams

#### Option 2: Free Cloud Deployment (15 minutes)

**Railway.app** (Recommended for beginners):
1. Fork this repo
2. Connect to Railway
3. Add environment variables
4. Deploy automatically
5. Use Railway URL in Azure bot

**Render.com**:
1. Create Web Service
2. Connect GitHub repo
3. Set environment variables
4. Deploy (builds automatically)

## Key Implementation Details

### What Makes This Different from Slack Bot

| Feature | Slack Bot | Teams Bot |
|---------|-----------|-----------|
| Authentication | OAuth + Signing Secret | Azure AD + Bot Framework |
| UI Elements | Blocks/Modals | Adaptive Cards |
| Message Format | Slack Markdown | Teams Markdown + Cards |
| Threading | Thread TS | Conversation References |
| Rate Limiting | Per workspace | Per user/channel/tenant |
| Deployment | Any HTTP server | Needs Bot Framework |
| Mentions | <@USERID> | <at>username</at> |
| Files | Direct URLs | Authenticated downloads |

### Core Components Explained

1. **app.py**: Flask server handling Teams webhooks
2. **bot.py**: Main bot logic with Teams-specific handlers
3. **adaptive_cards.py**: Rich UI components for Teams
4. **auth_handler.py**: Azure AD authentication
5. **customgpt_client.py**: Your CustomGPT API integration
6. **rate_limiter.py**: Multi-level rate limiting
7. **conversation_manager.py**: Context management

### Security Features

- **Multi-tenant support**: Works across organizations
- **Channel/User restrictions**: Via environment variables
- **Rate limiting**: Prevents abuse
- **Audit logging**: Track all interactions
- **Azure AD**: Enterprise authentication

### Quick Troubleshooting

**Bot not responding?**
- Check Azure bot messaging endpoint
- Verify ngrok is running (local dev)
- Check logs: `docker logs customgpt-teams-bot`

**Authentication errors?**
- Verify TEAMS_APP_ID and TEAMS_APP_PASSWORD
- Ensure bot is registered correctly in Azure

**Rate limit issues?**
- Adjust limits in .env
- Consider Redis for distributed limiting

### Essential Commands

```bash
# Development
python setup.py              # Interactive setup
python app.py               # Run locally
pytest                      # Run tests

# Docker
docker-compose up           # Run with Docker
docker-compose down         # Stop containers
docker logs -f customgpt-teams-bot  # View logs

# Deployment
docker build -t teams-bot . # Build image
az webapp up               # Deploy to Azure
```

### Environment Variables Reference

```env
# Required
TEAMS_APP_ID=               # From Azure bot registration
TEAMS_APP_PASSWORD=         # From Azure bot registration  
CUSTOMGPT_API_KEY=          # Your CustomGPT API key
CUSTOMGPT_PROJECT_ID=       # Your CustomGPT project ID

# Important Options
RATE_LIMIT_PER_USER=20      # Messages per minute
REQUIRE_MENTION_IN_CHANNELS=true  # Require @mention in channels
ENABLE_ADAPTIVE_CARDS=true  # Rich UI cards

# Optional
ALLOWED_TENANTS=            # Comma-separated tenant IDs
REDIS_URL=                  # For distributed rate limiting
```

### Next Steps

1. **Test locally** with ngrok first
2. **Deploy to cloud** when ready
3. **Monitor usage** via Application Insights
4. **Customize** Adaptive Cards for your use case
5. **Scale** with Redis when needed

For detailed instructions, see the full [README.md](README.md)

## Need Help?

- Check [deployment guides](deployment/)
- Review [test examples](tests/)
- See [Azure deployment guide](deployment/azure-deploy.md)
- Read about [why not Google Apps Script](deployment/google-apps-script-guide.md)