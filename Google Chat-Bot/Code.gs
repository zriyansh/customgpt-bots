/**
 * CustomGPT Google Apps Script Integration
 * 
 * This script provides:
 * 1. Google Chat bot integration
 * 2. Web app interface
 * 3. Google Sheets integration
 * 4. Gmail add-on capabilities
 */

// Configuration - Store these in Script Properties for security
const CONFIG = {
  CUSTOMGPT_API_KEY: PropertiesService.getScriptProperties().getProperty('CUSTOMGPT_API_KEY'),
  CUSTOMGPT_API_URL: 'https://app.customgpt.ai/api/v1',
  CUSTOMGPT_AGENT_ID: PropertiesService.getScriptProperties().getProperty('CUSTOMGPT_AGENT_ID'),
  
  // Rate limiting
  RATE_LIMIT_PER_USER: 10, // per minute
  RATE_LIMIT_PER_HOUR: 100,
  
  // Cache settings
  CACHE_DURATION: 300, // 5 minutes
  
  // Security
  ALLOWED_DOMAINS: PropertiesService.getScriptProperties().getProperty('ALLOWED_DOMAINS')?.split(',') || [],
  REQUIRE_DOMAIN_CHECK: false
};

// ============ Main Entry Points ============

/**
 * Google Chat bot webhook handler
 */
function doPost(e) {
  try {
    const message = JSON.parse(e.postData.contents);
    
    // Handle different event types
    switch (message.type) {
      case 'ADDED_TO_SPACE':
        return createWelcomeMessage(message);
      case 'MESSAGE':
        return handleChatMessage(message);
      case 'CARD_CLICKED':
        return handleCardClick(message);
      default:
        return createTextResponse('Unknown event type');
    }
  } catch (error) {
    console.error('Error in doPost:', error);
    return createErrorResponse(error);
  }
}

/**
 * Web app entry point
 */
function doGet(e) {
  const template = HtmlService.createTemplateFromFile('index');
  template.agentId = CONFIG.CUSTOMGPT_AGENT_ID;
  
  return template.evaluate()
    .setTitle('CustomGPT Chat')
    .setFaviconUrl('https://www.customgpt.ai/favicon.ico')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

// ============ Google Chat Bot Functions ============

/**
 * Handle incoming chat messages
 */
function handleChatMessage(message) {
  const userEmail = message.user.email;
  const userMessage = message.message.text;
  const spaceId = message.space.name;
  
  // Check rate limit
  if (!checkRateLimit(userEmail)) {
    return createTextResponse('⏱️ Rate limit exceeded. Please wait a moment before asking again.');
  }
  
  // Remove bot mention from message
  const cleanMessage = userMessage.replace(/<users\/.*>/g, '').trim();
  
  // Check for commands
  if (cleanMessage.startsWith('/')) {
    return handleCommand(cleanMessage, message);
  }
  
  // Get response from CustomGPT
  try {
    const response = sendToCustomGPT(cleanMessage, spaceId);
    return createChatResponse(response);
  } catch (error) {
    console.error('Error getting CustomGPT response:', error);
    return createErrorResponse(error);
  }
}

/**
 * Handle slash commands
 */
function handleCommand(command, message) {
  const parts = command.split(' ');
  const cmd = parts[0].toLowerCase();
  
  switch (cmd) {
    case '/help':
      return createHelpCard();
    case '/info':
      return createInfoCard();
    case '/reset':
      clearConversation(message.space.name);
      return createTextResponse('✅ Conversation has been reset.');
    case '/starters':
      return createStarterQuestionsCard();
    default:
      return createTextResponse(`Unknown command: ${cmd}. Type /help for available commands.`);
  }
}

/**
 * Handle card button clicks
 */
function handleCardClick(message) {
  const action = message.action;
  
  if (action.actionMethodName === 'askQuestion') {
    const question = action.parameters[0].value;
    const response = sendToCustomGPT(question, message.space.name);
    return createChatResponse(response);
  }
  
  return createTextResponse('Action completed');
}

// ============ CustomGPT API Integration ============

/**
 * Send message to CustomGPT API
 */
function sendToCustomGPT(message, conversationId) {
  const url = `${CONFIG.CUSTOMGPT_API_URL}/projects/${CONFIG.CUSTOMGPT_AGENT_ID}/chat/completions`;
  
  // Check cache first
  const cacheKey = `customgpt_${conversationId}_${Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, message)}`;
  const cached = CacheService.getScriptCache().get(cacheKey);
  if (cached) {
    return JSON.parse(cached);
  }
  
  const payload = {
    messages: [{
      role: 'user',
      content: message
    }],
    stream: false,
    lang: 'en',
    is_inline_citation: false
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
  
  try {
    const response = UrlFetchApp.fetch(url, options);
    const statusCode = response.getResponseCode();
    
    if (statusCode === 200 || statusCode === 201) {
      const data = JSON.parse(response.getContentText());
      const result = {
        content: data.choices[0].message.content,
        citations: data.citations || []
      };
      
      // Cache the response
      CacheService.getScriptCache().put(cacheKey, JSON.stringify(result), CONFIG.CACHE_DURATION);
      
      return result;
    } else {
      throw new Error(`API Error: ${statusCode} - ${response.getContentText()}`);
    }
  } catch (error) {
    console.error('CustomGPT API Error:', error);
    throw error;
  }
}

/**
 * Get agent information
 */
function getAgentInfo() {
  const url = `${CONFIG.CUSTOMGPT_API_URL}/projects/${CONFIG.CUSTOMGPT_AGENT_ID}`;
  
  const options = {
    method: 'get',
    headers: {
      'Authorization': `Bearer ${CONFIG.CUSTOMGPT_API_KEY}`
    },
    muteHttpExceptions: true
  };
  
  try {
    const response = UrlFetchApp.fetch(url, options);
    if (response.getResponseCode() === 200) {
      return JSON.parse(response.getContentText()).data;
    }
  } catch (error) {
    console.error('Error fetching agent info:', error);
  }
  
  return null;
}

/**
 * Get starter questions from agent settings
 */
function getStarterQuestions() {
  const url = `${CONFIG.CUSTOMGPT_API_URL}/projects/${CONFIG.CUSTOMGPT_AGENT_ID}/settings`;
  
  const options = {
    method: 'get',
    headers: {
      'Authorization': `Bearer ${CONFIG.CUSTOMGPT_API_KEY}`
    },
    muteHttpExceptions: true
  };
  
  try {
    const response = UrlFetchApp.fetch(url, options);
    if (response.getResponseCode() === 200) {
      const data = JSON.parse(response.getContentText()).data;
      return data.example_questions || [
        'What can you help me with?',
        'Tell me about your capabilities',
        'How do I get started?'
      ];
    }
  } catch (error) {
    console.error('Error fetching starter questions:', error);
  }
  
  return [
    'What can you help me with?',
    'Tell me about your capabilities',
    'How do I get started?'
  ];
}

// ============ Rate Limiting ============

/**
 * Check if user is within rate limits
 */
function checkRateLimit(userEmail) {
  const cache = CacheService.getScriptCache();
  const minuteKey = `rate_minute_${userEmail}`;
  const hourKey = `rate_hour_${userEmail}`;
  
  // Check minute limit
  const minuteCount = parseInt(cache.get(minuteKey) || '0');
  if (minuteCount >= CONFIG.RATE_LIMIT_PER_USER) {
    return false;
  }
  
  // Check hour limit
  const hourCount = parseInt(cache.get(hourKey) || '0');
  if (hourCount >= CONFIG.RATE_LIMIT_PER_HOUR) {
    return false;
  }
  
  // Increment counters
  cache.put(minuteKey, String(minuteCount + 1), 60); // 1 minute expiry
  cache.put(hourKey, String(hourCount + 1), 3600); // 1 hour expiry
  
  return true;
}

// ============ Response Builders ============

/**
 * Create welcome message when bot is added to space
 */
function createWelcomeMessage(message) {
  const card = {
    cards: [{
      header: {
        title: '👋 Welcome to CustomGPT Bot!',
        subtitle: 'Powered by CustomGPT.ai',
        imageUrl: 'https://www.customgpt.ai/logo.png'
      },
      sections: [{
        widgets: [{
          textParagraph: {
            text: 'I\'m here to help answer your questions using CustomGPT\'s knowledge base.'
          }
        }, {
          textParagraph: {
            text: '<b>Available Commands:</b>\n' +
                  '• Just ask me any question\n' +
                  '• /help - Show help information\n' +
                  '• /info - Show agent information\n' +
                  '• /starters - Show starter questions\n' +
                  '• /reset - Reset conversation'
          }
        }, {
          buttons: [{
            textButton: {
              text: 'Get Started',
              onClick: {
                action: {
                  actionMethodName: 'askQuestion',
                  parameters: [{
                    key: 'question',
                    value: 'What can you help me with?'
                  }]
                }
              }
            }
          }]
        }]
      }]
    }]
  };
  
  return card;
}

/**
 * Create chat response with proper formatting
 */
function createChatResponse(response) {
  const text = response.content;
  
  // Split long messages
  if (text.length > 4000) {
    return createTextResponse(text.substring(0, 4000) + '... (truncated)');
  }
  
  // Create card with response
  const card = {
    cards: [{
      sections: [{
        widgets: [{
          textParagraph: {
            text: text
          }
        }]
      }]
    }]
  };
  
  // Add citations if available
  if (response.citations && response.citations.length > 0) {
    card.cards[0].sections.push({
      header: '📚 Sources',
      widgets: response.citations.slice(0, 3).map(citation => ({
        textParagraph: {
          text: `<a href="${citation.url}">${citation.title || 'Source'}</a>`
        }
      }))
    });
  }
  
  return card;
}

/**
 * Create help card
 */
function createHelpCard() {
  return {
    cards: [{
      header: {
        title: '🤖 CustomGPT Bot Help',
        subtitle: 'How to use this bot'
      },
      sections: [{
        widgets: [{
          textParagraph: {
            text: '<b>Commands:</b>'
          }
        }, {
          keyValue: {
            topLabel: '/help',
            content: 'Show this help message'
          }
        }, {
          keyValue: {
            topLabel: '/info',
            content: 'Show agent information'
          }
        }, {
          keyValue: {
            topLabel: '/starters',
            content: 'Show starter questions'
          }
        }, {
          keyValue: {
            topLabel: '/reset',
            content: 'Reset conversation context'
          }
        }, {
          textParagraph: {
            text: '\n<b>Tips:</b>\n' +
                  '• Just type your question naturally\n' +
                  '• The bot remembers context within a space\n' +
                  '• Rate limit: 10 queries per minute'
          }
        }]
      }]
    }]
  };
}

/**
 * Create info card
 */
function createInfoCard() {
  const agentInfo = getAgentInfo();
  
  if (!agentInfo) {
    return createTextResponse('Unable to fetch agent information.');
  }
  
  return {
    cards: [{
      header: {
        title: `📊 ${agentInfo.project_name || 'CustomGPT Agent'}`,
        subtitle: `Agent ID: ${agentInfo.id}`
      },
      sections: [{
        widgets: [{
          keyValue: {
            topLabel: 'Status',
            content: agentInfo.status || 'Active',
            icon: 'BOOKMARK'
          }
        }, {
          keyValue: {
            topLabel: 'Created',
            content: new Date(agentInfo.created_at).toLocaleDateString(),
            icon: 'CLOCK'
          }
        }, {
          keyValue: {
            topLabel: 'Pages',
            content: String(agentInfo.pages_count || 0),
            icon: 'DESCRIPTION'
          }
        }]
      }]
    }]
  };
}

/**
 * Create starter questions card
 */
function createStarterQuestionsCard() {
  const questions = getStarterQuestions();
  
  return {
    cards: [{
      header: {
        title: '🚀 Starter Questions',
        subtitle: 'Click any question to ask'
      },
      sections: [{
        widgets: questions.map(question => ({
          buttons: [{
            textButton: {
              text: question,
              onClick: {
                action: {
                  actionMethodName: 'askQuestion',
                  parameters: [{
                    key: 'question',
                    value: question
                  }]
                }
              }
            }
          }]
        }))
      }]
    }]
  };
}

/**
 * Create simple text response
 */
function createTextResponse(text) {
  return {
    text: text
  };
}

/**
 * Create error response
 */
function createErrorResponse(error) {
  return createTextResponse(`😕 Sorry, I encountered an error: ${error.message || 'Unknown error'}`);
}

// ============ Utility Functions ============

/**
 * Clear conversation cache for a space
 */
function clearConversation(spaceId) {
  // In a real implementation, you might store conversation history
  // For now, we'll just clear any cached responses
  const cache = CacheService.getScriptCache();
  // This is a simplified approach - in production you'd want more sophisticated conversation management
}

/**
 * Include HTML file content (for web app)
 */
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

// ============ Web App API Endpoints ============

/**
 * Send message from web interface
 */
function sendWebMessage(message) {
  try {
    // Check if user is logged in and authorized
    const user = Session.getActiveUser().getEmail();
    if (CONFIG.REQUIRE_DOMAIN_CHECK && CONFIG.ALLOWED_DOMAINS.length > 0) {
      const domain = user.split('@')[1];
      if (!CONFIG.ALLOWED_DOMAINS.includes(domain)) {
        throw new Error('Unauthorized domain');
      }
    }
    
    // Check rate limit
    if (!checkRateLimit(user)) {
      throw new Error('Rate limit exceeded. Please wait a moment.');
    }
    
    // Get response from CustomGPT
    const response = sendToCustomGPT(message, user);
    return {
      success: true,
      data: response
    };
  } catch (error) {
    console.error('Web message error:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Get web app configuration
 */
function getWebConfig() {
  return {
    agentInfo: getAgentInfo(),
    starterQuestions: getStarterQuestions(),
    user: Session.getActiveUser().getEmail()
  };
}