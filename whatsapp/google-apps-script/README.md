# Google Apps Script WhatsApp Bot for CustomGPT

A lightweight WhatsApp bot implementation using Google Apps Script and Twilio.

## Features

- 🆓 **Free Hosting**: Runs on Google's infrastructure at no cost
- 🔌 **Easy Setup**: No server required, just copy and paste
- 📱 **WhatsApp Integration**: Uses Twilio for reliable messaging
- 🧠 **CustomGPT Powered**: Leverages your agent's knowledge base
- ⚡ **Rate Limiting**: Built-in protection against abuse
- 🌍 **Multi-language**: Support for multiple languages

## Prerequisites

1. **CustomGPT Account**
   - API Key
   - Agent/Project ID

2. **Twilio Account** (Free trial available)
   - Account SID
   - Auth Token
   - WhatsApp Sandbox or approved number

3. **Google Account**
   - Access to Google Apps Script

## Setup Instructions

### Step 1: Create Google Apps Script Project

1. Go to [script.google.com](https://script.google.com)
2. Click "New Project"
3. Name your project (e.g., "CustomGPT WhatsApp Bot")

### Step 2: Copy the Code

1. Delete any existing code in the editor
2. Copy all code from `Code.gs`
3. Paste into the Google Apps Script editor
4. Save the project (Ctrl+S or Cmd+S)

### Step 3: Configure Script Properties

1. In the script editor, click on "Project Settings" (gear icon)
2. Scroll down to "Script Properties"
3. Add the following properties:

| Property | Value | Description |
|----------|-------|-------------|
| CUSTOMGPT_API_KEY | your_api_key | Your CustomGPT API key |
| CUSTOMGPT_PROJECT_ID | your_project_id | Your agent/project ID |
| TWILIO_ACCOUNT_SID | your_account_sid | Twilio Account SID |
| TWILIO_AUTH_TOKEN | your_auth_token | Twilio Auth Token |
| TWILIO_WHATSAPP_NUMBER | whatsapp:+14155238886 | Your Twilio WhatsApp number |
| WEBHOOK_URL | (will be set later) | Your webhook URL |
| ADMIN_NUMBERS | +1234567890,+0987654321 | Admin phone numbers (optional) |

### Step 4: Deploy as Web App

1. Click "Deploy" → "New Deployment"
2. Choose type: "Web app"
3. Configure:
   - Description: "WhatsApp Bot v1"
   - Execute as: "Me"
   - Who has access: "Anyone"
4. Click "Deploy"
5. Copy the Web app URL (this is your webhook URL)
6. Go back to Script Properties and set WEBHOOK_URL to this URL

### Step 5: Configure Twilio

#### For Twilio Sandbox (Testing):

1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to "Messaging" → "Try it out" → "Send a WhatsApp message"
3. Follow instructions to join the sandbox
4. In sandbox settings, set webhook URL to your Google Apps Script URL

#### For Production (Approved Number):

1. Apply for WhatsApp Business API access
2. Once approved, configure webhook URL in your WhatsApp sender settings

### Step 6: Test Your Bot

1. Send "Hi" to your Twilio WhatsApp number
2. You should receive a welcome message
3. Try commands like:
   - `/help` - Show available commands
   - `/examples` - See example questions
   - `/stats` - View usage statistics

## Usage

### Commands

- `/start` - Start a new conversation
- `/help` - Show help message
- `/examples` - Show example questions
- `/stats` - View usage statistics
- `/language [code]` - Change language
- `/clear` - Clear conversation history

### Sending Messages

Just type your question naturally. The bot will:
1. Process your message
2. Query the CustomGPT API
3. Return a response with citations

## Limitations

### Google Apps Script Limits

- **Execution time**: 6 minutes per execution (but webhooks may timeout sooner!)
- **URL Fetch calls**: 20,000/day
- **Cache storage**: 100MB
- **Triggers**: 20 per user

### ⚠️ Important: Timeout Issues

**Google Apps Script may timeout when processing long responses!** This happens because:
1. Twilio expects a quick response (within ~10 seconds)
2. CustomGPT API calls can take 5-10 seconds for complex queries
3. Sending multiple messages (like "Thinking..." + response) increases execution time

**Symptoms of timeout**:
- You only receive "💭 Thinking..." but no actual response
- Multiple webhook executions in logs (Twilio retrying)
- Execution time > 5 seconds in the logs

**Solutions**:
1. **Disable the "Thinking..." message** (already done in latest version)
2. **Keep queries concise** to reduce API response time
3. **Use the Python bot** for production use with long responses
4. **Implement response queuing** (advanced - store response and send later)

### Twilio Limits

- **Sandbox**: Limited to approved test numbers
- **Free trial**: $15 credit (thousands of messages)
- **Rate limits**: Vary by account type

### Workarounds

- Use multiple Google accounts for scaling
- Implement queuing for high volume
- Consider upgrading to production Twilio account

## Troubleshooting

### Bot not responding

1. Check Script Properties are set correctly
2. Verify webhook URL in Twilio matches your deployment
3. Check execution logs in Apps Script editor
4. Ensure rate limits haven't been exceeded

### "Unauthorized" errors

1. Verify CustomGPT API key is correct
2. Check project ID matches your agent
3. Ensure API key has necessary permissions

### Rate limiting issues

1. Adjust RATE_LIMIT_DAILY and RATE_LIMIT_MINUTE in code
2. Clear cache if needed (create a clearCache function)
3. Monitor usage with /stats command

## Advanced Configuration

### Custom Rate Limits

Edit these values in the CONFIG object:
```javascript
RATE_LIMIT_DAILY: 100,  // Messages per day
RATE_LIMIT_MINUTE: 5,   // Messages per minute
```

### Adding Admin Commands

Add admin phone numbers to ADMIN_NUMBERS property, then add commands:
```javascript
case '/admin':
  if (isAdmin(phoneNumber)) {
    // Admin functionality
  }
  break;
```

### Logging and Monitoring

View logs:
1. In Apps Script editor, click "Execution log"
2. Or go to "Executions" in left sidebar

## Security Considerations

1. **Keep credentials secure**: Never share Script Properties
2. **Use environment-specific projects**: Separate dev/prod
3. **Monitor usage**: Check logs regularly
4. **Implement allowlists**: Restrict access if needed

## Cost Optimization

1. **Google Apps Script**: Always free
2. **Twilio**: 
   - Start with free trial
   - WhatsApp messages: ~$0.005 each
   - Consider monthly plans for volume
3. **CustomGPT**: Based on your plan limits

## Support

- **CustomGPT Issues**: Check API documentation
- **Twilio Issues**: Twilio support or community
- **Apps Script Issues**: Google Workspace support

## Next Steps

1. **Enhance functionality**: Add media support, voice messages
2. **Implement analytics**: Track usage patterns
3. **Add persistence**: Use Google Sheets for data storage
4. **Create admin panel**: Web interface for management