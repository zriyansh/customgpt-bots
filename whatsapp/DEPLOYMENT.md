# WhatsApp Bot Deployment Guide

Complete guide for deploying your CustomGPT WhatsApp bot to various free hosting providers.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Twilio Setup](#twilio-setup)
3. [Deployment Options](#deployment-options)
   - [Railway](#railway-recommended)
   - [Render](#render)
   - [Fly.io](#flyio)
   - [Google Apps Script](#google-apps-script)
   - [Other Options](#other-free-alternatives)
4. [Post-Deployment](#post-deployment)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have:

1. **CustomGPT Credentials**
   - API Key from your CustomGPT dashboard
   - Agent/Project ID

2. **Twilio Account**
   - Sign up at [twilio.com](https://www.twilio.com)
   - Get free trial credit ($15)
   - Verify your phone number

3. **Code Repository**
   - Push your code to GitHub
   - Make sure `.env` is in `.gitignore`

## Twilio Setup

### Step 1: Get WhatsApp Sandbox (for testing)

1. Log in to [Twilio Console](https://console.twilio.com)
2. Go to "Messaging" → "Try it out" → "Send a WhatsApp message"
3. Follow the instructions to join the sandbox
4. Note your sandbox number (e.g., `whatsapp:+14155238886`)

### Step 2: Get Credentials

1. Go to Account → API keys & tokens OR Click on Phone Number section in the sidenav. Note - You need to choose developer when you login to Twilio.
2. Note your:
   - Account SID
   - Auth Token
   - WhatsApp number

### Step 3: Configure Webhook (after deployment)

You'll set this after deploying your bot.

## Deployment Options

## Railway (Recommended)

**Free Tier**: 500 hours/month, $5 credit

### Steps:

1. **Sign up** at [railway.app](https://railway.app)

2. **Install Railway CLI** (optional):
   ```bash
   npm install -g @railway/cli
   ```

3. **Deploy via GitHub**:
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python

4. **Configure Environment Variables**:
   - Go to your project → Variables
   - Add all variables from `.env.example`:
     ```
     CUSTOMGPT_API_KEY=your_key
     CUSTOMGPT_PROJECT_ID=your_id
     TWILIO_ACCOUNT_SID=your_sid
     TWILIO_AUTH_TOKEN=your_token
     TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
     RATE_LIMIT_DAILY=100
     # ... add all other variables
     ```

5. **Get your URL**:
   - Go to Settings → Domains
   - Your URL will be like: `https://your-app.up.railway.app`

6. **Configure Twilio Webhook**:
   - In Twilio Sandbox settings
   - Set webhook URL: `https://your-app.up.railway.app/webhook/whatsapp`

### CLI Deployment:

```bash
# Login
railway login

# Initialize project
railway init

# Link to existing project
railway link

# Deploy
railway up

# View logs
railway logs
```

## Render

**Free Tier**: 750 hours/month

### Steps:

1. **Sign up** at [render.com](https://render.com)

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Select your repo

3. **Configure Service**:
   - Name: `customgpt-whatsapp-bot`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`

4. **Add Environment Variables**:
   - Go to Environment tab
   - Add all variables from `.env.example`

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment
   - Note your URL: `https://your-app.onrender.com`

6. **Configure Twilio**:
   - Set webhook: `https://your-app.onrender.com/webhook/whatsapp`

## Fly.io

**Free Tier**: 3 shared-cpu-1x VMs

### Steps:

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Sign up and login**:
   ```bash
   fly auth signup
   # or
   fly auth login
   ```

3. **Launch app**:
   ```bash
   cd whatsapp
   fly launch
   ```
   - Choose app name
   - Select region (closest to you)
   - Don't deploy yet

4. **Configure secrets**:
   ```bash
   fly secrets set CUSTOMGPT_API_KEY="your_key"
   fly secrets set CUSTOMGPT_PROJECT_ID="your_id"
   fly secrets set TWILIO_ACCOUNT_SID="your_sid"
   fly secrets set TWILIO_AUTH_TOKEN="your_token"
   fly secrets set TWILIO_WHATSAPP_NUMBER="whatsapp:+14155238886"
   # Set all other secrets
   ```

5. **Deploy**:
   ```bash
   fly deploy
   ```

6. **Get URL**:
   ```bash
   fly status
   # Your URL: https://your-app.fly.dev
   ```

7. **Configure Twilio**:
   - Set webhook: `https://your-app.fly.dev/webhook/whatsapp`

## Google Apps Script

**Free Tier**: Unlimited (with quotas)

Simplest option - no server needed!

### Steps:

1. **Go to** [script.google.com](https://script.google.com)

2. **Create new project**

3. **Copy code** from `google-apps-script/Code.gs`

4. **Set Script Properties**:
   - Project Settings → Script Properties
   - Add all required properties

5. **Deploy**:
   - Deploy → New Deployment
   - Type: Web app
   - Execute as: Me
   - Access: Anyone

6. **Get URL** and configure in Twilio

See detailed instructions in `google-apps-script/README.md`

## Other Free Alternatives

### Koyeb

**Free Tier**: 2 services, 1 vCPU, 256MB RAM

```bash
# Install CLI
curl -fsSL https://cli.koyeb.com/install.sh | sh

# Deploy
koyeb app create customgpt-whatsapp
koyeb service create customgpt-whatsapp \
  --git github.com/yourusername/yourrepo \
  --git-branch main \
  --ports 8000:http \
  --routes /:8000
```

### Cyclic.sh

**Free Tier**: 10,000 requests/month

1. Connect GitHub at [cyclic.sh](https://cyclic.sh)
2. Select repository
3. Add environment variables
4. Deploy

### Deta Space

**Free Tier**: Always free, 10GB storage

```bash
# Install Space CLI
curl -fsSL https://get.deta.dev/space-cli.sh | sh

# Deploy
space new
space push
```

## Post-Deployment

### 1. Test Your Bot

1. Send "Hi" to your Twilio WhatsApp number
2. Check for welcome message
3. Test all commands

### 2. Monitor Logs

- **Railway**: `railway logs`
- **Render**: Dashboard → Logs
- **Fly.io**: `fly logs`
- **Apps Script**: View → Logs

### 3. Set Up Monitoring

1. **Uptime monitoring**:
   - Use [uptimerobot.com](https://uptimerobot.com) (free)
   - Monitor: `https://your-app.com/health`

2. **Error tracking**:
   - Add Sentry (free tier)
   - Or use built-in logging

### 4. Configure Production WhatsApp

Once tested, apply for WhatsApp Business API:
1. Apply through Twilio
2. Get approved number
3. Update webhook URL

## Troubleshooting

### Bot Not Responding

1. **Check webhook URL**:
   ```bash
   curl -X POST https://your-app.com/webhook/whatsapp \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "From=whatsapp:+1234567890&Body=test"
   ```

2. **Check logs** for errors

3. **Verify environment variables** are set

4. **Test Twilio connection**:
   ```python
   # Test script
   from twilio.rest import Client
   client = Client(account_sid, auth_token)
   message = client.messages.create(
     to='whatsapp:+1234567890',
     from_='whatsapp:+14155238886',
     body='Test message'
   )
   ```

### Rate Limiting Issues

1. Increase limits in environment variables
2. Implement Redis for production
3. Monitor usage with `/stats` command

### Memory Issues

1. **Add Redis** for session/rate limit storage
2. **Optimize code**:
   - Remove unused imports
   - Use connection pooling
   - Implement caching

### SSL/Security Issues

1. All platforms provide free SSL
2. Never expose sensitive credentials
3. Use environment variables only

## Scaling Considerations

When you outgrow free tiers:

1. **Upgrade hosting**:
   - Railway: Pay as you go
   - Render: $7/month starter
   - Fly.io: Pay for additional resources

2. **Add Redis**:
   - Redis Cloud free tier (30MB)
   - Or upgrade to paid Redis

3. **Implement queuing**:
   - For high message volume
   - Use Redis + background workers

4. **Multiple instances**:
   - Load balance across instances
   - Share Redis for state

## Security Best Practices

1. **Environment Variables**:
   - Never commit `.env` file
   - Use platform secret management

2. **Webhook Security**:
   - Validate Twilio signatures
   - Implement request validation

3. **Rate Limiting**:
   - Always enabled
   - Monitor for abuse

4. **Access Control**:
   - Implement phone number whitelist
   - Admin commands protection

## Support

- **Deployment issues**: Check platform documentation
- **Twilio issues**: [Twilio Support](https://support.twilio.com)
- **CustomGPT issues**: Check API documentation
- **Bot issues**: Review logs and error messages