# Deploy to Vercel (Recommended)

Vercel offers the best free tier for webhook-based bots with automatic HTTPS and global CDN.

## Prerequisites
- GitHub account
- Vercel account (free)
- Facebook App configured
- CustomGPT API credentials

## Step 1: Prepare Your Code
1. Fork/clone this repository
2. Push to your GitHub account
3. Copy `.env.example` to `.env` and fill in values

## Step 2: Deploy to Vercel

### Option A: One-Click Deploy
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/customgpt-fb-messenger&env=FB_VERIFY_TOKEN,FB_PAGE_ACCESS_TOKEN,FB_APP_SECRET,CUSTOMGPT_API_KEY,CUSTOMGPT_AGENT_ID)

### Option B: Manual Deploy
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Configure environment variables:
   ```
   FB_VERIFY_TOKEN=your-verify-token
   FB_PAGE_ACCESS_TOKEN=your-page-token
   FB_APP_SECRET=your-app-secret
   CUSTOMGPT_API_KEY=your-api-key
   CUSTOMGPT_AGENT_ID=your-agent-id
   ```
5. Click "Deploy"

### Option C: CLI Deploy
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables
vercel env add FB_VERIFY_TOKEN production
vercel env add FB_PAGE_ACCESS_TOKEN production
vercel env add FB_APP_SECRET production
vercel env add CUSTOMGPT_API_KEY production
vercel env add CUSTOMGPT_AGENT_ID production

# Redeploy with env vars
vercel --prod
```

## Step 3: Configure Facebook Webhook
1. Copy your Vercel URL: `https://your-app.vercel.app`
2. In Facebook App Dashboard:
   - Webhook URL: `https://your-app.vercel.app/webhook`
   - Verify Token: Your `FB_VERIFY_TOKEN`
   - Subscribe to: `messages`, `messaging_postbacks`

## Step 4: Test Your Bot
1. Send a message to your Facebook Page
2. Check Vercel logs: `vercel logs`

## Vercel Features
- ✅ Free tier: 100GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Global CDN (18+ regions)
- ✅ Serverless functions
- ✅ Zero configuration
- ✅ GitHub integration

## Monitoring
1. Vercel Dashboard: View function logs
2. Analytics: Built-in performance metrics
3. Alerts: Set up error notifications

## Scaling
Vercel automatically scales your bot:
- Concurrent executions: 1000 (free tier)
- Function duration: 10 seconds
- Memory: 1024 MB

## Troubleshooting

### Webhook Verification Failed
- Check `FB_VERIFY_TOKEN` matches
- Ensure webhook URL is correct
- View logs: `vercel logs`

### Bot Not Responding
- Check environment variables are set
- Verify Facebook Page token is valid
- Check function logs for errors

### Rate Limit Issues
- Vercel has generous limits for webhooks
- Consider upgrading if hitting limits

## Custom Domain (Optional)
1. Add domain in Vercel dashboard
2. Update Facebook webhook URL
3. Vercel handles SSL automatically