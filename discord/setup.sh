#!/bin/bash

echo "CustomGPT Discord Bot Setup Script"
echo "=================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "Error: Python 3.8 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✓ Python version check passed"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
else
    echo "✓ .env file already exists"
fi

# Create logs directory
mkdir -p logs

echo ""
echo "Setup complete! Next steps:"
echo "1. Edit .env file with your Discord bot token and CustomGPT credentials"
echo "2. Run the bot with: python bot.py"
echo ""
echo "For deployment instructions, see README.md"