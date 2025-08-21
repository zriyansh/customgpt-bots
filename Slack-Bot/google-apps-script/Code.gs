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
  SHOW_CITATIONS: false,  // Disabled to avoid broken source links
  // Thread follow-up configuration
  THREAD_FOLLOW_UP_ENABLED: PropertiesService.getScriptProperties().getProperty('THREAD_FOLLOW_UP_ENABLED') !== 'false',
  THREAD_FOLLOW_UP_TIMEOUT: parseInt(PropertiesService.getScriptProperties().getProperty('THREAD_FOLLOW_UP_TIMEOUT') || '3600'),
  THREAD_FOLLOW_UP_MAX_MESSAGES: parseInt(PropertiesService.getScriptProperties().getProperty('THREAD_FOLLOW_UP_MAX_MESSAGES') || '50'),
  IGNORE_BOT_MESSAGES: PropertiesService.getScriptProperties().getProperty('IGNORE_BOT_MESSAGES') !== 'false'
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
        processUserMessage(event, true); // isDirectMention = true
      }
      // Handle thread follow-ups (when enabled)
      else if (CONFIG.THREAD_FOLLOW_UP_ENABLED && event.type === 'message' && event.thread_ts && event.thread_ts !== event.ts) {
        // Skip thread broadcast messages
        if (event.subtype === 'thread_broadcast') {
          return ContentService.createTextOutput('OK').setMimeType(ContentService.MimeType.TEXT);
        }
        
        // Check if bot should respond to this thread
        if (shouldRespondToThread(event.channel, event.thread_ts)) {
          // Additional deduplication
          const msgKey = `msg_${event.channel}_${event.ts}`;
          if (cache.get(msgKey)) {
            return ContentService.createTextOutput('OK').setMimeType(ContentService.MimeType.TEXT);
          }
          cache.put(msgKey, '1', 300);
          
          // Update thread activity
          updateThreadActivity(event.channel, event.thread_ts);
          
          // Process the message
          processUserMessage(event, false); // isDirectMention = false
        }
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
function processUserMessage(event, isDirectMention) {
  const userId = event.user;
  const channelId = event.channel;
  const text = (event.text || '').replace(/<@[A-Z0-9]+>/g, '').trim();
  const threadTs = event.thread_ts || event.ts;
  
  // Mark thread participation if this is a direct mention
  if (isDirectMention && threadTs && CONFIG.THREAD_FOLLOW_UP_ENABLED) {
    markThreadParticipation(channelId, threadTs);
  }
  
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
      
      processUserMessage(event, true);
      
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
        `• Slash command: /customgpt [question]\n` +
        `• Thread follow-ups: Continue conversation without mentions\n\n` +
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
 * Thread participation tracking functions
 */

/**
 * Mark that bot has participated in a thread
 */
function markThreadParticipation(channelId, threadTs) {
  if (!CONFIG.THREAD_FOLLOW_UP_ENABLED || !threadTs) {
    return;
  }
  
  const threadKey = `thread_${channelId}_${threadTs}`;
  const threadData = {
    firstParticipation: new Date().getTime(),
    lastActivity: new Date().getTime(),
    messageCount: 1
  };
  
  // Store thread participation info (cache expires after timeout)
  cache.put(threadKey, JSON.stringify(threadData), CONFIG.THREAD_FOLLOW_UP_TIMEOUT);
  
  // Also store a simple flag for quick checks
  cache.put(`thread_active_${channelId}_${threadTs}`, '1', CONFIG.THREAD_FOLLOW_UP_TIMEOUT);
}

/**
 * Update thread activity
 */
function updateThreadActivity(channelId, threadTs) {
  const threadKey = `thread_${channelId}_${threadTs}`;
  const threadDataStr = cache.get(threadKey);
  
  if (threadDataStr) {
    try {
      const threadData = JSON.parse(threadDataStr);
      threadData.lastActivity = new Date().getTime();
      threadData.messageCount = (threadData.messageCount || 0) + 1;
      
      // Check message limit
      if (threadData.messageCount >= CONFIG.THREAD_FOLLOW_UP_MAX_MESSAGES) {
        // Remove thread participation
        cache.remove(threadKey);
        cache.remove(`thread_active_${channelId}_${threadTs}`);
        return;
      }
      
      // Update cache
      cache.put(threadKey, JSON.stringify(threadData), CONFIG.THREAD_FOLLOW_UP_TIMEOUT);
      cache.put(`thread_active_${channelId}_${threadTs}`, '1', CONFIG.THREAD_FOLLOW_UP_TIMEOUT);
    } catch (e) {
      // Re-mark participation if parsing fails
      markThreadParticipation(channelId, threadTs);
    }
  }
}

/**
 * Check if bot should respond to a thread
 */
function shouldRespondToThread(channelId, threadTs) {
  if (!CONFIG.THREAD_FOLLOW_UP_ENABLED || !threadTs) {
    return false;
  }
  
  // Quick check using simple flag
  return cache.get(`thread_active_${channelId}_${threadTs}`) === '1';
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
    projectId: CONFIG.CUSTOMGPT_PROJECT_ID,
    threadFollowUpEnabled: CONFIG.THREAD_FOLLOW_UP_ENABLED,
    threadTimeout: CONFIG.THREAD_FOLLOW_UP_TIMEOUT,
    threadMaxMessages: CONFIG.THREAD_FOLLOW_UP_MAX_MESSAGES
  });
}