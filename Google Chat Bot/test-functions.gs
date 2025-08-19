/**
 * Test Functions for CustomGPT Google Apps Script Integration
 * 
 * Use these functions to test your setup and troubleshoot issues
 */

/**
 * Test API connection
 */
function testAPIConnection() {
  console.log('Testing CustomGPT API connection...');
  
  try {
    // Check if credentials are set
    if (!CONFIG.CUSTOMGPT_API_KEY) {
      throw new Error('CUSTOMGPT_API_KEY not set in Script Properties');
    }
    
    if (!CONFIG.CUSTOMGPT_AGENT_ID) {
      throw new Error('CUSTOMGPT_AGENT_ID not set in Script Properties');
    }
    
    // Test API call
    const response = sendToCustomGPT('Hello, this is a test', 'test');
    
    console.log('Success! Response:', response);
    return {
      success: true,
      message: 'API connection successful',
      response: response
    };
    
  } catch (error) {
    console.error('API test failed:', error);
    return {
      success: false,
      message: error.message,
      error: error
    };
  }
}

/**
 * Test rate limiting
 */
function testRateLimit() {
  const testEmail = 'test@example.com';
  const results = [];
  
  // Try 15 requests (should hit limit at 10)
  for (let i = 1; i <= 15; i++) {
    const allowed = checkRateLimit(testEmail);
    results.push({
      attempt: i,
      allowed: allowed,
      timestamp: new Date()
    });
    
    if (!allowed) {
      console.log(`Rate limit hit at attempt ${i}`);
      break;
    }
  }
  
  return results;
}

/**
 * Test cache functionality
 */
function testCache() {
  const cache = CacheService.getScriptCache();
  const testKey = 'test_cache_key';
  const testValue = { message: 'Hello from cache', timestamp: new Date() };
  
  // Store in cache
  cache.put(testKey, JSON.stringify(testValue), 60); // 1 minute
  
  // Retrieve from cache
  const retrieved = cache.get(testKey);
  const parsed = retrieved ? JSON.parse(retrieved) : null;
  
  return {
    stored: testValue,
    retrieved: parsed,
    success: parsed !== null
  };
}

/**
 * Test agent info retrieval
 */
function testAgentInfo() {
  try {
    const info = getAgentInfo();
    console.log('Agent info:', info);
    return {
      success: true,
      info: info
    };
  } catch (error) {
    console.error('Failed to get agent info:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Test starter questions
 */
function testStarterQuestions() {
  try {
    const questions = getStarterQuestions();
    console.log('Starter questions:', questions);
    return {
      success: true,
      questions: questions
    };
  } catch (error) {
    console.error('Failed to get starter questions:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Comprehensive test suite
 */
function runAllTests() {
  console.log('Running CustomGPT integration tests...\n');
  
  const results = {
    timestamp: new Date(),
    tests: {}
  };
  
  // Test 1: API Connection
  console.log('1. Testing API connection...');
  results.tests.apiConnection = testAPIConnection();
  
  // Test 2: Agent Info
  console.log('\n2. Testing agent info retrieval...');
  results.tests.agentInfo = testAgentInfo();
  
  // Test 3: Starter Questions
  console.log('\n3. Testing starter questions...');
  results.tests.starterQuestions = testStarterQuestions();
  
  // Test 4: Cache
  console.log('\n4. Testing cache functionality...');
  results.tests.cache = testCache();
  
  // Test 5: Rate Limiting
  console.log('\n5. Testing rate limiting...');
  results.tests.rateLimit = testRateLimit();
  
  // Summary
  const passed = Object.values(results.tests).filter(t => t.success).length;
  const total = Object.keys(results.tests).length;
  
  console.log(`\n========== TEST SUMMARY ==========`);
  console.log(`Passed: ${passed}/${total}`);
  console.log(`Status: ${passed === total ? '✅ All tests passed!' : '❌ Some tests failed'}`);
  console.log('==================================\n');
  
  return results;
}

/**
 * Test Google Chat message handling
 */
function testChatMessage() {
  // Simulate a chat message
  const mockMessage = {
    type: 'MESSAGE',
    message: {
      text: 'Hello, bot!'
    },
    user: {
      email: 'test@example.com',
      displayName: 'Test User'
    },
    space: {
      name: 'spaces/test123',
      type: 'DM'
    }
  };
  
  try {
    const response = handleChatMessage(mockMessage);
    console.log('Chat response:', response);
    return {
      success: true,
      response: response
    };
  } catch (error) {
    console.error('Chat message test failed:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Debug function to check script properties
 */
function debugScriptProperties() {
  const props = PropertiesService.getScriptProperties().getProperties();
  
  // Hide sensitive data
  const safeProps = {};
  for (const key in props) {
    if (key.includes('KEY') || key.includes('TOKEN')) {
      safeProps[key] = '***' + props[key].slice(-4); // Show only last 4 chars
    } else {
      safeProps[key] = props[key];
    }
  }
  
  console.log('Script Properties:', safeProps);
  return safeProps;
}

/**
 * Test error handling
 */
function testErrorHandling() {
  const tests = [];
  
  // Test 1: Invalid API key
  const originalKey = CONFIG.CUSTOMGPT_API_KEY;
  CONFIG.CUSTOMGPT_API_KEY = 'invalid_key';
  
  try {
    sendToCustomGPT('Test', 'error-test');
    tests.push({ test: 'Invalid API key', passed: false, message: 'Should have thrown error' });
  } catch (error) {
    tests.push({ test: 'Invalid API key', passed: true, error: error.message });
  }
  
  CONFIG.CUSTOMGPT_API_KEY = originalKey;
  
  // Test 2: Invalid agent ID
  const originalId = CONFIG.CUSTOMGPT_AGENT_ID;
  CONFIG.CUSTOMGPT_AGENT_ID = '99999999';
  
  try {
    sendToCustomGPT('Test', 'error-test-2');
    tests.push({ test: 'Invalid agent ID', passed: false, message: 'Should have thrown error' });
  } catch (error) {
    tests.push({ test: 'Invalid agent ID', passed: true, error: error.message });
  }
  
  CONFIG.CUSTOMGPT_AGENT_ID = originalId;
  
  return tests;
}

/**
 * Performance test
 */
function testPerformance() {
  const iterations = 5;
  const times = [];
  
  console.log(`Running ${iterations} API calls to test performance...`);
  
  for (let i = 0; i < iterations; i++) {
    const start = new Date().getTime();
    
    try {
      sendToCustomGPT(`Performance test ${i + 1}`, 'perf-test');
      const end = new Date().getTime();
      const duration = end - start;
      times.push(duration);
      console.log(`Call ${i + 1}: ${duration}ms`);
      
      // Small delay to avoid rate limit
      Utilities.sleep(1000);
    } catch (error) {
      console.error(`Call ${i + 1} failed:`, error);
    }
  }
  
  const avg = times.reduce((a, b) => a + b, 0) / times.length;
  const min = Math.min(...times);
  const max = Math.max(...times);
  
  return {
    iterations: iterations,
    times: times,
    average: avg,
    min: min,
    max: max
  };
}

/**
 * Create test report
 */
function generateTestReport() {
  const results = runAllTests();
  
  // Create a formatted report
  let report = `CustomGPT Integration Test Report\n`;
  report += `Generated: ${results.timestamp}\n\n`;
  
  for (const [testName, result] of Object.entries(results.tests)) {
    report += `${testName}: ${result.success ? '✅ PASSED' : '❌ FAILED'}\n`;
    if (!result.success && result.error) {
      report += `  Error: ${result.error}\n`;
    }
  }
  
  // Save to Drive (optional)
  // const blob = Utilities.newBlob(report, 'text/plain', 'test-report.txt');
  // DriveApp.createFile(blob);
  
  console.log(report);
  return report;
}