# Thread Follow-Up Testing Guide

This guide describes how to test the thread follow-up functionality in the CustomGPT Slack Bot.

## Configuration

The thread follow-up feature is controlled by the following environment variables:

```bash
# Enable/disable thread follow-up feature (default: true)
THREAD_FOLLOW_UP_ENABLED=true

# Timeout in seconds after which bot stops responding to thread (default: 3600 = 1 hour)
THREAD_FOLLOW_UP_TIMEOUT=3600

# Maximum messages bot will respond to in a thread (default: 50)
THREAD_FOLLOW_UP_MAX_MESSAGES=50

# Ignore messages from all bots to prevent loops (default: true)
IGNORE_BOT_MESSAGES=true
```

## Test Scenarios

### 1. Basic Thread Follow-Up
1. Mention the bot in a channel: `@CustomGPT what is the weather?`
2. Bot responds in a thread
3. In the same thread (without mentioning bot): `What about tomorrow?`
4. **Expected**: Bot responds to the follow-up question

### 2. Thread Timeout
1. Start a thread with the bot
2. Wait for `THREAD_FOLLOW_UP_TIMEOUT` seconds
3. Send a message in the thread without mentioning the bot
4. **Expected**: Bot does not respond (thread participation expired)

### 3. Message Limit
1. Start a thread with the bot
2. Have a conversation until `THREAD_FOLLOW_UP_MAX_MESSAGES` is reached
3. Send another message without mentioning the bot
4. **Expected**: Bot does not respond (message limit reached)

### 4. Bot Message Filtering
1. Have another bot post in a thread where CustomGPT is active
2. **Expected**: CustomGPT ignores the other bot's message

### 5. Multiple Threads
1. Start threads in multiple channels
2. Have conversations in each thread
3. **Expected**: Bot maintains separate context for each thread

### 6. Thread Broadcast
1. Start a thread with the bot
2. Send a message to the thread with "Also send to channel" checked
3. **Expected**: Bot ignores the broadcast message

### 7. Direct Messages
1. Send a direct message to the bot
2. **Expected**: Bot responds (no mention needed in DMs)

### 8. Feature Toggle
1. Set `THREAD_FOLLOW_UP_ENABLED=false`
2. Start a thread with the bot
3. Send a follow-up without mentioning
4. **Expected**: Bot does not respond to follow-ups

### 9. Re-mentioning in Thread
1. Start a thread with the bot
2. Let it timeout or reach message limit
3. Mention the bot again in the same thread
4. **Expected**: Bot reactivates thread participation

### 10. Empty Messages
1. Start a thread with the bot
2. Send an empty message or just spaces
3. **Expected**: Bot ignores the empty message

## Edge Cases Handled

1. **Infinite Loop Prevention**: Bot ignores its own messages and other bot messages
2. **System Messages**: Bot ignores join/leave/edit notifications
3. **Thread Broadcasts**: Bot ignores messages posted to both thread and channel
4. **Empty Messages**: Bot ignores messages with no content
5. **Rate Limiting**: Thread messages still count toward rate limits
6. **Security**: Thread messages still require user permissions

## Monitoring

Check logs for thread participation:
- `"Marked thread participation: {thread_key}"`
- `"Responding to thread follow-up: {reason}"`
- `"Not responding to thread: {reason}"`
- `"Cleaned up X expired thread participations"`

## Troubleshooting

### Bot not responding to thread follow-ups
1. Check if `THREAD_FOLLOW_UP_ENABLED=true`
2. Verify thread hasn't timed out
3. Check message count hasn't exceeded limit
4. Ensure bot was mentioned in the thread first

### Bot responding to its own messages
1. Verify `IGNORE_BOT_MESSAGES=true`
2. Check bot user ID is properly initialized
3. Look for "Bot initialized with user ID" in logs

### Performance issues
1. Monitor thread participation map size
2. Check cleanup task is running (hourly)
3. Consider reducing `THREAD_FOLLOW_UP_TIMEOUT`