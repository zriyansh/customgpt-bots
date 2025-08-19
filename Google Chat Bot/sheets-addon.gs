/**
 * Google Sheets Add-on for CustomGPT
 * 
 * This file contains functions specifically for Google Sheets integration
 */

/**
 * Creates menu when the spreadsheet opens
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('CustomGPT')
    .addItem('Ask Question', 'showSidebar')
    .addItem('Bulk Process', 'showBulkDialog')
    .addSeparator()
    .addItem('Settings', 'showSettings')
    .addItem('Help', 'showHelp')
    .createMenu();
}

/**
 * Custom function to query CustomGPT
 * @param {string} question The question to ask
 * @param {boolean} includeSource Whether to include source citations
 * @return {string|Array} The response from CustomGPT
 * @customfunction
 */
function CUSTOMGPT(question, includeSource = false) {
  if (!question) return "Please provide a question";
  
  try {
    const response = sendToCustomGPT(String(question), "sheets-function");
    
    if (includeSource && response.citations && response.citations.length > 0) {
      return [[response.content, response.citations.map(c => c.title).join(", ")]];
    }
    
    return response.content;
  } catch (error) {
    return `Error: ${error.message}`;
  }
}

/**
 * Batch process multiple questions
 * @param {Array<Array>} range The range containing questions
 * @return {Array<Array>} The responses
 * @customfunction
 */
function CUSTOMGPT_BATCH(range) {
  if (!range || !Array.isArray(range)) {
    return "Please select a range with questions";
  }
  
  return range.map(row => {
    if (!row[0]) return [""];
    
    try {
      // Add small delay to avoid rate limits
      Utilities.sleep(100);
      const response = sendToCustomGPT(String(row[0]), "sheets-batch");
      return [response.content];
    } catch (error) {
      return [`Error: ${error.message}`];
    }
  });
}

/**
 * Show sidebar for interactive chat
 */
function showSidebar() {
  const html = HtmlService.createTemplateFromFile('sheets-sidebar')
    .evaluate()
    .setTitle('CustomGPT Assistant')
    .setWidth(300);
  
  SpreadsheetApp.getUi().showSidebar(html);
}

/**
 * Show bulk processing dialog
 */
function showBulkDialog() {
  const html = HtmlService.createTemplateFromFile('sheets-bulk')
    .evaluate()
    .setWidth(400)
    .setHeight(300);
  
  SpreadsheetApp.getUi()
    .showModalDialog(html, 'Bulk Process with CustomGPT');
}

/**
 * Process selected range with CustomGPT
 */
function processSelectedRange() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const range = sheet.getActiveRange();
  const values = range.getValues();
  
  const results = [];
  let processed = 0;
  
  for (let i = 0; i < values.length; i++) {
    for (let j = 0; j < values[i].length; j++) {
      if (values[i][j]) {
        try {
          // Check rate limit
          if (!checkRateLimit(Session.getActiveUser().getEmail())) {
            throw new Error('Rate limit exceeded. Please wait.');
          }
          
          const response = sendToCustomGPT(String(values[i][j]), "sheets-bulk-process");
          results.push([values[i][j], response.content]);
          processed++;
          
          // Small delay between requests
          Utilities.sleep(200);
        } catch (error) {
          results.push([values[i][j], `Error: ${error.message}`]);
        }
      }
    }
  }
  
  // Write results to new sheet
  if (results.length > 0) {
    const resultSheet = SpreadsheetApp.getActiveSpreadsheet()
      .insertSheet(`CustomGPT Results ${new Date().toLocaleString()}`);
    
    resultSheet.getRange(1, 1, 1, 2)
      .setValues([['Question', 'Response']])
      .setFontWeight('bold');
    
    resultSheet.getRange(2, 1, results.length, 2)
      .setValues(results);
    
    resultSheet.autoResizeColumns(1, 2);
  }
  
  return {
    processed: processed,
    total: results.length
  };
}

/**
 * Insert response at cursor position
 */
function insertResponse(response) {
  const sheet = SpreadsheetApp.getActiveSheet();
  const cell = sheet.getActiveCell();
  cell.setValue(response);
}

/**
 * Get questions from selected column
 */
function getSelectedColumnQuestions() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const range = sheet.getActiveRange();
  const values = range.getValues();
  
  return values.filter(row => row[0]).map(row => row[0]);
}

/**
 * Settings management
 */
function showSettings() {
  const html = HtmlService.createTemplateFromFile('sheets-settings')
    .evaluate()
    .setWidth(400)
    .setHeight(500);
  
  SpreadsheetApp.getUi()
    .showModalDialog(html, 'CustomGPT Settings');
}

/**
 * Save settings to document properties
 */
function saveSheetSettings(settings) {
  const documentProperties = PropertiesService.getDocumentProperties();
  documentProperties.setProperties({
    'customgpt_default_mode': settings.defaultMode || 'concise',
    'customgpt_include_sources': settings.includeSources || 'false',
    'customgpt_auto_process': settings.autoProcess || 'false'
  });
  
  return { success: true };
}

/**
 * Get current settings
 */
function getSheetSettings() {
  const documentProperties = PropertiesService.getDocumentProperties();
  return {
    defaultMode: documentProperties.getProperty('customgpt_default_mode') || 'concise',
    includeSources: documentProperties.getProperty('customgpt_include_sources') === 'true',
    autoProcess: documentProperties.getProperty('customgpt_auto_process') === 'true'
  };
}

/**
 * Show help dialog
 */
function showHelp() {
  const html = HtmlService.createHtmlOutput(`
    <div style="font-family: Arial, sans-serif; padding: 20px;">
      <h2>CustomGPT Sheets Add-on Help</h2>
      
      <h3>Functions:</h3>
      <p><code>=CUSTOMGPT("Your question")</code><br>
      Ask a single question and get a response.</p>
      
      <p><code>=CUSTOMGPT("Your question", TRUE)</code><br>
      Include source citations with the response.</p>
      
      <p><code>=CUSTOMGPT_BATCH(A1:A10)</code><br>
      Process multiple questions at once.</p>
      
      <h3>Menu Options:</h3>
      <ul>
        <li><b>Ask Question:</b> Open sidebar for interactive chat</li>
        <li><b>Bulk Process:</b> Process selected cells with CustomGPT</li>
        <li><b>Settings:</b> Configure add-on preferences</li>
      </ul>
      
      <h3>Tips:</h3>
      <ul>
        <li>Select cells before using Bulk Process</li>
        <li>Responses are cached for 5 minutes</li>
        <li>Rate limit: 10 queries per minute</li>
      </ul>
      
      <p><a href="https://docs.customgpt.ai" target="_blank">View Full Documentation</a></p>
    </div>
  `);
  
  html.setWidth(400).setHeight(500);
  SpreadsheetApp.getUi()
    .showModalDialog(html, 'Help - CustomGPT Sheets Add-on');
}

/**
 * Custom menu for specific sheet operations
 */
function createConditionalFormatting() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const range = sheet.getDataRange();
  
  // Highlight cells with questions
  const questionRule = SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains('?')
    .setBackground('#e3f2fd')
    .setRanges([range])
    .build();
  
  // Highlight cells with errors
  const errorRule = SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains('Error:')
    .setBackground('#ffebee')
    .setRanges([range])
    .build();
  
  const rules = sheet.getConditionalFormatRules();
  rules.push(questionRule);
  rules.push(errorRule);
  sheet.setConditionalFormatRules(rules);
}

/**
 * Template generation functions
 */
function generateFAQTemplate() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet()
    .insertSheet('FAQ Template');
  
  const headers = [['Question', 'CustomGPT Response', 'Reviewed', 'Notes']];
  const sampleQuestions = [
    ['What are your business hours?', '=CUSTOMGPT(A2)', 'FALSE', ''],
    ['How do I reset my password?', '=CUSTOMGPT(A3)', 'FALSE', ''],
    ['What payment methods do you accept?', '=CUSTOMGPT(A4)', 'FALSE', ''],
    ['How can I track my order?', '=CUSTOMGPT(A5)', 'FALSE', ''],
    ['What is your return policy?', '=CUSTOMGPT(A6)', 'FALSE', '']
  ];
  
  sheet.getRange(1, 1, 1, 4).setValues(headers).setFontWeight('bold');
  sheet.getRange(2, 1, sampleQuestions.length, 4).setValues(sampleQuestions);
  sheet.autoResizeColumns(1, 4);
  
  // Add checkbox for reviewed column
  sheet.getRange(2, 3, sampleQuestions.length, 1).insertCheckboxes();
}

/**
 * Auto-process new entries (for triggers)
 */
function onEdit(e) {
  const settings = getSheetSettings();
  
  if (settings.autoProcess) {
    const range = e.range;
    const value = e.value;
    
    // Check if edit is in designated column and contains a question
    if (value && value.includes('?')) {
      const responseColumn = range.getColumn() + 1;
      
      try {
        const response = sendToCustomGPT(value, "sheets-auto");
        range.getSheet().getRange(range.getRow(), responseColumn)
          .setValue(response.content);
      } catch (error) {
        range.getSheet().getRange(range.getRow(), responseColumn)
          .setValue(`Error: ${error.message}`);
      }
    }
  }
}