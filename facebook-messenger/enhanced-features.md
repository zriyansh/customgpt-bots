# Enhanced Features Guide

## Starter Questions

### Dynamic Starter Questions from CustomGPT

Fetch starter questions from your agent settings:

```javascript
async function getStarterQuestions() {
  try {
    const response = await axios.get(
      `${config.CUSTOMGPT_API_URL}/projects/${config.CUSTOMGPT_AGENT_ID}/settings`,
      {
        headers: {
          'Authorization': `Bearer ${config.CUSTOMGPT_API_KEY}`
        }
      }
    );
    
    const settings = response.data.data;
    return settings.example_questions || defaultQuestions;
  } catch (error) {
    console.error('Failed to fetch starter questions');
    return defaultQuestions;
  }
}
```

### Persistent Menu

Configure in Facebook App Dashboard or via API:

```javascript
async function setPersistentMenu() {
  const menu = {
    persistent_menu: [{
      locale: "default",
      composer_input_disabled: false,
      call_to_actions: [
        {
          title: "🏠 Get Started",
          type: "postback",
          payload: "GET_STARTED"
        },
        {
          title: "❓ Help",
          type: "postback",
          payload: "HELP"
        },
        {
          title: "💡 Examples",
          type: "postback",
          payload: "EXAMPLES"
        }
      ]
    }]
  };
  
  // POST to Facebook API
}
```

---

## Advanced Security

### Input Validation

```javascript
function validateInput(text) {
  // Length check
  if (text.length > 1000) {
    return { valid: false, reason: "Message too long" };
  }
  
  // Blocked patterns
  const blockedPatterns = [
    /\b(password|token|secret|key)\b/i,
    /<script/i,
    /DROP TABLE/i,
    /\.\.\//g
  ];
  
  for (const pattern of blockedPatterns) {
    if (pattern.test(text)) {
      return { valid: false, reason: "Invalid content" };
    }
  }
  
  return { valid: true };
}
```

### User Whitelisting

```javascript
const ALLOWED_USERS = process.env.ALLOWED_USERS?.split(',') || [];
const BLOCKED_USERS = process.env.BLOCKED_USERS?.split(',') || [];

function isUserAllowed(userId) {
  if (BLOCKED_USERS.includes(userId)) return false;
  if (ALLOWED_USERS.length > 0) {
    return ALLOWED_USERS.includes(userId);
  }
  return true;
}
```

### Enhanced Rate Limiting

```javascript
class RateLimiter {
  constructor() {
    this.limits = new Map();
  }
  
  check(userId, limits = {
    minute: 5,
    hour: 50,
    day: 100
  }) {
    const now = Date.now();
    const userLimits = this.limits.get(userId) || {
      minute: { count: 0, reset: now + 60000 },
      hour: { count: 0, reset: now + 3600000 },
      day: { count: 0, reset: now + 86400000 }
    };
    
    // Check and update each limit
    for (const [period, limit] of Object.entries(limits)) {
      const periodData = userLimits[period];
      
      if (now > periodData.reset) {
        periodData.count = 1;
        periodData.reset = now + (period === 'minute' ? 60000 : 
                                 period === 'hour' ? 3600000 : 86400000);
      } else {
        periodData.count++;
        if (periodData.count > limit) {
          return { allowed: false, period, resetIn: periodData.reset - now };
        }
      }
    }
    
    this.limits.set(userId, userLimits);
    return { allowed: true };
  }
}
```

---

## Rich Responses

### Cards and Carousels

```javascript
async function sendProductCarousel(recipientId, products) {
  const elements = products.map(product => ({
    title: product.name,
    subtitle: product.description,
    image_url: product.image,
    buttons: [{
      type: "postback",
      title: "Learn More",
      payload: `PRODUCT_${product.id}`
    }]
  }));
  
  const messageData = {
    recipient: { id: recipientId },
    message: {
      attachment: {
        type: "template",
        payload: {
          template_type: "generic",
          elements: elements
        }
      }
    }
  };
  
  await callSendAPI(messageData);
}
```

### Media Responses

```javascript
async function sendImage(recipientId, imageUrl) {
  const messageData = {
    recipient: { id: recipientId },
    message: {
      attachment: {
        type: "image",
        payload: {
          url: imageUrl,
          is_reusable: true
        }
      }
    }
  };
  
  await callSendAPI(messageData);
}
```

---

## Analytics and Monitoring

### User Analytics

```javascript
class Analytics {
  constructor() {
    this.events = [];
  }
  
  track(userId, event, properties = {}) {
    this.events.push({
      userId,
      event,
      properties,
      timestamp: new Date().toISOString()
    });
    
    // Send to analytics service
    if (this.events.length >= 10) {
      this.flush();
    }
  }
  
  async flush() {
    // Send to Google Analytics, Mixpanel, etc.
    this.events = [];
  }
}

// Usage
analytics.track(userId, 'message_sent', {
  messageLength: text.length,
  hasAttachment: false,
  conversationId: sessionId
});
```

### Error Tracking

```javascript
function logError(error, context = {}) {
  console.error('Bot Error:', {
    message: error.message,
    stack: error.stack,
    context,
    timestamp: new Date().toISOString()
  });
  
  // Send to error tracking service (Sentry, etc.)
}
```

---

## Conversation Features

### Context Management

```javascript
class ConversationContext {
  constructor(userId) {
    this.userId = userId;
    this.context = {
      messages: [],
      topics: [],
      language: 'en',
      preferences: {}
    };
  }
  
  addMessage(role, content) {
    this.context.messages.push({
      role,
      content,
      timestamp: Date.now()
    });
    
    // Keep last 10 messages
    if (this.context.messages.length > 10) {
      this.context.messages.shift();
    }
  }
  
  getContext() {
    return this.context;
  }
}
```

### Multi-language Support

```javascript
async function detectLanguage(text) {
  // Use a language detection service or library
  // For now, check CustomGPT response language
  return 'en';
}

async function respondInLanguage(userId, response, language) {
  const translations = {
    'es': {
      'sources': 'Fuentes',
      'help': 'Ayuda',
      'examples': 'Ejemplos'
    },
    'fr': {
      'sources': 'Sources',
      'help': 'Aide',
      'examples': 'Exemples'
    }
  };
  
  // Apply translations
  if (translations[language]) {
    // Translate UI elements
  }
  
  return response;
}
```

---

## Integration Features

### Webhook for External Systems

```javascript
app.post('/external-webhook', async (req, res) => {
  const { userId, message, metadata } = req.body;
  
  // Trigger bot response
  await handleCustomGPTQuery(userId, message);
  
  res.json({ success: true });
});
```

### API Endpoints

```javascript
// Get conversation history
app.get('/api/conversations/:userId', async (req, res) => {
  const { userId } = req.params;
  const history = await getConversationHistory(userId);
  res.json(history);
});

// Send broadcast message
app.post('/api/broadcast', async (req, res) => {
  const { userIds, message } = req.body;
  
  for (const userId of userIds) {
    await sendTextMessage(userId, message);
  }
  
  res.json({ sent: userIds.length });
});
```

---

## Performance Optimization

### Caching Strategy

```javascript
const responseCache = new NodeCache({ 
  stdTTL: 300, // 5 minutes
  checkperiod: 60 
});

async function getCachedResponse(query) {
  const cacheKey = crypto
    .createHash('md5')
    .update(query.toLowerCase())
    .digest('hex');
  
  const cached = responseCache.get(cacheKey);
  if (cached) return cached;
  
  const response = await sendToCustomGPT(sessionId, query);
  responseCache.set(cacheKey, response);
  
  return response;
}
```

### Async Processing

```javascript
// Process messages in background
async function processMessageAsync(senderId, message) {
  // Acknowledge immediately
  await sendTypingOn(senderId);
  
  // Process in background
  setImmediate(async () => {
    try {
      await handleCustomGPTQuery(senderId, message.text);
    } catch (error) {
      await sendTextMessage(senderId, "Sorry, an error occurred.");
    } finally {
      await sendTypingOff(senderId);
    }
  });
}
```

---

## Testing and Debugging

### Test Suite

```javascript
// test.js
const axios = require('axios');

async function testWebhook() {
  const response = await axios.get('http://localhost:3000/webhook', {
    params: {
      'hub.mode': 'subscribe',
      'hub.verify_token': process.env.FB_VERIFY_TOKEN,
      'hub.challenge': 'test123'
    }
  });
  
  console.assert(response.data === 'test123', 'Webhook verification failed');
}

async function testMessage() {
  const response = await axios.post('http://localhost:3000/webhook', {
    object: 'page',
    entry: [{
      messaging: [{
        sender: { id: 'TEST_USER' },
        message: { text: 'Hello bot' }
      }]
    }]
  });
  
  console.assert(response.status === 200, 'Message handling failed');
}
```

### Debug Mode

```javascript
const DEBUG = process.env.DEBUG === 'true';

function debug(message, data) {
  if (DEBUG) {
    console.log(`[DEBUG] ${message}`, data);
  }
}

// Usage
debug('CustomGPT Response', response);
```