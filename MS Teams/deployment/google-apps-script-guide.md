# Google Apps Script Deployment for Microsoft Teams Bot

## Overview

While Google Apps Script (GAS) is primarily designed for Google Workspace integrations, it has significant limitations for Microsoft Teams bots. This guide explains the challenges and provides alternative serverless solutions.

## Why Google Apps Script is NOT Recommended for Teams Bots

### Technical Limitations

1. **No WebSocket Support**: Teams bots require real-time messaging capabilities
2. **Limited HTTP Methods**: GAS only supports GET and POST
3. **No Custom Headers**: Cannot properly handle Bot Framework authentication
4. **Execution Time Limits**: 6 minutes max, not suitable for long conversations
5. **No Async/Await**: Limited async programming support
6. **No External Libraries**: Cannot use Bot Framework SDK
7. **CORS Restrictions**: Cannot properly handle Teams domain requirements

### Security Concerns

1. **No Proper Authentication**: Cannot implement Bot Framework security
2. **Limited Token Validation**: Cannot validate JWT tokens properly
3. **No Certificate Pinning**: Security vulnerabilities
4. **Public Endpoints Only**: No IP whitelisting or network security

### Missing Features

1. **No Adaptive Cards**: Cannot render rich Teams UI
2. **No Proactive Messaging**: Cannot send notifications
3. **No File Handling**: Cannot process Teams attachments
4. **No Threading**: Cannot maintain conversation context
5. **No Teams-specific Features**: Meetings, mentions, channels

## Recommended Free Alternatives

### 1. Azure Functions (Serverless)

**Best for**: Production Teams bots with automatic scaling

```javascript
// Azure Function example
module.exports = async function (context, req) {
    const adapter = new BotFrameworkAdapter({
        appId: process.env.MicrosoftAppId,
        appPassword: process.env.MicrosoftAppPassword
    });
    
    await adapter.processActivity(req, context.res, async (turnContext) => {
        await bot.run(turnContext);
    });
};
```

**Free Tier**: 1 million requests/month

### 2. AWS Lambda

**Best for**: Existing AWS infrastructure

```python
import json
from botbuilder.core import BotFrameworkAdapter
from bot import CustomGPTBot

def lambda_handler(event, context):
    adapter = BotFrameworkAdapter(settings)
    bot = CustomGPTBot()
    
    return adapter.process(event['body'], event['headers'], bot.on_turn)
```

**Free Tier**: 1 million requests/month

### 3. Google Cloud Functions

**Best for**: Google Cloud users who need Teams integration

```python
from flask import Request, Response
from botbuilder.core import BotFrameworkAdapter

def teams_bot(request: Request) -> Response:
    adapter = BotFrameworkAdapter(settings)
    bot = CustomGPTBot()
    
    if request.method == "POST":
        body = request.get_json()
        headers = dict(request.headers)
        
        response = adapter.process_activity(body, headers, bot.on_turn)
        return Response(response, status=201)
```

**Free Tier**: 2 million invocations/month

### 4. Vercel

**Best for**: Simple deployments with great DX

```javascript
// api/messages.js
import { BotFrameworkAdapter } from 'botbuilder';

export default async function handler(req, res) {
    const adapter = new BotFrameworkAdapter({
        appId: process.env.APP_ID,
        appPassword: process.env.APP_PASSWORD
    });
    
    await adapter.processActivity(req, res, async (context) => {
        await bot.run(context);
    });
}
```

**Free Tier**: Unlimited requests (with limits)

### 5. Cloudflare Workers

**Best for**: Edge deployment with low latency

```javascript
export default {
    async fetch(request, env) {
        const adapter = new BotFrameworkAdapter({
            appId: env.APP_ID,
            appPassword: env.APP_PASSWORD
        });
        
        return await adapter.handleRequest(request);
    }
};
```

**Free Tier**: 100,000 requests/day

## Minimal Working Example (Without Full Bot Framework)

If you absolutely must use a limited platform, here's a minimal webhook that forwards to CustomGPT:

```python
# Minimal Teams webhook (NOT RECOMMENDED for production)
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/messages', methods=['POST'])
def messages():
    try:
        # Extract message from Teams
        data = request.json
        if data.get('type') == 'message':
            user_message = data.get('text', '')
            
            # Forward to CustomGPT
            customgpt_response = requests.post(
                'https://app.customgpt.ai/api/v1/messages',
                json={
                    'query': user_message,
                    'project_id': 'YOUR_PROJECT_ID'
                },
                headers={
                    'Authorization': f'Bearer YOUR_API_KEY'
                }
            )
            
            # Send response back to Teams
            return jsonify({
                'type': 'message',
                'text': customgpt_response.json()['response']['text']
            })
    except Exception as e:
        return jsonify({'text': 'Error processing message'}), 500

if __name__ == '__main__':
    app.run(port=3978)
```

**⚠️ WARNING**: This minimal example lacks:
- Proper authentication
- Rate limiting
- Error handling
- Conversation context
- Teams features
- Security validation

## Migration Path from Google Apps Script

If you're currently trying to use GAS, here's how to migrate:

### 1. Export Your Logic
```javascript
// Save your current GAS logic
function saveCurrentLogic() {
    // Your CustomGPT integration logic
    const customGPTQuery = (message) => {
        // Your implementation
    };
}
```

### 2. Choose a Platform
Based on your needs:
- **Simple bot**: Vercel or Netlify
- **Enterprise**: Azure Functions
- **Existing infrastructure**: Match your cloud provider

### 3. Implement Bot Framework
```bash
# Install Bot Framework
npm install botbuilder botbuilder-core

# Or for Python
pip install botbuilder-core
```

### 4. Deploy and Test
Follow the deployment guide for your chosen platform.

## Comparison Table

| Feature | Google Apps Script | Azure Functions | AWS Lambda | Vercel |
|---------|-------------------|-----------------|------------|---------|
| Teams SDK Support | ❌ | ✅ | ✅ | ✅ |
| WebSockets | ❌ | ✅ | ✅ | ⚠️ |
| Adaptive Cards | ❌ | ✅ | ✅ | ✅ |
| Authentication | ❌ | ✅ | ✅ | ✅ |
| Free Tier | ✅ | ✅ | ✅ | ✅ |
| Setup Complexity | Low | Medium | Medium | Low |
| Production Ready | ❌ | ✅ | ✅ | ✅ |

## Conclusion

While Google Apps Script is excellent for Google Workspace integrations, it's not suitable for Microsoft Teams bots. Use proper serverless platforms that support the Bot Framework SDK for a secure, feature-rich Teams bot experience.

For the easiest free deployment, we recommend:
1. **Vercel** - Simplest setup
2. **Azure Functions** - Best Teams integration
3. **Railway/Render** - Good free tiers

See the main [README.md](../README.md) for detailed deployment instructions on these platforms.