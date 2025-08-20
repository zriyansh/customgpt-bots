// Google Apps Script WhatsApp Bot for CustomGPT (using Twilio)
// Deploy as Web App with "Anyone" access

// Configuration - Set these in Script Properties
const CONFIG = {
  CUSTOMGPT_API_KEY: PropertiesService.getScriptProperties().getProperty('CUSTOMGPT_API_KEY'),
  CUSTOMGPT_PROJECT_ID: PropertiesService.getScriptProperties().getProperty('CUSTOMGPT_PROJECT_ID'),
  CUSTOMGPT_API_URL: 'https://app.customgpt.ai',
  TWILIO_ACCOUNT_SID: PropertiesService.getScriptProperties().getProperty('TWILIO_ACCOUNT_SID'),
  TWILIO_AUTH_TOKEN: PropertiesService.getScriptProperties().getProperty('TWILIO_AUTH_TOKEN'),
  TWILIO_WHATSAPP_NUMBER: PropertiesService.getScriptProperties().getProperty('TWILIO_WHATSAPP_NUMBER'),
  WEBHOOK_URL: PropertiesService.getScriptProperties().getProperty('WEBHOOK_URL'),
  RATE_LIMIT_DAILY: 100,
  RATE_LIMIT_MINUTE: 5,
  ADMIN_NUMBERS: PropertiesService.getScriptProperties().getProperty('ADMIN_NUMBERS') || '',
  ENABLE_THINKING_MESSAGE: true  // Set to false to disable "Thinking..." message
};

// Main webhook handler for Twilio
function doPost(e) {
  try {
    // Parse Twilio webhook data
    const params = e.parameter;
    
    // Extract message details
    const from = params.From ? params.From.replace('whatsapp:', '') : '';
    const to = params.To;
    const body = params.Body || '';
    const messageSid = params.MessageSid;
    const numMedia = parseInt(params.NumMedia || '0');
    
    console.log('WhatsApp message received:', {
      from: from,
      body: body.substring(0, 50),
      hasMedia: numMedia > 0
    });
    
    // Process the message
    handleWhatsAppMessage(from, body, messageSid, numMedia);
    
    // Return TwiML response (empty to acknowledge)
    const twiml = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>';
    
    return ContentService.createTextOutput(twiml)
      .setMimeType(ContentService.MimeType.XML);
  } catch (error) {
    console.error('Error in doPost:', error);
    return ContentService.createTextOutput('Error')
      .setMimeType(ContentService.MimeType.TEXT);
  }
}

// Handle incoming WhatsApp messages
function handleWhatsAppMessage(fromNumber, messageText, messageSid, numMedia) {
  try {
    // Security check
    if (!isAllowedNumber(fromNumber)) {
      sendWhatsAppMessage(fromNumber, '❌ Sorry, you are not authorized to use this bot.');
      return;
    }
    
    // Rate limiting
    if (!checkRateLimit(fromNumber)) {
      sendWhatsAppMessage(fromNumber, '⏳ Rate limit exceeded. Please try again later.');
      return;
    }
    
    // Handle media messages
    if (numMedia > 0) {
      sendWhatsAppMessage(fromNumber, '📎 Media files are not supported yet. Please send text messages.');
      return;
    }
    
    // Handle commands
    if (messageText.startsWith('/')) {
      handleCommand(fromNumber, messageText);
    } else {
      // Regular message - send to CustomGPT
      handleCustomGPTQuery(fromNumber, messageText);
    }
    
  } catch (error) {
    console.error('Message handling error:', error);
    sendWhatsAppMessage(fromNumber, '❌ An error occurred. Please try again later.');
  }
}

// Handle bot commands
function handleCommand(phoneNumber, command) {
  const parts = command.split(' ');
  const cmd = parts[0].toLowerCase();
  const args = parts.slice(1).join(' ');
  
  switch (cmd) {
    case '/start':
      sendStartMessage(phoneNumber);
      break;
    case '/help':
      sendHelpMessage(phoneNumber);
      break;
    case '/examples':
      sendExamplesMessage(phoneNumber);
      break;
    case '/stats':
      sendStatsMessage(phoneNumber);
      break;
    case '/clear':
      clearSession(phoneNumber);
      break;
    case '/language':
      handleLanguageCommand(phoneNumber, args);
      break;
    default:
      sendWhatsAppMessage(phoneNumber, "Unknown command. Try /help");
  }
}

// Send start message
function sendStartMessage(phoneNumber) {
  const message = `🤖 Welcome to CustomGPT WhatsApp Bot!

I'm here to help you with your questions.

You can:
• Ask me questions directly
• Use /help to see commands
• Use /examples for sample questions

How can I assist you today?`;
  
  sendWhatsAppMessage(phoneNumber, message);
}

// Send help message
function sendHelpMessage(phoneNumber) {
  const message = `📚 *Available Commands:*

/start - Start a new conversation
/help - Show this help message
/examples - Show example questions
/stats - View your usage statistics
/language [code] - Change language
/clear - Clear conversation history

*Tips:*
• Just type your question naturally
• Your daily limit is ${CONFIG.RATE_LIMIT_DAILY} messages

Need help? Just ask!`;
  
  sendWhatsAppMessage(phoneNumber, message);
}

// Send examples message
function sendExamplesMessage(phoneNumber) {
  const message = `💡 *Example Questions:*

*General:*
• What can you help me with?
• How do I get started?

*Technical:*
• How do I use the API?
• Show me some examples

*Support:*
• I need help with a problem
• Where can I find documentation?

Just type any question to get started!`;
  
  sendWhatsAppMessage(phoneNumber, message);
}

// Handle CustomGPT API query
function handleCustomGPTQuery(phoneNumber, query) {
  const startTime = new Date().getTime();
  
  try {
    console.log('=== Starting CustomGPT Query ===');
    console.log('Phone:', phoneNumber);
    console.log('Query:', query);
    console.log('Query length:', query.length);
    
    // Send thinking message
    if (CONFIG.ENABLE_THINKING_MESSAGE) {
      console.log('Sending thinking message...');
      sendWhatsAppMessage(phoneNumber, '💭 Processing your request...');
    }
    
    // Get or create session
    let sessionId = getSession(phoneNumber);
    console.log('Current session:', sessionId);
    
    if (!sessionId) {
      console.log('Creating new conversation...');
      sessionId = createConversation();
      if (sessionId) {
        saveSession(phoneNumber, sessionId);
        console.log('New session created:', sessionId);
      } else {
        console.error('Failed to create conversation');
        sendWhatsAppMessage(phoneNumber, '❌ Sorry, I couldn\'t start a conversation. Please try again later.');
        return;
      }
    }
    
    // Send message to CustomGPT
    console.log('Sending to CustomGPT API...');
    const apiStartTime = new Date().getTime();
    const response = sendToCustomGPT(sessionId, query);
    const apiEndTime = new Date().getTime();
    console.log('API call took:', (apiEndTime - apiStartTime) / 1000, 'seconds');
    
    if (response && response.openai_response) {
      let responseText = response.openai_response;
      console.log('Got response, length:', responseText.length);
      console.log('Response preview:', responseText.substring(0, 100) + '...');
      
      // Add citations if available
      if (response.citations && response.citations.length > 0) {
        console.log('Adding citations:', response.citations.length);
        // Check if citations are IDs or objects
        if (typeof response.citations[0] === 'number' || typeof response.citations[0] === 'string') {
          // Citations are just IDs
          responseText += `\n\n📚 *Sources:* ${response.citations.length} references used`;
        } else {
          // Citations are objects with details
          responseText += '\n\n📚 *Sources:*\n';
          response.citations.slice(0, 3).forEach((citation, index) => {
            responseText += `${index + 1}. ${citation.title || citation.url || 'Source'}\n`;
          });
        }
      }
      
      // Check if response is too long for WhatsApp (max 1600 chars)
      if (responseText.length > 1600) {
        console.log('Response too long, truncating from', responseText.length, 'to 1500 chars');
        responseText = responseText.substring(0, 1500) + '...\n\n[Response truncated due to length]';
      }
      
      console.log('Sending final response to WhatsApp...');
      sendWhatsAppMessage(phoneNumber, responseText);
      
      const totalTime = new Date().getTime() - startTime;
      console.log('=== Request completed in', totalTime / 1000, 'seconds ===');
    } else {
      console.error('No response from CustomGPT API');
      console.error('Response object:', JSON.stringify(response));
      sendWhatsAppMessage(phoneNumber, '❌ I couldn\'t get a response. Please try again.');
    }
    
  } catch (error) {
    console.error('=== ERROR in handleCustomGPTQuery ===');
    console.error('Error type:', error.name);
    console.error('Error message:', error.message);
    console.error('Error stack:', error.stack);
    console.error('Query that failed:', query);
    
    const totalTime = new Date().getTime() - startTime;
    console.log('Failed after', totalTime / 1000, 'seconds');
    
    sendWhatsAppMessage(phoneNumber, '❌ An error occurred: ' + error.message);
  }
}

// Create a new conversation in CustomGPT
function createConversation() {
  const url = `${CONFIG.CUSTOMGPT_API_URL}/api/v1/projects/${CONFIG.CUSTOMGPT_PROJECT_ID}/conversations`;
  
  try {
    const response = UrlFetchApp.fetch(url, {
      method: 'post',
      headers: {
        'Authorization': `Bearer ${CONFIG.CUSTOMGPT_API_KEY}`,
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify({
        name: `WhatsApp Chat ${new Date().toISOString()}`
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
  const url = `${CONFIG.CUSTOMGPT_API_URL}/api/v1/projects/${CONFIG.CUSTOMGPT_PROJECT_ID}/conversations/${sessionId}/messages`;
  
  console.log('CustomGPT API Request:');
  console.log('URL:', url);
  console.log('Session ID:', sessionId);
  console.log('Message:', message.substring(0, 100) + (message.length > 100 ? '...' : ''));
  
  try {
    const payload = {
      prompt: message,
      response_source: 'default'
    };
    
    const options = {
      method: 'post',
      headers: {
        'Authorization': `Bearer ${CONFIG.CUSTOMGPT_API_KEY}`,
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };
    
    console.log('Sending request to CustomGPT...');
    const response = UrlFetchApp.fetch(url, options);
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    console.log('Response code:', responseCode);
    console.log('Response length:', responseText.length);
    
    if (responseCode === 200) {
      const data = JSON.parse(responseText);
      console.log('Response structure:', Object.keys(data));
      if (data.data) {
        console.log('Response data keys:', Object.keys(data.data));
        console.log('Has openai_response:', !!data.data.openai_response);
        console.log('Response length:', data.data.openai_response ? data.data.openai_response.length : 0);
      }
      return data.data;
    } else {
      console.error('CustomGPT API error - Status:', responseCode);
      console.error('Error response:', responseText.substring(0, 500));
      return null;
    }
  } catch (error) {
    console.error('Send to CustomGPT exception:', error.message);
    console.error('Error stack:', error.stack);
    return null;
  }
}

// Send WhatsApp message via Twilio
function sendWhatsAppMessage(to, message) {
  // Check if 'to' parameter is provided
  if (!to) {
    console.error('sendWhatsAppMessage: Missing recipient phone number');
    return;
  }
  
  const twilioUrl = `https://api.twilio.com/2010-04-01/Accounts/${CONFIG.TWILIO_ACCOUNT_SID}/Messages.json`;
  
  // Ensure phone number has whatsapp: prefix
  if (!to.startsWith('whatsapp:')) {
    to = `whatsapp:${to}`;
  }
  
  const options = {
    method: 'post',
    headers: {
      'Authorization': 'Basic ' + Utilities.base64Encode(`${CONFIG.TWILIO_ACCOUNT_SID}:${CONFIG.TWILIO_AUTH_TOKEN}`),
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    payload: `To=${encodeURIComponent(to)}&From=${encodeURIComponent(CONFIG.TWILIO_WHATSAPP_NUMBER)}&Body=${encodeURIComponent(message)}`,
    muteHttpExceptions: true
  };
  
  try {
    const response = UrlFetchApp.fetch(twilioUrl, options);
    const responseCode = response.getResponseCode();
    console.log('Message sent:', responseCode);
    
    // Log error details for debugging
    if (responseCode !== 201) {
      const responseText = response.getContentText();
      console.error('Twilio error response:', responseText);
    }
  } catch (error) {
    console.error('Twilio send error:', error);
  }
}

// Session management using Script Properties
function getSession(phoneNumber) {
  const cache = CacheService.getScriptCache();
  return cache.get(`session_${phoneNumber}`);
}

function saveSession(phoneNumber, sessionId) {
  const cache = CacheService.getScriptCache();
  cache.put(`session_${phoneNumber}`, sessionId, 1800); // 30 minutes
}

function clearSession(phoneNumber) {
  const cache = CacheService.getScriptCache();
  cache.remove(`session_${phoneNumber}`);
  sendWhatsAppMessage(phoneNumber, '✅ Conversation cleared! Start fresh by sending me a message.');
}

// Rate limiting using cache
function checkRateLimit(phoneNumber) {
  const cache = CacheService.getScriptCache();
  const now = new Date();
  
  // Get daily count
  const dailyKey = `daily_${phoneNumber}_${now.toDateString()}`;
  let dailyCount = parseInt(cache.get(dailyKey) || '0');
  
  // Get minute count
  const minuteKey = `minute_${phoneNumber}_${Math.floor(now.getTime() / 60000)}`;
  let minuteCount = parseInt(cache.get(minuteKey) || '0');
  
  if (dailyCount >= CONFIG.RATE_LIMIT_DAILY || minuteCount >= CONFIG.RATE_LIMIT_MINUTE) {
    return false;
  }
  
  // Increment counters
  cache.put(dailyKey, (dailyCount + 1).toString(), 86400); // 24 hours
  cache.put(minuteKey, (minuteCount + 1).toString(), 60); // 1 minute
  
  return true;
}

// Get user stats
function sendStatsMessage(phoneNumber) {
  const cache = CacheService.getScriptCache();
  const now = new Date();
  
  const dailyKey = `daily_${phoneNumber}_${now.toDateString()}`;
  const dailyCount = parseInt(cache.get(dailyKey) || '0');
  
  const message = `📊 *Your Usage Statistics*

Today's Usage: ${dailyCount} / ${CONFIG.RATE_LIMIT_DAILY}
Remaining Today: ${CONFIG.RATE_LIMIT_DAILY - dailyCount}

Keep in mind:
• Daily limit resets at midnight
• Rate limit: ${CONFIG.RATE_LIMIT_MINUTE} messages per minute`;
  
  sendWhatsAppMessage(phoneNumber, message);
}

// Language handling
function handleLanguageCommand(phoneNumber, language) {
  if (!language) {
    sendWhatsAppMessage(phoneNumber, '🌍 Please specify a language code. Example: /language es');
    return;
  }
  
  // Save language preference
  const cache = CacheService.getScriptCache();
  cache.put(`lang_${phoneNumber}`, language, 86400 * 30); // 30 days
  
  sendWhatsAppMessage(phoneNumber, `✅ Language changed to: ${language}`);
}

// Security check
function isAllowedNumber(phoneNumber) {
  // If no restrictions, allow all
  const adminNumbers = CONFIG.ADMIN_NUMBERS.split(',').map(n => n.trim());
  
  // For demo, allow all numbers. In production, implement whitelist
  return true;
}

// Setup webhook (run once)
function setupWebhook() {
  const webhookUrl = CONFIG.WEBHOOK_URL;
  if (!webhookUrl) {
    throw new Error('WEBHOOK_URL not set in Script Properties');
  }
  
  console.log('Webhook URL:', webhookUrl);
  console.log('Configure this URL in your Twilio WhatsApp sandbox settings');
}

// Test function
function test() {
  console.log('Config:', CONFIG);
  
  // IMPORTANT: Replace with your actual WhatsApp number that has joined the Twilio sandbox
  const testPhoneNumber = 'whatsapp:+1234567890'; // Replace with your number!
  
  console.log('Testing message send to:', testPhoneNumber);
  console.log('Make sure you have joined the Twilio sandbox first!');
  
  // Test message sending
  sendWhatsAppMessage(testPhoneNumber, 'Test message from Google Apps Script');
}

// Test specific functions
function testExamples() {
  // Replace with your actual WhatsApp number
  const phoneNumber = '+1234567890'; // No 'whatsapp:' prefix here
  sendExamplesMessage(phoneNumber);
}

function testHelp() {
  // Replace with your actual WhatsApp number
  const phoneNumber = '+1234567890'; // No 'whatsapp:' prefix here
  sendHelpMessage(phoneNumber);
}

function testStart() {
  // Replace with your actual WhatsApp number
  const phoneNumber = '+1234567890'; // No 'whatsapp:' prefix here
  sendStartMessage(phoneNumber);
}