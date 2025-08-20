# Deploy Telegram Bot to Replit

## Step 1: Create Replit Account
1. Go to [replit.com](https://replit.com)
2. Sign up for free

## Step 2: Create New Repl
1. Click "Create Repl"
2. Choose "Python" template
3. Name it "customgpt-telegram-bot"

## Step 3: Upload Files
Upload these files to your Repl:
- `bot.py`
- `customgpt_client.py`
- `simple_cache.py`
- `requirements.txt`

## Step 4: Set Environment Variables
1. Click "Secrets" (lock icon) in left sidebar
2. Add these secrets:
   - `TELEGRAM_BOT_TOKEN` = your bot token
   - `CUSTOMGPT_API_KEY` = your API key
   - `CUSTOMGPT_PROJECT_ID` = your project ID

## Step 5: Update bot.py for Replit
Add this at the top of bot.py:
```python
import os
# Replit uses Secrets instead of .env
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CUSTOMGPT_API_KEY = os.environ.get('CUSTOMGPT_API_KEY')
CUSTOMGPT_PROJECT_ID = os.environ.get('CUSTOMGPT_PROJECT_ID')
```

## Step 6: Create main.py
```python
from bot import main

if __name__ == '__main__':
    main()
```

## Step 7: Run the Bot
1. Click "Run" button
2. Your bot should start!

## Step 8: Keep Bot Alive (Optional)
For free tier with better uptime:
1. Set up UptimeRobot to ping your Repl every 5 minutes
2. Your Repl URL: `https://your-repl-name.your-username.repl.co`

## Replit-Specific Files

### .replit
```toml
run = "python bot.py"
language = "python3"

[packager]
language = "python3"
```

### replit.nix
```nix
{ pkgs }: {
  deps = [
    pkgs.python39
    pkgs.python39Packages.pip
  ];
}