# Setting up ngrok for WhatsApp Bot

## Step 1: Create ngrok Account (Free)

1. Go to https://dashboard.ngrok.com/signup
2. Sign up for a free account (no credit card required)
3. Verify your email

## Step 2: Get Your Auth Token

1. After signing in, go to: https://dashboard.ngrok.com/get-started/your-authtoken
2. Copy your authtoken (it looks like: `2abc123XYZ...`)

## Step 3: Configure ngrok

Run this command with your authtoken:
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

## Step 4: Start ngrok

In a new terminal window, run:
```bash
ngrok http 8000
```

You'll see output like:
```
Session Status                online
Account                       your-email@example.com
Version                       3.26.0
Region                        United States (us)
Latency                       78ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8000
```

## Step 5: Copy Your Public URL

Copy the HTTPS forwarding URL (e.g., `https://abc123.ngrok-free.app`)

## Step 6: Configure Twilio

1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to: **Messaging** → **Try it out** → **Send a WhatsApp message**
3. In the "Sandbox Configuration" section:
   - Find "When a message comes in" field
   - Enter: `https://abc123.ngrok-free.app/webhook/whatsapp`
   - Method: POST
   - Click "Save"

## Step 7: Join WhatsApp Sandbox

1. In Twilio Console, you'll see instructions like:
   "Send 'join word-word' to +1 415 523 8886"
2. Open WhatsApp on your phone
3. Send the join message to the Twilio number
4. You should receive a confirmation

## Step 8: Test Your Bot

1. Send any message to the Twilio WhatsApp number
2. Your bot should respond!
3. Check your terminal for logs

## Troubleshooting

### Bot not responding?
1. Check ngrok is still running
2. Check your bot is running (`python bot.py`)
3. Check Twilio webhook URL is correct
4. Look for errors in bot terminal

### ngrok URL changed?
ngrok free tier gives you a new URL each time. When you restart ngrok:
1. Copy the new URL
2. Update it in Twilio Console
3. Save the configuration

### Want a permanent URL?
- Upgrade to ngrok paid plan for custom domains
- Or use deployment options (Railway, Render, etc.)

## Next Steps

Once testing is complete, consider:
1. Deploying to a cloud service for 24/7 availability
2. Getting a Twilio WhatsApp Business API number
3. Setting up production error monitoring