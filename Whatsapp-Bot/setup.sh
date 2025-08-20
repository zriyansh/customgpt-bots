#!/bin/bash

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo "Setup complete! To run the bot:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Copy .env.example to .env and fill in your credentials"
echo "3. Run the bot: python bot.py"