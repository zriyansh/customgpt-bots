# Google Apps Script Setup for Facebook Messenger Bot

Free, serverless Facebook Messenger bot using Google Apps Script.

## Prerequisites
1. Google Account
2. Facebook Page and App
3. CustomGPT API credentials

## Setup Steps

### 1. Create Google Apps Script Project
1. Go to [script.google.com](https://script.google.com)
2. Click "New project"
3. Copy all code from `Code.gs` into the editor
4. Save the project with name "CustomGPT FB Bot"

### 2. Configure Script Properties
1. Click "Project Settings" (gear icon)
2. Scroll to "Script Properties"
3. Add these properties:
   - `FB_VERIFY_TOKEN`: Your custom verification token
   - `FB_PAGE_ACCESS_TOKEN`: From Facebook App Dashboard
   - `FB_APP_SECRET`: From Facebook App Settings
   - `CUSTOMGPT_API_KEY`: Your CustomGPT API key
   - `CUSTOMGPT_PROJECT_ID`: Your agent ID

### 3. Deploy as Web App
1. Click "Deploy" > "New deployment"
2. Settings:
   - Type: Web app
   - Execute as: Me
   - Who has access: Anyone
3. Click "Deploy"
4. Copy the Web app URL

### 4. Facebook App Configuration
1. Go to [Facebook Developers](https://developers.facebook.com)
2. Select your app
3. Go to Messenger > Settings
4. In Webhooks section:
   - Callback URL: Your Google Apps Script URL
   - Verify Token: Your `FB_VERIFY_TOKEN`
   - Subscribe to: `messages`, `messaging_postbacks`

### 5. Generate Page Access Token
1. In Messenger Settings
2. Add your Facebook Page
3. Generate token
4. Copy and add to Script Properties

### 6. Test Your Bot
1. Message your Facebook Page
2. Check Google Apps Script logs for debugging

## Features
- ✅ Free hosting
- ✅ No server management
- ✅ Built-in HTTPS
- ✅ Auto-scaling
- ✅ Easy updates

## Limitations
- 6 minute execution time limit
- 20MB response size limit
- Limited concurrent executions
- No websockets

## Troubleshooting

### Bot not responding
1. Check webhook subscription
2. Verify all Script Properties are set
3. Check execution logs in Apps Script

### Rate limit errors
1. Adjust limits in code
2. Clear cache if needed

### API errors
1. Verify API credentials
2. Check CustomGPT dashboard for usage

## Advanced Configuration

### Custom Commands
Edit the `handleMessage()` function to add new commands.

### Starter Questions
Modify the `sendExampleQuestions()` function.

### Rate Limits
Adjust `RATE_LIMIT_MINUTE` and `RATE_LIMIT_DAILY` in CONFIG.

## Security Notes
- Script Properties are secure and not exposed
- Webhook signature verification implemented
- Rate limiting per user
- No sensitive data in logs