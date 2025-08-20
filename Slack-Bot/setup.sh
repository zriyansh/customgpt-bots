#!/bin/bash

# CustomGPT Slack Bot Setup Script
# This script helps you set up the bot environment

set -e

echo "🤖 CustomGPT Slack Bot Setup"
echo "=========================="
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✅ Python $python_version is installed"
else
    echo "❌ Python 3.8+ is required. You have $python_version"
    exit 1
fi

# Create virtual environment
echo ""
echo "🏗️  Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
echo ""
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created from .env.example"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your credentials:"
    echo "   - SLACK_BOT_TOKEN"
    echo "   - SLACK_SIGNING_SECRET"
    echo "   - CUSTOMGPT_API_KEY"
    echo "   - CUSTOMGPT_PROJECT_ID"
else
    echo "ℹ️  .env file already exists"
fi

# Check for Redis (optional)
echo ""
echo "🔍 Checking for Redis (optional)..."
if command -v redis-cli &> /dev/null; then
    echo "✅ Redis is installed"
    redis_status=$(redis-cli ping 2>&1 || echo "not running")
    if [ "$redis_status" = "PONG" ]; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is installed but not running"
        echo "   Start Redis with: redis-server"
    fi
else
    echo "ℹ️  Redis not found (optional - needed for distributed rate limiting)"
fi

# Create logs directory
echo ""
if [ ! -d "logs" ]; then
    mkdir logs
    echo "✅ Created logs directory"
fi

# Summary
echo ""
echo "✨ Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Run the bot with: python bot.py"
echo "3. Or use Docker: docker-compose up"
echo ""
echo "For Slack setup, see README.md"
echo ""
echo "Happy botting! 🚀"