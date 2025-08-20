# Quick Start Guide - Facebook Messenger Bot

## 🚀 Fastest Setup (15 minutes)

### Option 1: Google Apps Script (Simplest, Free Forever)

1. **Copy Script**
   - Open [script.google.com](https://script.google.com)
   - Create new project
   - Copy code from `google-apps-script/Code.gs`

2. **Add Credentials**
   - Project Settings > Script Properties
   - Add your keys:
     - `FB_VERIFY_TOKEN`: random-string-123
     - `FB_PAGE_ACCESS_TOKEN`: (from Facebook)
     - `CUSTOMGPT_API_KEY`: (from CustomGPT)
     - `CUSTOMGPT_PROJECT_ID`: (your agent ID)

3. **Deploy**
   - Deploy > New deployment > Web app
   - Execute as: Me, Access: Anyone
   - Copy URL

4. **Connect Facebook**
   - Facebook App > Messenger > Webhooks
   - URL: Your Apps Script URL
   - Verify Token: random-string-123
   - Subscribe to: messages, messaging_postbacks

✅ **Done! Message your Facebook page**

---

### Option 2: Vercel (Modern, Scalable)

1. **Click Deploy**
   
   [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/customgpt-fb-messenger)

2. **Add Environment Variables**
   ```
   FB_VERIFY_TOKEN=random-string-123
   FB_PAGE_ACCESS_TOKEN=your-token
   FB_APP_SECRET=your-secret
   CUSTOMGPT_API_KEY=your-key
   CUSTOMGPT_AGENT_ID=your-id
   ```

3. **Connect Facebook**
   - Webhook URL: `https://your-app.vercel.app/webhook`
   - Verify Token: random-string-123

✅ **Done! Test your bot**

---

## 📋 Prerequisites Checklist

### Facebook Setup
- [ ] Facebook Page created
- [ ] Facebook App created (Business type)
- [ ] Messenger product added
- [ ] Page Access Token generated

### CustomGPT Setup
- [ ] CustomGPT account
- [ ] API key generated
- [ ] Agent/Project ID noted

---

## 🎯 Features Included

### Core Features
- ✅ CustomGPT integration
- ✅ Rate limiting (20/min, 100/day)
- ✅ Session management
- ✅ Error handling

### Security
- ✅ Webhook verification
- ✅ Input validation
- ✅ User rate limiting
- ✅ Query sanitization

### Chat Features
- ✅ Typing indicators
- ✅ Quick replies
- ✅ Starter questions
- ✅ Commands (help, reset, examples)
- ✅ Citation support

---

## 🛠️ Customization

### Change Rate Limits
```javascript
// In config or environment variables
RATE_LIMIT_REQUESTS=30  // per minute
DAILY_LIMIT=200         // per day
```

### Add Starter Questions
Edit `config.js`:
```javascript
STARTER_QUESTIONS: [
  "Your question 1",
  "Your question 2"
]
```

### Add Commands
Edit `handleMessage()` function:
```javascript
case 'yourcommand':
  // Your handler
  break;
```

---

## 🐛 Troubleshooting

### Bot Not Responding
1. Check webhook subscription in Facebook
2. Verify all tokens are correct
3. Check logs (Vercel/Apps Script)

### Rate Limit Errors
- Increase limits in config
- Add user to whitelist

### API Errors
- Verify CustomGPT API key
- Check agent ID is correct
- Monitor API usage

---

## 📚 Resources

- [Full Documentation](README.md)
- [Enhanced Features](enhanced-features.md)
- [Deployment Options](deploy-alternatives.md)
- [Facebook Messenger Docs](https://developers.facebook.com/docs/messenger-platform)
- [CustomGPT API Docs](https://docs.customgpt.ai)

---

## 💬 Support

Need help? Check:
1. Console logs
2. Facebook webhook dashboard
3. CustomGPT usage dashboard
4. Create an issue on GitHub