# Google Apps Script Implementation for CustomGPT Slack Bot

This is a free, serverless implementation of the CustomGPT Slack Bot using Google Apps Script.

## Features

- ✅ **Free Hosting** - No credit card required
- ✅ **Auto-scaling** - Google handles the infrastructure
- ✅ **Built-in Security** - SSL/HTTPS by default
- ✅ **Easy Deployment** - Web-based IDE
- ✅ **Multi-Agent Support** - Switch between different CustomGPT agents
- ✅ **Rate Limiting** - Per-user and per-channel limits
- ✅ **Thread Support** - Maintains conversation context in threads with automatic follow-ups
- ✅ **Slash Commands** - `/customgpt`, `/customgpt-agent`, `/customgpt-help`
- ⚠️ **Limitations** - 6-minute execution time, 20MB response limit

## Setup Instructions

### 1. Create Google Apps Script Project

1. Go to [script.google.com](https://script.google.com)
2. Click "New Project"
3. Name your project (e.g., "CustomGPT Slack Bot")

### 2. Add the Code

1. Delete the default code in `Code.gs`
2. Copy the entire contents of `Code.gs` from this folder
3. Paste it into the script editor
4. Save the project (Ctrl+S or Cmd+S)

### 3. Set Script Properties

1. In the script editor, go to Project Settings (gear icon)
2. Scroll down to "Script Properties"
3. Add the following properties:
   - `SLACK_BOT_TOKEN` - Your Slack bot token (xoxb-...)
   - `SLACK_SIGNING_SECRET` - Your Slack signing secret
   - `CUSTOMGPT_API_KEY` - Your CustomGPT API key
   - `CUSTOMGPT_PROJECT_ID` - Your default CustomGPT project/agent ID
   
   Optional properties for thread follow-up feature:
   - `THREAD_FOLLOW_UP_ENABLED` - Enable thread follow-ups (default: true)
   - `THREAD_FOLLOW_UP_TIMEOUT` - Timeout in seconds (default: 3600)
   - `THREAD_FOLLOW_UP_MAX_MESSAGES` - Max messages per thread (default: 50)
   - `IGNORE_BOT_MESSAGES` - Ignore bot messages (default: true)

### 4. Deploy as Web App

1. Click "Deploy" > "New Deployment"
2. Click the gear icon > "Web app"
3. Configure:
   - Description: "Slack Bot v1"
   - Execute as: "Me"
   - Who has access: "Anyone"
4. Click "Deploy"
5. Copy the Web App URL (you'll need this for Slack)

### 5. Configure Slack App

1. Go to your Slack app settings at [api.slack.com/apps](https://api.slack.com/apps)
2. Go to "Event Subscriptions"
3. Enable Events
4. Set Request URL to your Google Apps Script Web App URL
5. Add Bot Events:
   - `app_mention`
   - `message.im`
   - `message.channels` (required for thread follow-ups)
6. Save changes

### 6. Configure Slash Commands (Optional)

For each slash command:
1. Go to "Slash Commands" in Slack app settings
2. Create New Command
3. Set Request URL to your Google Apps Script Web App URL
4. Configure these commands:
   - `/customgpt` - Command for asking questions
   - `/customgpt-agent` - Switch between different CustomGPT agents
   - `/customgpt-help` - Show help information

## Limitations

### Google Apps Script Limitations

1. **Execution Time**: Maximum 6 minutes per execution
2. **Response Size**: Maximum 20MB response
3. **Quota Limits**: 
   - URL Fetch: 20,000 calls/day
   - Cache: 100MB
4. **No WebSocket Support**: Can't use Socket Mode

### Workarounds

1. **Rate Limiting**: Uses built-in cache service (limited to 100MB)
2. **Conversation State**: Stored in cache with 6-hour expiry
3. **Thread Tracking**: Thread participation stored in cache with configurable timeout
4. **No Persistent Storage**: Agent switching lasts for 24 hours in cache
5. **Synchronous Only**: No true async support
6. **Citations Disabled**: Source links disabled to avoid broken references

## Customization

### Modify Rate Limits

Edit these values in the CONFIG object:
```javascript
RATE_LIMIT_PER_USER: 20, // per minute
RATE_LIMIT_PER_CHANNEL: 100, // per hour
```

### Change Default Messages

Modify the `showStarterQuestions()` function to customize starter questions.

### Enable/Disable Citations

To enable citations (if CustomGPT provides valid URLs):
```javascript
SHOW_CITATIONS: true  // Currently false to avoid broken links
```

### Configure Thread Follow-ups

Adjust thread follow-up behavior in Script Properties:
- `THREAD_FOLLOW_UP_ENABLED` - Set to 'false' to disable
- `THREAD_FOLLOW_UP_TIMEOUT` - Seconds before bot stops responding (default: 3600)
- `THREAD_FOLLOW_UP_MAX_MESSAGES` - Max messages per thread (default: 50)

### Add Custom Features

You can extend the script with additional features:
- Custom logging to Google Sheets
- Integration with other Google services
- Webhook notifications

## Troubleshooting

### Bot Not Responding

1. Check the Execution Log in Apps Script editor
2. Verify all Script Properties are set correctly
3. Ensure Slack Event Subscriptions URL is verified
4. Check quotas haven't been exceeded
5. Make sure bot is added to the channel/workspace

### Common Issues

1. **"operation_timeout" error**: This is normal for slash commands - the bot will still respond
2. **Duplicate messages**: Fixed in current version with proper deduplication
3. **Help messages showing repeatedly**: Fixed with improved bot message detection
4. **Broken source links**: Citations are disabled by default to avoid this

### Rate Limiting Issues

- Cache might be full (100MB limit)
- Consider implementing time-based cleanup
- Rate limits reset after 1 minute (user) and 1 hour (channel)

### Performance Issues

- Reduce the number of API calls
- Implement more aggressive caching
- Consider moving to a dedicated hosting solution

## Migration Path

When you outgrow Google Apps Script, you can easily migrate to:
1. **Railway/Render**: Use the Python implementation
2. **AWS Lambda**: Serverless with better limits
3. **VPS**: Full control with the Docker implementation

## Security Notes

- Never expose Script Properties in logs
- Use Slack signature verification
- Implement input validation
- Regular security reviews

## Usage

### Basic Commands

- **Direct Message**: Just type your question in a DM with the bot
- **Mention in Channel**: `@CustomGPT your question here`
- **Slash Command**: `/customgpt your question here`

### Thread Follow-ups

Once the bot responds to your mention in a thread, you can continue the conversation without mentioning it again:

```
User: @CustomGPT what is the weather?
Bot: The weather is sunny today.
User: What about tomorrow?  (no @mention needed)
Bot: Tomorrow will be cloudy with a chance of rain.
```

The bot will continue responding in the thread until:
- The timeout expires (default: 1 hour)
- The message limit is reached (default: 50 messages)
- You start a new thread

### Agent Management

Switch between different CustomGPT agents:
```
/customgpt-agent 12345  # Switch to agent with ID 12345
/customgpt-agent        # Show current agent ID
```

### Getting Help

```
/customgpt-help         # Show available commands
```
Or just mention the bot without any text to see starter questions.

## Support

For issues specific to Google Apps Script implementation:
1. Check the Execution transcript
2. Review quota usage in Google Cloud Console
3. Ensure all permissions are granted
4. Check logs in Apps Script editor (View → Logs)