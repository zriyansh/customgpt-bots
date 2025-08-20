# Deployment Guide for CustomGPT Discord Bot

This guide covers multiple free hosting options for your Discord bot.

## Free Hosting Options Comparison

| Platform | Free Tier | Always On | Pros | Cons |
|----------|-----------|-----------|------|------|
| Railway | 500 hours/month | Yes | Easy deploy, Good performance | Limited hours |
| Fly.io | 3 shared VMs | Yes | Great performance, Global | Complex setup |
| Replit | Unlimited | No* | Easiest setup | Needs keepalive |
| Render | 750 hours/month | Yes | Simple, Reliable | Limited hours |
| Oracle Cloud | Always Free tier | Yes | Full VPS control | Complex setup |

*Can be kept alive with external monitoring

## 1. Railway Deployment (Recommended)

Railway offers $5 free credit monthly (about 500 hours of runtime).

### Steps:

1. **Sign up** at [railway.app](https://railway.app)

2. **Install CLI**:
   ```bash
   npm install -g @railway/cli
   ```

3. **Deploy**:
   ```bash
   cd discord
   railway login
   railway init
   railway up
   ```

4. **Set Environment Variables**:
   - Go to your project dashboard
   - Click on your service
   - Go to Variables tab
   - Add all variables from `.env.example`

5. **View Logs**:
   ```bash
   railway logs
   ```

## 2. Fly.io Deployment

Fly.io offers 3 shared-cpu-1x VMs with 256MB RAM free.

### Steps:

1. **Sign up** at [fly.io](https://fly.io)

2. **Install CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

3. **Create App**:
   ```bash
   cd discord
   flyctl launch --no-deploy
   ```

4. **Set Secrets**:
   ```bash
   flyctl secrets set DISCORD_BOT_TOKEN="your_token" \
     CUSTOMGPT_API_KEY="your_key" \
     CUSTOMGPT_AGENT_ID="your_id"
   ```

5. **Deploy**:
   ```bash
   flyctl deploy
   ```

6. **Monitor**:
   ```bash
   flyctl logs
   flyctl status
   ```

## 3. Replit Deployment

Replit is free but stops after inactivity. Use with UptimeRobot.

### Steps:

1. **Create Repl**:
   - Go to [replit.com](https://replit.com)
   - Create new Python repl
   - Import from GitHub or upload files

2. **Set Secrets**:
   - Click Secrets (🔒) in sidebar
   - Add all environment variables

3. **Install Dependencies**:
   - Replit auto-installs from requirements.txt

4. **Keep Alive**:
   - Create account at [uptimerobot.com](https://uptimerobot.com)
   - Add HTTP monitor for your Repl URL
   - Set to ping every 5 minutes

5. **Web Server for Monitoring** (add to bot.py):
   ```python
   from flask import Flask
   from threading import Thread
   
   app = Flask('')
   
   @app.route('/')
   def home():
       return "Bot is alive!"
   
   def run():
       app.run(host='0.0.0.0', port=8080)
   
   def keep_alive():
       t = Thread(target=run)
       t.start()
   
   # Add before bot.run()
   if os.getenv('REPL_ID'):  # Only on Replit
       keep_alive()
   ```

## 4. Render Deployment

Render offers 750 hours/month free.

### Steps:

1. **Create account** at [render.com](https://render.com)

2. **New Web Service**:
   - Connect GitHub repo
   - Choose Python environment
   - Build command: `pip install -r requirements.txt`
   - Start command: `python bot.py`

3. **Environment Variables**:
   - Add in dashboard under Environment

4. **Deploy**:
   - Automatic on git push

## 5. Oracle Cloud (Advanced)

Oracle offers Always Free VMs (1 OCPU, 1GB RAM).

### Steps:

1. **Create VM**:
   - Sign up at [cloud.oracle.com](https://cloud.oracle.com)
   - Create Compute instance (Ubuntu)
   - Open port 22 for SSH

2. **Setup Server**:
   ```bash
   # SSH into server
   ssh ubuntu@your_server_ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and Git
   sudo apt install python3.10 python3.10-venv git -y
   
   # Clone repository
   git clone your_repo_url
   cd discord
   
   # Setup
   ./setup.sh
   ```

3. **Install as Service**:
   ```bash
   # Copy service file
   sudo cp discord-bot.service /etc/systemd/system/
   
   # Create bot user
   sudo useradd -r -s /bin/false botuser
   sudo chown -R botuser:botuser /path/to/bot
   
   # Enable service
   sudo systemctl enable discord-bot
   sudo systemctl start discord-bot
   ```

4. **Monitor**:
   ```bash
   sudo systemctl status discord-bot
   sudo journalctl -u discord-bot -f
   ```

## Docker Deployment (Any VPS)

For any VPS with Docker:

```bash
# Clone and enter directory
git clone your_repo_url
cd discord

# Create .env file
cp .env.example .env
nano .env  # Edit with your values

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

## Post-Deployment Checklist

- [ ] Bot shows as online in Discord
- [ ] Commands respond correctly
- [ ] Rate limiting works
- [ ] Starter questions load
- [ ] Error handling works
- [ ] Logs are accessible
- [ ] Monitoring is set up

## Monitoring & Maintenance

### Health Checks

1. **UptimeRobot**: Free monitoring
2. **Better Stack**: Free tier with status page
3. **Fly.io**: Built-in health checks

### Logs

Check logs regularly:
- Railway: `railway logs`
- Fly.io: `flyctl logs`
- Docker: `docker-compose logs`
- SystemD: `journalctl -u discord-bot`

### Updates

1. Test locally first
2. Update git repository
3. Deploy:
   - Railway: Auto-deploys
   - Fly.io: `flyctl deploy`
   - Render: Auto-deploys
   - Docker: `docker-compose pull && docker-compose up -d`

## Troubleshooting

### Bot Offline
- Check logs for errors
- Verify token is correct
- Ensure hosting platform is running

### High Memory Usage
- Implement conversation cleanup
- Use Redis for caching
- Monitor for memory leaks

### Rate Limit Issues
- Use Redis for distributed limiting
- Adjust limits based on usage
- Monitor for abuse

## Cost Optimization

To stay within free tiers:
1. Use efficient code
2. Implement caching
3. Clean up old conversations
4. Monitor resource usage
5. Set up alerts for limits

## Security Notes

1. Never expose tokens in logs
2. Use environment variables
3. Enable 2FA on all platforms
4. Regularly rotate tokens
5. Monitor for suspicious activity