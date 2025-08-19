#!/usr/bin/env python3
"""
Script to set Telegram webhook for your bot
"""

import sys
import json
import urllib.request
import urllib.error

def set_webhook(bot_token, webhook_url):
    """Set webhook for Telegram bot"""
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    data = json.dumps({
        "url": webhook_url,
        "drop_pending_updates": True  # Optional: ignore old messages
    }).encode('utf-8')
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        req = urllib.request.Request(api_url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.URLError as e:
        return {"ok": False, "error": str(e)}

def get_webhook_info(bot_token):
    """Get current webhook info"""
    api_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    
    try:
        with urllib.request.urlopen(api_url) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.URLError as e:
        return {"ok": False, "error": str(e)}

def delete_webhook(bot_token):
    """Delete webhook (switch back to polling)"""
    api_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
    
    try:
        with urllib.request.urlopen(api_url) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.URLError as e:
        return {"ok": False, "error": str(e)}

def main():
    print("Telegram Bot Webhook Setup")
    print("-" * 30)
    
    # Get bot token
    bot_token = input("Enter your bot token: ").strip()
    if not bot_token:
        print("❌ Bot token is required!")
        sys.exit(1)
    
    # Show current webhook info
    print("\nChecking current webhook...")
    info = get_webhook_info(bot_token)
    
    if info.get("ok"):
        webhook_data = info.get("result", {})
        current_url = webhook_data.get("url", "")
        if current_url:
            print(f"✓ Current webhook: {current_url}")
            print(f"  Pending updates: {webhook_data.get('pending_update_count', 0)}")
        else:
            print("✓ No webhook currently set (bot is using polling)")
    else:
        print(f"❌ Error getting webhook info: {info.get('error')}")
    
    # Ask what to do
    print("\nWhat would you like to do?")
    print("1. Set new webhook")
    print("2. Delete webhook (switch to polling)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        # Set webhook
        webhook_url = input("\nEnter your Vercel webhook URL (e.g., https://your-app.vercel.app/api/webhook): ").strip()
        if not webhook_url:
            print("❌ Webhook URL is required!")
            sys.exit(1)
        
        print(f"\nSetting webhook to: {webhook_url}")
        result = set_webhook(bot_token, webhook_url)
        
        if result.get("ok"):
            print("✅ Webhook set successfully!")
            print("\nYour bot is now ready to receive messages via webhook.")
            print("Make sure your Vercel app is deployed and environment variables are set.")
        else:
            print(f"❌ Error setting webhook: {result.get('error', result.get('description', 'Unknown error'))}")
    
    elif choice == "2":
        # Delete webhook
        print("\nDeleting webhook...")
        result = delete_webhook(bot_token)
        
        if result.get("ok"):
            print("✅ Webhook deleted successfully!")
            print("Your bot is now in polling mode. Run bot.py to receive messages.")
        else:
            print(f"❌ Error deleting webhook: {result.get('error', result.get('description', 'Unknown error'))}")
    
    else:
        print("Exiting...")

if __name__ == "__main__":
    main()