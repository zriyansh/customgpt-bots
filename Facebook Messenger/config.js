// Configuration and starter questions
module.exports = {
  // Starter questions - customize these based on your agent's knowledge base
  STARTER_QUESTIONS: [
    "What can you help me with?",
    "How do I get started?",
    "What features are available?",
    "Show me some examples",
    "How does pricing work?",
    "Can you explain the API?",
    "What integrations do you support?",
    "How do I troubleshoot issues?"
  ],
  
  // Response templates
  RESPONSE_TEMPLATES: {
    welcome: `🤖 Welcome to CustomGPT Bot!

I'm powered by AI and can help answer your questions using our knowledge base.

You can:
• Ask me anything about our products and services
• Type 'help' to see available commands
• Type 'examples' to see sample questions

What would you like to know?`,
    
    help: `📚 Available Commands:

• help - Show this help message
• reset - Start a new conversation
• examples - Show example questions
• stats - View your usage statistics
• about - Learn about this bot

Just type your question naturally to get started!`,
    
    about: `ℹ️ About This Bot:

I'm an AI assistant powered by CustomGPT's RAG technology. I can answer questions based on our curated knowledge base.

Features:
• Intelligent responses from your agent's content
• Source citations for transparency
• Rate limiting for fair usage
• Conversation context management

Built with ❤️ using CustomGPT API`,
    
    rateLimit: `⏳ You've reached the rate limit. Please try again in a moment.

Your limits:
• {requests} messages per minute
• {daily} messages per day

Type 'stats' to check your usage.`,
    
    error: `❌ I encountered an error. Please try again or type 'reset' to start fresh.`,
    
    noContext: `📝 I don't have enough context to answer that. Could you please provide more details?`,
    
    maintenance: `🔧 The bot is currently under maintenance. Please try again later.`
  },
  
  // Quick reply options
  QUICK_REPLIES: {
    main: [
      { title: "Ask a question", payload: "ASK_QUESTION" },
      { title: "See examples", payload: "EXAMPLES" },
      { title: "Help", payload: "HELP" }
    ],
    
    afterAnswer: [
      { title: "Ask another", payload: "ASK_QUESTION" },
      { title: "New topic", payload: "RESET" },
      { title: "Help", payload: "HELP" }
    ],
    
    examples: [
      { title: "Getting Started", payload: "EXAMPLE_How_do_I_get_started" },
      { title: "Features", payload: "EXAMPLE_What_features_are_available" },
      { title: "Pricing", payload: "EXAMPLE_How_does_pricing_work" },
      { title: "API Guide", payload: "EXAMPLE_How_do_I_use_the_API" }
    ]
  },
  
  // Persistent menu structure
  PERSISTENT_MENU: [
    {
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
        },
        {
          title: "📊 My Stats",
          type: "postback",
          payload: "STATS"
        },
        {
          title: "🔄 Reset Chat",
          type: "postback",
          payload: "RESET"
        }
      ]
    }
  ],
  
  // Get Started button
  GET_STARTED: {
    get_started: {
      payload: "GET_STARTED"
    }
  },
  
  // Greeting text
  GREETING: [
    {
      locale: "default",
      text: "Hi {{user_first_name}}! 👋 I'm your CustomGPT assistant. Ask me anything!"
    }
  ],
  
  // Security settings
  SECURITY: {
    // Blocked patterns (regex)
    BLOCKED_PATTERNS: [
      /\b(password|token|secret|key)\b/i,
      /\b(hack|exploit|vulnerability)\b/i,
      /\b(sql|injection|xss|csrf)\b/i
    ],
    
    // Max message length
    MAX_MESSAGE_LENGTH: 1000,
    
    // Allowed user IDs (optional whitelist)
    ALLOWED_USERS: process.env.ALLOWED_USERS ? process.env.ALLOWED_USERS.split(',') : null,
    
    // Blocked user IDs
    BLOCKED_USERS: process.env.BLOCKED_USERS ? process.env.BLOCKED_USERS.split(',') : []
  }
};