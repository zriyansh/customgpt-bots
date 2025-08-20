// Google Apps Script Facebook Messenger Bot for CustomGPT
// Deploy as Web App with "Anyone" access

// Configuration - Set these in Script Properties
const CONFIG = {
  // Facebook
  FB_VERIFY_TOKEN: PropertiesService.getScriptProperties().getProperty('FB_VERIFY_TOKEN'),
  FB_PAGE_ACCESS_TOKEN: PropertiesService.getScriptProperties().getProperty('FB_PAGE_ACCESS_TOKEN'),
  FB_APP_SECRET: PropertiesService.getScriptProperties().getProperty('FB_APP_SECRET'),
  
  // CustomGPT
  CUSTOMGPT_API_KEY: PropertiesService.getScriptProperties().getProperty('CUSTOMGPT_API_KEY'),
  CUSTOMGPT_PROJECT_ID: PropertiesService.getScriptProperties().getProperty('CUSTOMGPT_PROJECT_ID'),
  CUSTOMGPT_API_URL: 'https://app.customgpt.ai/api/v1',
  
  // Rate Limiting
  RATE_LIMIT_MINUTE: 5,
  RATE_LIMIT_DAILY: 100,
  
  // Admin Settings
  ADMIN_PSIDS: PropertiesService.getScriptProperties().getProperty('ADMIN_PSIDS') || ''
};

// Webhook verification (GET request)
function doGet(e) {
  const mode = e.parameter['hub.mode'];
  const token = e.parameter['hub.verify_token'];
  const challenge = e.parameter['hub.challenge'];
  
  if (mode && token) {
    if (mode === 'subscribe' && token === CONFIG.FB_VERIFY_TOKEN) {
      console.log('WEBHOOK_VERIFIED');
      return ContentService.createTextOutput(challenge);
    }
  }
  
  return ContentService.createTextOutput('Forbidden').setMimeType(ContentService.MimeType.TEXT);
}

// Handle webhook events (POST request)
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    
    // Verify webhook signature
    if (!verifyWebhookSignature(e)) {
      console.error('Invalid signature');
      return ContentService.createTextOutput('Unauthorized');
    }
    
    // Process Facebook webhook
    if (data.object === 'page') {
      data.entry.forEach(entry => {
        entry.messaging.forEach(event => {
          console.log('Webhook event:', event);
          
          if (event.message && !event.message.is_echo) {
            handleMessage(event.sender.id, event.message);
          } else if (event.postback) {
            handlePostback(event.sender.id, event.postback);
          }
        });
      });
    }
    
    return ContentService.createTextOutput('EVENT_RECEIVED');
  } catch (error) {
    console.error('Error in doPost:', error);
    return ContentService.createTextOutput('Error');
  }
}

// Verify webhook signature
function verifyWebhookSignature(e) {
  const signature = e.parameter['X-Hub-Signature-256'] || e.headers['x-hub-signature-256'];
  
  if (!signature || !CONFIG.FB_APP_SECRET) {
    return true; // Skip verification if not configured
  }
  
  const payload = e.postData.contents;
  const expectedSignature = 'sha256=' + Utilities.computeHmacSha256Signature(payload, CONFIG.FB_APP_SECRET)
    .map(byte => ('0' + (byte & 0xFF).toString(16)).slice(-2))
    .join('');
  
  return signature === expectedSignature;
}

// Handle incoming messages
function handleMessage(senderId, message) {
  try {
    // Check rate limits
    if (!checkRateLimit(senderId)) {
      sendTextMessage(senderId, "⏳ You've reached the rate limit. Please try again later.");
      return;
    }
    
    // Send typing indicator
    sendTypingOn(senderId);
    
    if (message.text) {
      const text = message.text.toLowerCase().trim();
      
      // Handle commands
      switch (text) {
        case 'help':
        case '/help':
          sendHelpMessage(senderId);
          break;
          
        case 'reset':
        case '/reset':
          resetConversation(senderId);
          break;
          
        case 'examples':
        case '/examples':
          sendExampleQuestions(senderId);
          break;
          
        case 'stats':
        case '/stats':
          sendUsageStats(senderId);
          break;
          
        case 'about':
        case '/about':
          sendAboutMessage(senderId);
          break;
          
        default:
          // Send to CustomGPT
          handleCustomGPTQuery(senderId, message.text);
      }
    } else if (message.attachments) {
      sendTextMessage(senderId, "📎 I can only process text messages at the moment.");
    }
    
    // Send typing off
    sendTypingOff(senderId);
    
  } catch (error) {
    console.error('Error handling message:', error);
    sendTextMessage(senderId, "❌ Sorry, something went wrong. Please try again.");
  }
}

// Handle postback events
function handlePostback(senderId, postback) {
  const payload = postback.payload;
  
  switch (payload) {
    case 'GET_STARTED':
      sendWelcomeMessage(senderId);
      break;
      
    case 'HELP':
      sendHelpMessage(senderId);
      break;
      
    case 'EXAMPLES':
      sendExampleQuestions(senderId);
      break;
      
    case 'STATS':
      sendUsageStats(senderId);
      break;
      
    case 'RESET':
      resetConversation(senderId);
      break;
      
    default:
      if (payload.startsWith('EXAMPLE_')) {
        const question = payload.replace('EXAMPLE_', '').replace(/_/g, ' ');
        handleCustomGPTQuery(senderId, question);
      }
  }
}

// Handle CustomGPT queries
function handleCustomGPTQuery(senderId, query) {
  try {
    // Get or create session
    const cache = CacheService.getScriptCache();
    let sessionId = cache.get(`session_${senderId}`);
    
    if (!sessionId) {
      sessionId = createCustomGPTConversation();
      if (sessionId) {
        cache.put(`session_${senderId}`, sessionId, 1800); // 30 minutes
      } else {
        sendTextMessage(senderId, "❌ Couldn't start a conversation. Please try again.");
        return;
      }
    }
    
    // Send message to CustomGPT
    const response = sendToCustomGPT(sessionId, query);
    
    if (response && response.openai_response) {
      // Send response
      sendTextMessage(senderId, response.openai_response);
      
      // Send citations if available
      if (response.citations && response.citations.length > 0) {
        sendCitations(senderId, response.citations);
      }
    } else {
      sendTextMessage(senderId, "❌ I couldn't get a response. Please try again.");
    }
    
  } catch (error) {
    console.error('CustomGPT error:', error);
    sendTextMessage(senderId, "❌ An error occurred. Please try again.");
  }
}

// Create CustomGPT conversation
function createCustomGPTConversation() {
  const url = `${CONFIG.CUSTOMGPT_API_URL}/projects/${CONFIG.CUSTOMGPT_PROJECT_ID}/conversations`;
  
  try {
    const response = UrlFetchApp.fetch(url, {
      method: 'post',
      headers: {
        'Authorization': `Bearer ${CONFIG.CUSTOMGPT_API_KEY}`,
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify({
        name: `FB Messenger Chat ${new Date().toISOString()}`
      })
    });
    
    if (response.getResponseCode() === 200 || response.getResponseCode() === 201) {
      const data = JSON.parse(response.getContentText());
      return data.data?.session_id;
    }
  } catch (error) {
    console.error('Create conversation error:', error);
  }
  return null;
}

// Send message to CustomGPT
function sendToCustomGPT(sessionId, message) {
  const url = `${CONFIG.CUSTOMGPT_API_URL}/projects/${CONFIG.CUSTOMGPT_PROJECT_ID}/conversations/${sessionId}/messages`;
  
  try {
    const response = UrlFetchApp.fetch(url, {
      method: 'post',
      headers: {
        'Authorization': `Bearer ${CONFIG.CUSTOMGPT_API_KEY}`,
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify({
        prompt: message,
        response_source: 'default'
      }),
      muteHttpExceptions: true
    });
    
    if (response.getResponseCode() === 200) {
      const data = JSON.parse(response.getContentText());
      return data.data;
    }
  } catch (error) {
    console.error('Send to CustomGPT error:', error);
  }
  return null;
}

// Send text message via Facebook
function sendTextMessage(recipientId, text) {
  // Split long messages
  const chunks = splitMessage(text);
  
  chunks.forEach(chunk => {
    const messageData = {
      recipient: { id: recipientId },
      message: { text: chunk }
    };
    
    callSendAPI(messageData);
  });
}

// Send typing indicators
function sendTypingOn(recipientId) {
  const messageData = {
    recipient: { id: recipientId },
    sender_action: 'typing_on'
  };
  
  callSendAPI(messageData);
}

function sendTypingOff(recipientId) {
  const messageData = {
    recipient: { id: recipientId },
    sender_action: 'typing_off'
  };
  
  callSendAPI(messageData);
}

// Send welcome message
function sendWelcomeMessage(senderId) {
  const message = `🤖 Welcome to CustomGPT Bot!

I'm here to help answer your questions using our knowledge base.

You can:
• Ask me anything
• Type 'help' for commands
• Type 'examples' for sample questions

How can I assist you today?`;
  
  sendTextMessage(senderId, message);
  sendQuickReplies(senderId);
}

// Send help message
function sendHelpMessage(senderId) {
  const message = `📚 Available Commands:

• help - Show this help message
• reset - Start a new conversation
• examples - Show example questions
• stats - View your usage statistics
• about - Learn about this bot

Just type your question to get started!`;
  
  sendTextMessage(senderId, message);
}

// Send example questions
function sendExampleQuestions(senderId) {
  const messageData = {
    recipient: { id: senderId },
    message: {
      text: "Here are some example questions:",
      quick_replies: [
        {
          content_type: "text",
          title: "How do I get started?",
          payload: "EXAMPLE_How_do_I_get_started"
        },
        {
          content_type: "text",
          title: "What features are available?",
          payload: "EXAMPLE_What_features_are_available"
        },
        {
          content_type: "text",
          title: "How does it work?",
          payload: "EXAMPLE_How_does_it_work"
        },
        {
          content_type: "text",
          title: "Show pricing",
          payload: "EXAMPLE_What_are_the_pricing_options"
        }
      ]
    }
  };
  
  callSendAPI(messageData);
}

// Send quick replies
function sendQuickReplies(senderId) {
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
  
  callSendAPI(messageData);
}

// Send citations
function sendCitations(senderId, citations) {
  let citationText = "📚 Sources:\n";
  
  citations.slice(0, 3).forEach((citation, index) => {
    if (typeof citation === 'object') {
      citationText += `${index + 1}. ${citation.title || citation.url || 'Source'}\n`;
    }
  });
  
  sendTextMessage(senderId, citationText);
}

// Send usage stats
function sendUsageStats(senderId) {
  const cache = CacheService.getScriptCache();
  const now = new Date();
  
  const dailyKey = `daily_${senderId}_${now.toDateString()}`;
  const dailyCount = parseInt(cache.get(dailyKey) || '0');
  
  const message = `📊 Your Usage Stats:

Today: ${dailyCount} / ${CONFIG.RATE_LIMIT_DAILY}
Remaining: ${CONFIG.RATE_LIMIT_DAILY - dailyCount}

Rate limit: ${CONFIG.RATE_LIMIT_MINUTE} messages per minute`;
  
  sendTextMessage(senderId, message);
}

// Send about message
function sendAboutMessage(senderId) {
  const message = `ℹ️ About This Bot:

I'm an AI assistant powered by CustomGPT's RAG technology. I can answer questions based on our curated knowledge base.

Features:
• Intelligent responses
• Source citations
• Rate limiting
• Conversation context

Built with CustomGPT API`;
  
  sendTextMessage(senderId, message);
}

// Reset conversation
function resetConversation(senderId) {
  const cache = CacheService.getScriptCache();
  cache.remove(`session_${senderId}`);
  sendTextMessage(senderId, "✅ Conversation reset! Start fresh by asking me a question.");
}

// Call Facebook Send API
function callSendAPI(messageData) {
  const url = 'https://graph.facebook.com/v18.0/me/messages';
  
  try {
    UrlFetchApp.fetch(url, {
      method: 'post',
      headers: {
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify(messageData),
      muteHttpExceptions: true,
      params: {
        access_token: CONFIG.FB_PAGE_ACCESS_TOKEN
      }
    });
  } catch (error) {
    console.error('Send API error:', error);
  }
}

// Rate limiting
function checkRateLimit(userId) {
  const cache = CacheService.getScriptCache();
  const now = new Date();
  
  // Check minute rate limit
  const minuteKey = `minute_${userId}_${Math.floor(now.getTime() / 60000)}`;
  let minuteCount = parseInt(cache.get(minuteKey) || '0');
  
  // Check daily limit
  const dailyKey = `daily_${userId}_${now.toDateString()}`;
  let dailyCount = parseInt(cache.get(dailyKey) || '0');
  
  if (minuteCount >= CONFIG.RATE_LIMIT_MINUTE || dailyCount >= CONFIG.RATE_LIMIT_DAILY) {
    return false;
  }
  
  // Increment counters
  cache.put(minuteKey, (minuteCount + 1).toString(), 60);
  cache.put(dailyKey, (dailyCount + 1).toString(), 86400);
  
  return true;
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
  
  return chunks.length > 0 ? chunks : [text];
}

// Setup functions (run once)
function setupWebhook() {
  const webhookUrl = ScriptApp.getService().getUrl();
  console.log('Your webhook URL:', webhookUrl);
  console.log('Use this URL in Facebook App Dashboard');
}

function testBot() {
  // Test sending a message
  sendTextMessage('TEST_USER_ID', 'Test message from Google Apps Script');
}