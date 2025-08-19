# CustomGPT Google Apps Script Integration

A comprehensive Google Apps Script solution that integrates CustomGPT with Google Workspace, providing:
- 🤖 **Google Chat Bot** - Interactive chatbot for Google Chat
- 🌐 **Web App** - Standalone chat interface with Material Design
- 📊 **Google Sheets Integration** - Use CustomGPT from spreadsheets
- 📧 **Gmail Add-on** - AI responses in Gmail

## Features

### Google Chat Bot
- Slash commands (`/help`, `/info`, `/starters`, `/reset`)
- Interactive card responses with buttons
- Conversation context within spaces
- Rate limiting per user
- Welcome messages and onboarding

### Web App Interface
- Material Design UI with light/dark themes
- Real-time chat interface
- Starter questions
- Citation support
- Export chat history
- Mobile responsive

### Security & Performance
- API key security with Script Properties
- Rate limiting (10/min per user, 100/hour)
- Response caching (5 minutes)
- Domain-based access control
- Error handling and recovery

## Setup Instructions

### 1. Create Google Apps Script Project

1. Go to [script.google.com](https://script.google.com)
2. Click **New Project**
3. Name your project (e.g., "CustomGPT Integration")

### 2. Add Project Files

Copy these files to your project:
- `Code.gs` - Main server-side code
- `index.html` - Web app interface
- `styles.html` - CSS styles
- `javascript.html` - Client-side JavaScript
- `appsscript.json` - Project manifest

### 3. Configure Script Properties

1. In Apps Script editor, go to **Project Settings** (gear icon)
2. Scroll to **Script Properties**
3. Add these properties:
   - `CUSTOMGPT_API_KEY` - Your CustomGPT API key
   - `CUSTOMGPT_AGENT_ID` - Your agent/project ID
   - `ALLOWED_DOMAINS` - (Optional) Comma-separated list of allowed domains

### 4. Deploy as Web App

1. Click **Deploy** > **New Deployment**
2. Choose type: **Web app**
3. Settings:
   - Description: "CustomGPT Chat Interface"
   - Execute as: **User accessing the web app**
   - Who has access: Choose based on your needs:
     - **Anyone** - Public access
     - **Anyone with Google account** - Requires login
     - **Only myself** - Private use
     - **Anyone within [your domain]** - Organization only
4. Click **Deploy**
5. Copy the Web App URL

### 5. Set Up Google Chat Bot

1. Enable Google Chat API:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create or select a project
   - Enable "Google Chat API"

2. Configure Chat Bot:
   - In Cloud Console, go to **APIs & Services** > **Credentials**
   - Create credentials > **Service Account**
   - Download JSON key file

3. Configure Bot in Google Chat:
   - Go to Google Chat API configuration
   - Set bot name, avatar, description
   - Add the Apps Script Web App URL as the bot endpoint
   - Configure slash commands

4. Deploy Chat Bot:
   - In Apps Script, click **Deploy** > **New Deployment**
   - Add type: **API Executable**
   - Deploy and copy the deployment ID

## Usage Guide

### Google Chat Bot Commands

- **Direct Message**: Just type your question
- **`/help`** - Show available commands
- **`/info`** - Display agent information
- **`/starters`** - Show starter questions
- **`/reset`** - Reset conversation context

### Web App Features

1. **Chat Interface**:
   - Type questions in the input field
   - Press Enter to send (Shift+Enter for new line)
   - View responses with citations

2. **UI Controls**:
   - 🌓 Theme toggle (light/dark)
   - ℹ️ Agent information
   - 🔄 Reset conversation
   - 📥 Export chat history

3. **Starter Questions**:
   - Click any suggested question to ask it
   - Customize in agent settings

### Google Sheets Integration

Add this custom function to use in sheets:

```javascript
/**
 * Query CustomGPT from Google Sheets
 * @param {string} question The question to ask
 * @return {string} The response from CustomGPT
 * @customfunction
 */
function CUSTOMGPT(question) {
  if (!question) return "Please provide a question";
  
  try {
    const response = sendToCustomGPT(question, "sheets");
    return response.content;
  } catch (error) {
    return "Error: " + error.message;
  }
}
```

Usage in Sheets:
```
=CUSTOMGPT("What is the weather forecast?")
=CUSTOMGPT(A1)  // Reference a cell
```

### Gmail Add-on

To create a Gmail add-on:

1. Add to `appsscript.json`:
```json
{
  "gmail": {
    "name": "CustomGPT Assistant",
    "logoUrl": "https://www.customgpt.ai/logo.png",
    "contextualTriggers": [{
      "unconditional": {},
      "onTriggerFunction": "onGmailMessage"
    }]
  }
}
```

2. Add handler function:
```javascript
function onGmailMessage(e) {
  // Create card with CustomGPT integration
  return buildGmailCard(e);
}
```

## Advanced Configuration

### Rate Limiting

Adjust in `CONFIG` object:
```javascript
RATE_LIMIT_PER_USER: 10,     // Per minute
RATE_LIMIT_PER_HOUR: 100,    // Per hour
CACHE_DURATION: 300,         // 5 minutes
```

### Domain Restrictions

Set `ALLOWED_DOMAINS` in Script Properties:
```
example.com,anotherdomain.com
```

Enable checking:
```javascript
REQUIRE_DOMAIN_CHECK: true
```

### Custom Styling

Modify `styles.html` to customize:
- Colors and themes
- Fonts and sizes
- Layout and spacing
- Animations

### API Response Handling

Customize response processing:
```javascript
// Add to sendToCustomGPT function
if (response.someField) {
  // Custom logic
}
```

## Deployment Options

### 1. Personal Use
- Deploy as "Only myself"
- No authentication needed
- Full access to your data

### 2. Team/Organization
- Deploy to your Google Workspace
- Set domain restrictions
- Manage permissions via Google Groups

### 3. Public Service
- Deploy as "Anyone"
- Implement additional security
- Monitor usage and costs

## Monitoring & Logs

### View Logs
1. In Apps Script editor, click **Executions** (📊)
2. Filter by function or status
3. Click any execution for details

### Stackdriver Logging
Logs are automatically sent to Google Cloud Logging:
- View in Cloud Console
- Set up alerts
- Export to BigQuery

### Usage Tracking
Add custom tracking:
```javascript
function trackUsage(action, user) {
  console.log(`Usage: ${action} by ${user}`);
  // Send to analytics service
}
```

## Troubleshooting

### Bot Not Responding
- Check API key and agent ID in Script Properties
- Verify Chat API is enabled
- Check execution logs for errors

### Rate Limit Errors
- Increase limits in CONFIG
- Implement user notifications
- Consider caching strategies

### Authentication Issues
- Check OAuth scopes in manifest
- Verify deployment settings
- Test with different access levels

### Performance Issues
- Enable caching
- Optimize API calls
- Use batch operations

## Best Practices

1. **Security**:
   - Never hardcode API keys
   - Use Script Properties
   - Implement domain checks
   - Monitor access logs

2. **Performance**:
   - Cache frequent responses
   - Batch API calls
   - Minimize external requests
   - Use async operations

3. **User Experience**:
   - Provide clear error messages
   - Show loading states
   - Offer helpful suggestions
   - Maintain conversation context

4. **Maintenance**:
   - Regular testing
   - Monitor quotas
   - Update documentation
   - Version control

## API Reference

### Core Functions

```javascript
// Send message to CustomGPT
sendToCustomGPT(message, conversationId)

// Check rate limits
checkRateLimit(userEmail)

// Get agent information
getAgentInfo()

// Get starter questions  
getStarterQuestions()
```

### Web App Functions

```javascript
// Send message from web UI
sendWebMessage(message)

// Get configuration
getWebConfig()

// Export functions
exportChat()
```

### Chat Bot Handlers

```javascript
// Main webhook handler
doPost(e)

// Message handler
handleChatMessage(message)

// Command handler
handleCommand(command, message)
```

## Extending the Integration

### Add Custom Commands

```javascript
case '/custom':
  return handleCustomCommand(parts, message);
```

### Integrate with Other Services

```javascript
function integrateWithService(data) {
  const serviceUrl = 'https://api.example.com';
  return UrlFetchApp.fetch(serviceUrl, {
    method: 'post',
    payload: JSON.stringify(data)
  });
}
```

### Create Scheduled Tasks

```javascript
function scheduledTask() {
  // Run daily summaries, reports, etc.
}
```

Set up time-based trigger in Apps Script.

## Support & Resources

- [CustomGPT API Docs](https://docs.customgpt.ai)
- [Google Apps Script Docs](https://developers.google.com/apps-script)
- [Google Chat Bot Guide](https://developers.google.com/chat/how-tos/bots-develop)
- [Material Design Guidelines](https://material.io/design)

## License

MIT License - Feel free to modify and distribute.