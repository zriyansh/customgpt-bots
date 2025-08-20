# Deployment Guide for CustomGPT Slack Bot

This guide covers deployment options for the CustomGPT Slack Bot, from free solutions to enterprise-grade hosting.

## Deployment Options Overview

| Platform | Cost | Pros | Cons | Best For |
|----------|------|------|------|----------|
| Google Apps Script | Free | No servers, Auto-scaling | 6-min limit, Limited features | Small teams, Testing |
| Railway | $5/month credit | Easy deployment, Good DX | Limited free tier | Small-medium teams |
| Render | Free tier | Auto-deploy from GitHub | Sleeps after 15 min | Development, Small teams |
| Fly.io | Free tier | Global deployment | Requires credit card | Production, Global teams |
| AWS/GCP/Azure | Pay-as-you-go | Full control, Scalable | Complex setup | Enterprise |

## 1. Google Apps Script (Free, Serverless)

See the detailed guide in `google-apps-script/README.md`

**Quick Start:**
```bash
# No installation needed - all web-based
# 1. Copy Code.gs to script.google.com
# 2. Set Script Properties
# 3. Deploy as Web App
# 4. Add URL to Slack
```

## 2. Railway Deployment

### Prerequisites
- Railway account (no credit card for $5 credit)
- GitHub account

### Steps

1. **Prepare your code:**
```bash
# Create a new GitHub repository
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO
git push -u origin main
```

2. **Create `railway.json`:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python bot.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

3. **Deploy to Railway:**
- Go to [railway.app](https://railway.app)
- Click "New Project" → "Deploy from GitHub repo"
- Select your repository
- Add environment variables:
  - `SLACK_BOT_TOKEN`
  - `SLACK_SIGNING_SECRET`
  - `CUSTOMGPT_API_KEY`
  - `CUSTOMGPT_PROJECT_ID`
- Click "Deploy"

4. **Get your URL:**
- Go to Settings → Domains
- Generate a domain or use the provided one
- Update Slack Event Subscriptions URL

## 3. Render Deployment

### Steps

1. **Create `render.yaml`:**
```yaml
services:
  - type: web
    name: customgpt-slack-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python bot.py
    envVars:
      - key: SLACK_BOT_TOKEN
        sync: false
      - key: SLACK_SIGNING_SECRET
        sync: false
      - key: CUSTOMGPT_API_KEY
        sync: false
      - key: CUSTOMGPT_PROJECT_ID
        sync: false
```

2. **Deploy to Render:**
- Push code to GitHub
- Go to [render.com](https://render.com)
- New → Web Service → Connect GitHub
- Select repository
- Use the following settings:
  - Name: customgpt-slack-bot
  - Environment: Python 3
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `python bot.py`
- Add environment variables
- Click "Create Web Service"

## 4. Fly.io Deployment

### Prerequisites
- Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
- Credit card (for verification, free tier available)

### Steps

1. **Create `fly.toml`:**
```toml
app = "customgpt-slack-bot"
primary_region = "ord"

[http_service]
  internal_port = 3000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[env]
  PORT = "3000"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

2. **Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["python", "bot.py"]
```

3. **Deploy:**
```bash
# Login to Fly
fly auth login

# Create app
fly apps create customgpt-slack-bot

# Set secrets
fly secrets set SLACK_BOT_TOKEN=xoxb-your-token
fly secrets set SLACK_SIGNING_SECRET=your-secret
fly secrets set CUSTOMGPT_API_KEY=your-api-key
fly secrets set CUSTOMGPT_PROJECT_ID=your-project-id

# Deploy
fly deploy

# Get URL
fly info
```

## 5. Docker Deployment (VPS/Cloud)

### Build and Run

1. **Create `Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:3000/health')"

# Run the bot
CMD ["python", "bot.py"]
```

2. **Create `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  bot:
    build: .
    ports:
      - "3000:3000"
    environment:
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
      - SLACK_SIGNING_SECRET=${SLACK_SIGNING_SECRET}
      - CUSTOMGPT_API_KEY=${CUSTOMGPT_API_KEY}
      - CUSTOMGPT_PROJECT_ID=${CUSTOMGPT_PROJECT_ID}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

3. **Deploy:**
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f bot

# Update
git pull
docker-compose build
docker-compose up -d
```

## 6. Kubernetes Deployment

### Create Kubernetes Manifests

1. **`deployment.yaml`:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: customgpt-slack-bot
spec:
  replicas: 2
  selector:
    matchLabels:
      app: customgpt-slack-bot
  template:
    metadata:
      labels:
        app: customgpt-slack-bot
    spec:
      containers:
      - name: bot
        image: your-registry/customgpt-slack-bot:latest
        ports:
        - containerPort: 3000
        env:
        - name: SLACK_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: slack-secrets
              key: bot-token
        - name: SLACK_SIGNING_SECRET
          valueFrom:
            secretKeyRef:
              name: slack-secrets
              key: signing-secret
        - name: CUSTOMGPT_API_KEY
          valueFrom:
            secretKeyRef:
              name: customgpt-secrets
              key: api-key
        - name: CUSTOMGPT_PROJECT_ID
          valueFrom:
            configMapKeyRef:
              name: bot-config
              key: project-id
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: customgpt-slack-bot
spec:
  selector:
    app: customgpt-slack-bot
  ports:
  - port: 80
    targetPort: 3000
  type: LoadBalancer
```

2. **Deploy to Kubernetes:**
```bash
# Create secrets
kubectl create secret generic slack-secrets \
  --from-literal=bot-token=xoxb-your-token \
  --from-literal=signing-secret=your-secret

kubectl create secret generic customgpt-secrets \
  --from-literal=api-key=your-api-key

# Create configmap
kubectl create configmap bot-config \
  --from-literal=project-id=your-project-id

# Deploy
kubectl apply -f deployment.yaml

# Get external IP
kubectl get service customgpt-slack-bot
```

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `SLACK_BOT_TOKEN` | Bot User OAuth Token | Yes |
| `SLACK_SIGNING_SECRET` | For request verification | Yes |
| `CUSTOMGPT_API_KEY` | CustomGPT API key | Yes |
| `CUSTOMGPT_PROJECT_ID` | Default agent ID | Yes |
| `REDIS_URL` | Redis for rate limiting | No |
| `PORT` | Server port (default: 3000) | No |
| `LOG_LEVEL` | Logging level | No |

## SSL/HTTPS Setup

### Using Cloudflare (Recommended)
1. Add your domain to Cloudflare
2. Set SSL/TLS to "Full"
3. Create a CNAME record pointing to your bot
4. Update Slack with the HTTPS URL

### Using Let's Encrypt
```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d your-bot-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Using Nginx Reverse Proxy
```nginx
server {
    listen 443 ssl;
    server_name your-bot-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-bot-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-bot-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring & Logging

### Basic Health Check
Add this to your `bot.py`:
```python
@app.route("/health")
async def health_check(req):
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

### Logging Services
- **Railway**: Built-in logging
- **Render**: Built-in logging  
- **Fly.io**: `fly logs`
- **Docker**: `docker logs` or logging drivers
- **Cloud**: CloudWatch, Stackdriver, Azure Monitor

### Monitoring Services
- **UptimeRobot**: Free uptime monitoring
- **Datadog**: APM and logging (free tier)
- **New Relic**: Application monitoring (free tier)

## Troubleshooting

### Bot Not Responding
1. Check logs for errors
2. Verify environment variables
3. Test Slack Event URL manually
4. Check SSL certificate

### High Latency
1. Check server location vs Slack workspace
2. Monitor CPU/memory usage
3. Review CustomGPT API response times
4. Consider caching strategies

### Rate Limiting Issues
1. Implement Redis for distributed rate limiting
2. Adjust rate limit thresholds
3. Monitor usage patterns
4. Consider user-based quotas

## Scaling Considerations

### Horizontal Scaling
- Use load balancer
- Implement Redis for shared state
- Consider message queue for async processing

### Performance Optimization
- Cache agent settings
- Batch API requests where possible
- Implement connection pooling
- Use CDN for static assets

### Cost Optimization
- Use spot instances where appropriate
- Implement auto-scaling
- Monitor and optimize API usage
- Consider serverless for variable load