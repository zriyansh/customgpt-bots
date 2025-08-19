# CustomGPT Google Apps Script - Quick Start Guide

Get up and running with CustomGPT in Google Workspace in 5 minutes!

## 🚀 Quick Setup (Web App Only)

### 1. Create New Project
1. Go to [script.google.com](https://script.google.com)
2. Click **New Project**
3. Name it "CustomGPT Integration"

### 2. Copy Files
Copy these files into your project:
- `Code.gs` (main code)
- `index.html` (web interface)
- `styles.html` (styling)
- `javascript.html` (client code)

### 3. Set API Credentials
1. Click **Project Settings** ⚙️
2. Scroll to **Script Properties**
3. Add properties:
   - Key: `CUSTOMGPT_API_KEY` → Value: Your API key
   - Key: `CUSTOMGPT_AGENT_ID` → Value: Your agent ID

### 4. Deploy Web App
1. Click **Deploy** → **New Deployment**
2. Type: **Web app**
3. Execute as: **Me**
4. Access: **Anyone** (or your preference)
5. Click **Deploy**
6. Copy the URL - that's your chat interface!

## 🤖 Google Chat Bot Setup

### Prerequisites
- Google Workspace account
- Admin access (for public bots)

### Steps
1. **Enable Chat API**:
   ```
   Google Cloud Console → APIs → Enable "Google Chat API"
   ```

2. **Configure Bot**:
   - Go to Google Chat API configuration
   - Set name, avatar, description
   - Bot URL: Your Apps Script Web App URL
   - HTTP endpoint

3. **Add to Space**:
   - In Google Chat, click + → "Find apps"
   - Search for your bot name
   - Add to space

## 📊 Google Sheets Functions

### Add Custom Functions
1. Copy `sheets-addon.gs` to your Sheets project
2. Use in any cell:
   ```
   =CUSTOMGPT("What is the weather?")
   =CUSTOMGPT(A1)  // Reference a cell
   ```

### Add Menu
The Sheets add-on creates a CustomGPT menu with:
- Interactive sidebar
- Bulk processing
- Settings

## ⚡ Common Use Cases

### 1. Customer Support Bot
```javascript
// In Google Chat
@YourBot What's the return policy?
@YourBot How do I track my order?
```

### 2. Data Analysis in Sheets
```
=CUSTOMGPT("Analyze this data: " & A1:A10)
=CUSTOMGPT("Summarize the trends in column B")
```

### 3. Email Assistant
```javascript
// Gmail add-on
"Generate a professional response to this email"
"Summarize this email thread"
```

### 4. Documentation Helper
```javascript
// Web app
"Explain how to use feature X"
"What are the best practices for Y?"
```

## 🛠️ Troubleshooting

### "Script function not found"
- Make sure you copied `Code.gs` correctly
- Check function names match

### "Unauthorized" error
- Verify API key in Script Properties
- Check agent ID is correct

### Bot not responding
- Check Chat API is enabled
- Verify webhook URL
- Look at Execution logs

### Rate limit errors
- Default: 10 requests/minute
- Increase in CONFIG object
- Add caching for common queries

## 🎯 Pro Tips

### 1. Caching Responses
```javascript
// Responses are cached for 5 minutes by default
CONFIG.CACHE_DURATION = 600; // 10 minutes
```

### 2. Custom Commands
```javascript
// Add to handleCommand function
case '/summary':
  return createSummaryCard();
```

### 3. Scheduled Reports
```javascript
function dailyReport() {
  const summary = sendToCustomGPT("Daily summary", "scheduled");
  // Send via email or post to Chat
}
// Set up time trigger in Apps Script
```

### 4. Team Permissions
- Deploy to specific domain only
- Use Google Groups for access control
- Set `ALLOWED_DOMAINS` in properties

## 📋 Checklist

- [ ] API key and agent ID configured
- [ ] Web app deployed and tested
- [ ] Chat bot configured (optional)
- [ ] Sheets functions working (optional)
- [ ] Rate limits appropriate
- [ ] Error handling tested

## 🔗 Quick Links

- [Get API Key](https://app.customgpt.ai/settings)
- [Apps Script Docs](https://developers.google.com/apps-script)
- [Google Chat Bots](https://developers.google.com/chat)
- [Troubleshooting Guide](README.md#troubleshooting)

## 💡 Next Steps

1. **Customize UI**: Edit `styles.html` for branding
2. **Add Features**: Extend `Code.gs` with new functions
3. **Monitor Usage**: Check execution logs regularly
4. **Share**: Deploy to your team or organization

---

Need help? Check the full [README.md](README.md) or [CustomGPT Docs](https://docs.customgpt.ai)