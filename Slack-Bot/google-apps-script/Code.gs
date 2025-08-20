/**
 * CustomGPT Slack Bot for Google Apps Script
 * Clean version with proper event handling
 */

// Configuration - Set these in Script Properties
const CONFIG = {
  SLACK_BOT_TOKEN: PropertiesService.getScriptProperties().getProperty('SLACK_BOT_TOKEN'),
  SLACK_SIGNING_SECRET: PropertiesService.getScriptProperties().getProperty('SLACK_SIGNING_SECRET'),
  CUSTOMGPT_API_KEY: PropertiesService.getScriptProperties().getProperty('CUSTOMGPT_API_KEY'),
  CUSTOMGPT_PROJECT_ID: PropertiesService.getScriptProperties().getProperty('CUSTOMGPT_PROJECT_ID'),
  CUSTOMGPT_API_BASE_URL: 'https://app.customgpt.ai/api/v1',
  RATE_LIMIT_PER_USER: 20,
  RATE_LIMIT_PER_CHANNEL: 100,
  SHOW_CITATIONS: false  // Disabled to avoid broken source links
};

// Cache service
const cache = CacheService.getScriptCache();

/**
 * Main entry point
 */
function doPost(e) {
  try {
    // Parse request
    let payload;
    try {
      payload = JSON.parse(e.postData.contents);
    } catch (error) {
      // Handle slash commands
      if (e.parameter && e.parameter.command) {
        return handleSlashCommand(e.parameter);
      }
      return ContentService.createTextOutput('OK').setMimeType(ContentService.MimeType.TEXT);
    }
    
    // URL verification
    if (payload.type === 'url_verification') {
      return ContentService.createTextOutput(payload.challenge).setMimeType(ContentService.MimeType.TEXT);
    }
    
    // Process event only once
    if (payload.event_id) {
      const eventKey = `event_${payload.event_id}`;
      if (cache.get(eventKey)) {
        return ContentService.createTextOutput('OK').setMimeType(ContentService.MimeType.TEXT);
      }
      cache.put(eventKey, '1', 300);
    }
    
    // Handle events
    if (payload.event && payload.event.type) {
      const event = payload.event;
      
      // Skip bot messages entirely
      if (event.bot_id || event.subtype === 'bot_message' || !event.user) {
        return ContentService.createTextOutput('OK').setMimeType(ContentService.MimeType.TEXT);
      }
      
      // Handle user messages
      if (event.type === 'app_mention' || (event.type === 'message' && event.channel_type === 'im')) {
        // Additional deduplication by message timestamp
        const msgKey = `msg_${event.channel}_${event.ts}`;
        if (cache.get(msgKey)) {
          return ContentService.createTextOutput('OK').setMimeType(ContentService.MimeType.TEXT);
        }
        cache.put(msgKey, '1', 300);
        
        // Process the message
        processUserMessage(event);
      }
    }
    
    return ContentService.createTextOutput('OK').setMimeType(ContentService.MimeType.TEXT);
    
  } catch (error) {
    console.error('Error:', error);
    return ContentService.createTextOutput('OK').setMimeType(ContentService.MimeType.TEXT);
  }
}

/**
 * Process user messages
 */
function processUserMessage(event) {
  const userId = event.user;
  const channelId = event.channel;
  const text = (event.text || '').replace(/<@[A-Z0-9]+>/g, '').trim();
  const threadTs = event.thread_ts || event.ts;
  
  // Rate limiting
  const rateKey = `rate_${userId}`;
  const count = parseInt(cache.get(rateKey) || '0');
  if (count >= CONFIG.RATE_LIMIT_PER_USER) {
    sendMessage(channelId, "You've reached the rate limit. Please wait a moment.", threadTs);
    return;
  }
  cache.put(rateKey, String(count + 1), 60);
  
  // Empty message - show help
  if (!text) {
    showStarterQuestions(channelId, threadTs);
    return;
  }
  
  // Get conversation
  const convKey = `conv_${userId}_${channelId}_${threadTs || 'main'}`;
  let conversationId = cache.get(convKey);
  
  if (!conversationId) {
    conversationId = createConversation(channelId);
    if (conversationId) {
      cache.put(convKey, conversationId, 21600); // 6 hours
    }
  }
  
  // Send query to CustomGPT
  queryCustomGPT(text, conversationId, channelId, threadTs);
}

/**
 * Create conversation
 */
function createConversation(channelId) {
  try {
    const agentId = cache.get(`agent_${channelId}`) || CONFIG.CUSTOMGPT_PROJECT_ID;
    
    const response = UrlFetchApp.fetch(
      `${CONFIG.CUSTOMGPT_API_BASE_URL}/projects/${agentId}/conversations`,
      {
        method: 'post',
        headers: {
          'Authorization': `Bearer ${CONFIG.CUSTOMGPT_API_KEY}`,
          'Content-Type': 'application/json'
        },
        muteHttpExceptions: true
      }
    );
    
    if (response.getResponseCode() === 201) {
      const data = JSON.parse(response.getContentText());
      return data.data.session_id;
    }
  } catch (error) {
    console.error('Error creating conversation:', error);
  }
  
  return Utilities.getUuid();
}

/**
 * Query CustomGPT
 */
function queryCustomGPT(query, conversationId, channelId, threadTs) {
  // Send thinking message
  const thinkingMsg = sendMessage(channelId, "Thinking...", threadTs);
  let thinkingTs = threadTs;
  
  try {
    const msgData = JSON.parse(thinkingMsg);
    if (msgData.ok && msgData.ts) {
      thinkingTs = msgData.ts;
    }
  } catch (e) {
    // Use threadTs
  }
  
  try {
    const agentId = cache.get(`agent_${channelId}`) || CONFIG.CUSTOMGPT_PROJECT_ID;
    
    const response = UrlFetchApp.fetch(
      `${CONFIG.CUSTOMGPT_API_BASE_URL}/projects/${agentId}/conversations/${conversationId}/messages`,
      {
        method: 'post',
        headers: {
          'Authorization': `Bearer ${CONFIG.CUSTOMGPT_API_KEY}`,
          'Content-Type': 'application/json'
        },
        payload: JSON.stringify({
          prompt: query,
          response_source: 'default',
          stream: false,
          lang: 'en'
        }),
        muteHttpExceptions: true
      }
    );
    
    let responseText = '';
    
    if (response.getResponseCode() === 200) {
      const data = JSON.parse(response.getContentText());
      responseText = data.data.openai_response || data.data.response || 'No response received.';
    } else if (response.getResponseCode() === 429) {
      responseText = "I'm a bit busy right now. Please try again in a moment.";
    } else {
      responseText = "Sorry, I encountered an error. Please try again later.";
    }
    
    // Update thinking message
    if (thinkingTs !== threadTs) {
      updateMessage(channelId, responseText, thinkingTs);
    } else {
      sendMessage(channelId, responseText, threadTs);
    }
    
  } catch (error) {
    console.error('Error:', error);
    sendMessage(channelId, "Sorry, I encountered an error.", threadTs);
  }
}

/**
 * Show starter questions
 */
function showStarterQuestions(channelId, threadTs) {
  const questions = [
    "What can you help me with?",
    "Tell me about your main features",
    "How do I get started?"
  ];
  
  let text = "*Here are some questions you can ask me:*\n\n";
  questions.forEach(q => {
    text += `• ${q}\n`;
  });
  text += "\nJust type your question and I'll help!";
  
  sendMessage(channelId, text, threadTs);
}

/**
 * Handle slash commands
 */
function handleSlashCommand(params) {
  const command = params.command;
  const text = params.text || '';
  const userId = params.user_id;
  const channelId = params.channel_id;
  
  switch (command) {
    case '/customgpt':
    case '/ask':
      if (!text) {
        return ContentService.createTextOutput(
          'Please provide a question. Usage: `/customgpt [your question]`'
        ).setMimeType(ContentService.MimeType.TEXT);
      }
      
      // Post question and process
      sendMessage(channelId, `<@${userId}> asked: ${text}`);
      
      const event = {
        user: userId,
        channel: channelId,
        text: text,
        ts: new Date().getTime() / 1000
      };
      
      processUserMessage(event);
      
      return ContentService.createTextOutput('').setMimeType(ContentService.MimeType.TEXT);
      
    case '/customgpt-agent':
      if (!text) {
        const currentAgent = cache.get(`agent_${channelId}`) || CONFIG.CUSTOMGPT_PROJECT_ID;
        return ContentService.createTextOutput(
          `Current agent ID: \`${currentAgent}\`\nTo change: \`/customgpt-agent [agent_id]\``
        ).setMimeType(ContentService.MimeType.TEXT);
      }
      
      if (!/^\d+$/.test(text)) {
        return ContentService.createTextOutput(
          'Invalid agent ID. Agent IDs must be numeric.'
        ).setMimeType(ContentService.MimeType.TEXT);
      }
      
      cache.put(`agent_${channelId}`, text, 86400);
      return ContentService.createTextOutput(
        `✅ Agent ID set to \`${text}\` for this channel.`
      ).setMimeType(ContentService.MimeType.TEXT);
      
    case '/customgpt-help':
      return ContentService.createTextOutput(
        `*CustomGPT Bot Help*\n\n` +
        `*Usage:*\n` +
        `• Direct message me\n` +
        `• Mention me: @CustomGPT\n` +
        `• Slash command: /customgpt [question]\n\n` +
        `*Commands:*\n` +
        `• \`/customgpt [question]\` - Ask a question\n` +
        `• \`/customgpt-agent [id]\` - Switch agent\n` +
        `• \`/customgpt-help\` - Show this help`
      ).setMimeType(ContentService.MimeType.TEXT);
      
    default:
      return ContentService.createTextOutput('Unknown command').setMimeType(ContentService.MimeType.TEXT);
  }
}

/**
 * Send message to Slack
 */
function sendMessage(channel, text, threadTs) {
  const payload = {
    channel: channel,
    text: text
  };
  
  if (threadTs) {
    payload.thread_ts = threadTs;
  }
  
  try {
    const response = UrlFetchApp.fetch('https://slack.com/api/chat.postMessage', {
      method: 'post',
      headers: {
        'Authorization': `Bearer ${CONFIG.SLACK_BOT_TOKEN}`,
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });
    
    return response.getContentText();
  } catch (error) {
    console.error('Error sending message:', error);
    return null;
  }
}

/**
 * Update message
 */
function updateMessage(channel, text, ts) {
  try {
    UrlFetchApp.fetch('https://slack.com/api/chat.update', {
      method: 'post',
      headers: {
        'Authorization': `Bearer ${CONFIG.SLACK_BOT_TOKEN}`,
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify({
        channel: channel,
        ts: ts,
        text: text
      }),
      muteHttpExceptions: true
    });
  } catch (error) {
    console.error('Error updating message:', error);
  }
}

/**
 * Test configuration
 */
function testConfig() {
  console.log('Config:', {
    hasToken: !!CONFIG.SLACK_BOT_TOKEN,
    hasSecret: !!CONFIG.SLACK_SIGNING_SECRET,
    hasApiKey: !!CONFIG.CUSTOMGPT_API_KEY,
    hasProjectId: !!CONFIG.CUSTOMGPT_PROJECT_ID,
    projectId: CONFIG.CUSTOMGPT_PROJECT_ID
  });
}