const express = require('express');
const bodyParser = require('body-parser');
const crypto = require('crypto');
const axios = require('axios');
const NodeCache = require('node-cache');
require('dotenv').config();

const app = express();
const cache = new NodeCache({ stdTTL: 600 }); // 10 minute cache

// Configuration
const config = {
  // Facebook
  FB_VERIFY_TOKEN: process.env.FB_VERIFY_TOKEN || 'your-verify-token',
  FB_PAGE_ACCESS_TOKEN: process.env.FB_PAGE_ACCESS_TOKEN,
  FB_APP_SECRET: process.env.FB_APP_SECRET,
  
  // CustomGPT
  CUSTOMGPT_API_KEY: process.env.CUSTOMGPT_API_KEY,
  CUSTOMGPT_AGENT_ID: process.env.CUSTOMGPT_AGENT_ID,
  CUSTOMGPT_API_URL: 'https://app.customgpt.ai/api/v1',
  
  // Rate Limiting
  RATE_LIMIT_REQUESTS: parseInt(process.env.RATE_LIMIT_REQUESTS) || 20,
  RATE_LIMIT_WINDOW_MS: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 60000, // 1 minute
  DAILY_LIMIT: parseInt(process.env.DAILY_LIMIT) || 100,
  
  // Server
  PORT: process.env.PORT || 3000
};

// Middleware
app.use(bodyParser.json({ verify: verifyRequestSignature }));
app.use(bodyParser.urlencoded({ extended: false }));

// Rate limiting storage
const rateLimitMap = new Map();
const dailyUsageMap = new Map();

// Webhook verification
app.get('/webhook', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];
  
  if (mode && token) {
    if (mode === 'subscribe' && token === config.FB_VERIFY_TOKEN) {
      console.log('WEBHOOK_VERIFIED');
      res.status(200).send(challenge);
    } else {
      res.sendStatus(403);
    }
  }
});

// Message handler
app.post('/webhook', async (req, res) => {
  const body = req.body;
  
  if (body.object === 'page') {
    // Process each entry
    body.entry.forEach(async (entry) => {
      // Get messaging events
      entry.messaging.forEach(async (event) => {
        console.log('Webhook event:', event);
        
        if (event.message && !event.message.is_echo) {
          await handleMessage(event.sender.id, event.message);
        } else if (event.postback) {
          await handlePostback(event.sender.id, event.postback);
        }
      });
    });
    
    // Return 200 immediately
    res.status(200).send('EVENT_RECEIVED');
  } else {
    res.sendStatus(404);
  }
});

// Handle messages
async function handleMessage(senderId, message) {
  try {
    // Check rate limits
    if (!checkRateLimit(senderId)) {
      await sendTextMessage(senderId, "⏳ You've reached the rate limit. Please try again later.");
      return;
    }
    
    // Send typing indicator
    await sendTypingOn(senderId);
    
    // Handle different message types
    if (message.text) {
      const text = message.text.toLowerCase();
      
      // Handle commands
      if (text === 'help' || text === '/help') {
        await sendHelpMessage(senderId);
      } else if (text === 'reset' || text === '/reset') {
        await resetConversation(senderId);
      } else if (text === 'examples' || text === '/examples') {
        await sendExampleQuestions(senderId);
      } else if (text === 'stats' || text === '/stats') {
        await sendUsageStats(senderId);
      } else {
        // Send to CustomGPT
        await handleCustomGPTQuery(senderId, message.text);
      }
    } else if (message.attachments) {
      await sendTextMessage(senderId, "📎 I can only process text messages at the moment.");
    }
    
    // Send typing off
    await sendTypingOff(senderId);
    
  } catch (error) {
    console.error('Error handling message:', error);
    await sendTextMessage(senderId, "❌ Sorry, something went wrong. Please try again.");
  }
}

// Handle postbacks
async function handlePostback(senderId, postback) {
  const payload = postback.payload;
  
  switch (payload) {
    case 'GET_STARTED':
      await sendWelcomeMessage(senderId);
      break;
    case 'HELP':
      await sendHelpMessage(senderId);
      break;
    case 'EXAMPLES':
      await sendExampleQuestions(senderId);
      break;
    default:
      if (payload.startsWith('EXAMPLE_')) {
        const question = payload.replace('EXAMPLE_', '').replace(/_/g, ' ');
        await handleCustomGPTQuery(senderId, question);
      }
  }
}

// CustomGPT integration
async function handleCustomGPTQuery(senderId, query) {
  try {
    // Get or create session
    let sessionId = cache.get(`session_${senderId}`);
    
    if (!sessionId) {
      sessionId = await createCustomGPTConversation();
      if (sessionId) {
        cache.set(`session_${senderId}`, sessionId, 1800); // 30 minutes
      } else {
        await sendTextMessage(senderId, "❌ Couldn't start a conversation. Please try again.");
        return;
      }
    }
    
    // Send message to CustomGPT
    const response = await sendToCustomGPT(sessionId, query);
    
    if (response && response.openai_response) {
      let responseText = response.openai_response;
      
      // Split long messages
      const chunks = splitMessage(responseText);
      for (const chunk of chunks) {
        await sendTextMessage(senderId, chunk);
      }
      
      // Send citations if available
      if (response.citations && response.citations.length > 0) {
        await sendCitations(senderId, response.citations);
      }
    } else {
      await sendTextMessage(senderId, "❌ I couldn't get a response. Please try again.");
    }
    
  } catch (error) {
    console.error('CustomGPT error:', error);
    await sendTextMessage(senderId, "❌ An error occurred. Please try again.");
  }
}

// Create CustomGPT conversation
async function createCustomGPTConversation() {
  try {
    const response = await axios.post(
      `${config.CUSTOMGPT_API_URL}/projects/${config.CUSTOMGPT_AGENT_ID}/conversations`,
      { name: `FB Messenger Chat ${new Date().toISOString()}` },
      {
        headers: {
          'Authorization': `Bearer ${config.CUSTOMGPT_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    return response.data.data?.session_id;
  } catch (error) {
    console.error('Create conversation error:', error.response?.data || error);
    return null;
  }
}

// Send to CustomGPT
async function sendToCustomGPT(sessionId, message) {
  try {
    const response = await axios.post(
      `${config.CUSTOMGPT_API_URL}/projects/${config.CUSTOMGPT_AGENT_ID}/conversations/${sessionId}/messages`,
      {
        prompt: message,
        response_source: 'default'
      },
      {
        headers: {
          'Authorization': `Bearer ${config.CUSTOMGPT_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    return response.data.data;
  } catch (error) {
    console.error('Send to CustomGPT error:', error.response?.data || error);
    return null;
  }
}

// Send messages to Facebook
async function sendTextMessage(recipientId, text) {
  const messageData = {
    recipient: { id: recipientId },
    message: { text }
  };
  
  await callSendAPI(messageData);
}

// Send typing indicators
async function sendTypingOn(recipientId) {
  const messageData = {
    recipient: { id: recipientId },
    sender_action: 'typing_on'
  };
  
  await callSendAPI(messageData);
}

async function sendTypingOff(recipientId) {
  const messageData = {
    recipient: { id: recipientId },
    sender_action: 'typing_off'
  };
  
  await callSendAPI(messageData);
}

// Send welcome message
async function sendWelcomeMessage(senderId) {
  const message = `🤖 Welcome to CustomGPT Bot!

I'm here to help answer your questions using our knowledge base.

You can:
• Ask me anything
• Type 'help' for commands
• Type 'examples' for sample questions

How can I assist you today?`;
  
  await sendTextMessage(senderId, message);
  await sendQuickReplies(senderId);
}

// Send help message
async function sendHelpMessage(senderId) {
  const message = `📚 Available Commands:

• help - Show this help message
• reset - Start a new conversation
• examples - Show example questions
• stats - View your usage statistics

Just type your question to get started!`;
  
  await sendTextMessage(senderId, message);
}

// Send example questions
async function sendExampleQuestions(senderId) {
  const examples = [
    { title: "How do I get started?", payload: "EXAMPLE_How_do_I_get_started" },
    { title: "What features are available?", payload: "EXAMPLE_What_features_are_available" },
    { title: "How does it work?", payload: "EXAMPLE_How_does_it_work" }
  ];
  
  const messageData = {
    recipient: { id: senderId },
    message: {
      text: "Here are some example questions:",
      quick_replies: examples.map(ex => ({
        content_type: "text",
        title: ex.title,
        payload: ex.payload
      }))
    }
  };
  
  await callSendAPI(messageData);
}

// Send quick replies
async function sendQuickReplies(senderId) {
  const messageData = {
    recipient: { id: senderId },
    message: {
      text: "What would you like to do?",
      quick_replies: [
        {
          content_type: "text",
          title: "Ask a question",
          payload: "ASK_QUESTION"
        },
        {
          content_type: "text",
          title: "See examples",
          payload: "EXAMPLES"
        },
        {
          content_type: "text",
          title: "Help",
          payload: "HELP"
        }
      ]
    }
  };
  
  await callSendAPI(messageData);
}

// Send citations
async function sendCitations(senderId, citations) {
  let citationText = "📚 Sources:\n";
  
  citations.slice(0, 3).forEach((citation, index) => {
    if (typeof citation === 'object') {
      citationText += `${index + 1}. ${citation.title || citation.url || 'Source'}\n`;
    }
  });
  
  await sendTextMessage(senderId, citationText);
}

// Send usage stats
async function sendUsageStats(senderId) {
  const dailyUsage = dailyUsageMap.get(senderId) || 0;
  const remaining = config.DAILY_LIMIT - dailyUsage;
  
  const message = `📊 Your Usage Stats:

Today: ${dailyUsage} / ${config.DAILY_LIMIT}
Remaining: ${remaining}

Rate limit: ${config.RATE_LIMIT_REQUESTS} messages per minute`;
  
  await sendTextMessage(senderId, message);
}

// Reset conversation
async function resetConversation(senderId) {
  cache.del(`session_${senderId}`);
  await sendTextMessage(senderId, "✅ Conversation reset! Start fresh by asking me a question.");
}

// Call Facebook Send API
async function callSendAPI(messageData) {
  try {
    await axios.post(
      `https://graph.facebook.com/v18.0/me/messages`,
      messageData,
      {
        params: { access_token: config.FB_PAGE_ACCESS_TOKEN }
      }
    );
  } catch (error) {
    console.error('Send API error:', error.response?.data || error);
  }
}

// Rate limiting
function checkRateLimit(userId) {
  const now = Date.now();
  const userKey = `rate_${userId}`;
  const dailyKey = `daily_${userId}_${new Date().toDateString()}`;
  
  // Check minute rate limit
  const userRateData = rateLimitMap.get(userKey) || { count: 0, resetTime: now + config.RATE_LIMIT_WINDOW_MS };
  
  if (now > userRateData.resetTime) {
    userRateData.count = 1;
    userRateData.resetTime = now + config.RATE_LIMIT_WINDOW_MS;
  } else {
    userRateData.count++;
  }
  
  rateLimitMap.set(userKey, userRateData);
  
  // Check daily limit
  const dailyUsage = (dailyUsageMap.get(dailyKey) || 0) + 1;
  dailyUsageMap.set(dailyKey, dailyUsage);
  
  // Update daily usage for stats
  dailyUsageMap.set(userId, dailyUsage);
  
  // Clean up old entries
  if (rateLimitMap.size > 1000) {
    const cutoff = now - config.RATE_LIMIT_WINDOW_MS;
    for (const [key, data] of rateLimitMap.entries()) {
      if (data.resetTime < cutoff) {
        rateLimitMap.delete(key);
      }
    }
  }
  
  return userRateData.count <= config.RATE_LIMIT_REQUESTS && dailyUsage <= config.DAILY_LIMIT;
}

// Verify webhook signature
function verifyRequestSignature(req, res, buf) {
  const signature = req.headers['x-hub-signature-256'];
  
  if (!signature) {
    console.warn('No signature found');
    return;
  }
  
  const expectedSignature = crypto
    .createHmac('sha256', config.FB_APP_SECRET)
    .update(buf)
    .digest('hex');
  
  if (signature !== `sha256=${expectedSignature}`) {
    console.error('Invalid signature');
    throw new Error('Invalid signature');
  }
}

// Split long messages
function splitMessage(text, maxLength = 2000) {
  const chunks = [];
  let currentChunk = '';
  
  const sentences = text.split(/(?<=[.!?])\s+/);
  
  for (const sentence of sentences) {
    if (currentChunk.length + sentence.length > maxLength) {
      if (currentChunk) {
        chunks.push(currentChunk.trim());
        currentChunk = '';
      }
    }
    currentChunk += sentence + ' ';
  }
  
  if (currentChunk) {
    chunks.push(currentChunk.trim());
  }
  
  return chunks;
}

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start server
app.listen(config.PORT, () => {
  console.log(`Server running on port ${config.PORT}`);
});