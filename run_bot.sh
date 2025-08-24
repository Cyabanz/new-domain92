#!/bin/bash

# Domain92 Discord Bot Startup Script

echo "Starting Domain92 Discord Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if config file exists
if [ ! -f "config.json" ]; then
    echo "Config file not found. Creating from example..."
    cp config.json.example config.json
    echo "Please edit config.json with your bot token before running again."
    echo "You can also set the DISCORD_BOT_TOKEN environment variable instead."
    exit 1
fi

# Check for bot token
if [ -z "$DISCORD_BOT_TOKEN" ]; then
    echo "Checking config file for bot token..."
    if ! grep -q "YOUR_DISCORD_BOT_TOKEN_HERE" config.json; then
        echo "Bot token found in config file."
    else
        echo "Please set your bot token in config.json or as DISCORD_BOT_TOKEN environment variable."
        exit 1
    fi
else
    echo "Using bot token from environment variable."
fi

# Add domain92 to PATH
export PATH="/home/ubuntu/.local/bin:$PATH"

# Start the bot
echo "Starting Discord bot..."
python3 discord_bot.py