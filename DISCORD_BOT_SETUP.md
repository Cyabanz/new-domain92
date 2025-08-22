# Quick Setup Guide - Domain92 Discord Bot

## What Was Created

The domain92 CLI tool has been transformed into a multi-user Discord bot with the following new files:

### Core Files
- `discord_bot.py` - Main Discord bot application
- `requirements.txt` - All required Python dependencies
- `config.json.example` - Configuration template

### Setup Scripts
- `run_bot.sh` - Linux/Mac startup script
- `run_bot.bat` - Windows startup script

### Documentation
- `README_DISCORD_BOT.md` - Complete documentation
- `DISCORD_BOT_SETUP.md` - This quick setup guide

## Quick Start (3 Steps)

### 1. Create Discord Bot
1. Go to https://discord.com/developers/applications
2. Create new application → Bot section → Copy token
3. OAuth2 section → Select "bot" → Copy invite URL → Add to server

### 2. Configure
```bash
# Copy config template
cp config.json.example config.json

# Edit config.json and replace "YOUR_DISCORD_BOT_TOKEN_HERE" with your actual token
```

### 3. Run
```bash
# Linux/Mac
./run_bot.sh

# Windows
run_bot.bat

# Or manually
pip install -r requirements.txt
python discord_bot.py
```

## Discord Commands

- `!start` - Select server (PeteZah/Shadow/Lunar/Lunar Alt)
- `!domain92` - Interactive interface
- `!domain92_auto 5` - Create 5 links automatically
- `!terminal ls` - Execute safe terminal commands
- `!help_domain92` - Show all commands

## Server Configuration

The bot includes these predefined servers:
- **PeteZah**: 62.72.3.251 (no emoji)
- **Shadow**: 104.243.38.18 (shadow emoji)
- **Lunar**: 199.180.255.67 (lunar emoji)
- **Lunar Alt**: 172.93.101.294 (vapor emoji)
- **gn-math**: 107.174.34.44 (kahoot emoji)

## Multi-User Features

✅ Multiple users can use simultaneously  
✅ Individual user sessions  
✅ Dropdown server selection  
✅ Interactive Discord UI  
✅ Secure terminal access  
✅ Session management  

## Security Features

- Restricted terminal commands (ls, pwd, whoami, date, uptime, df, free, ps)
- Individual user sessions prevent conflicts
- Command timeouts (30 seconds)
- Configurable user permissions

## Need Help?

See `README_DISCORD_BOT.md` for complete documentation including:
- Detailed setup instructions
- Full command reference
- Troubleshooting guide
- Configuration options

The original domain92 CLI functionality remains unchanged and available.