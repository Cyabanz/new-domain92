# Domain92 Discord Bot

A multi-user Discord bot version of domain92 that allows several users to use the freedns automation tool simultaneously through an interactive dropdown interface.

## Features

- **Multi-User Support**: Multiple users can use the bot simultaneously without conflicts
- **Server Selection**: Dropdown menu to select from predefined servers:
  - **PeteZah**: 62.72.3.251 (no emoji)
  - **Shadow**: 104.243.38.18 (shadow emoji)
  - **Lunar**: 199.180.255.67 (lunar emoji)
  - **Vapor**: 172.93.101.294 (vapor emoji)
  - **gn-math**: 107.174.34.44 (kahoot emoji)
- **Interactive Interface**: Easy-to-use Discord UI with buttons and modals
- **Terminal Access**: Execute safe terminal commands with security restrictions
- **Session Management**: Individual user sessions with automatic cleanup
- **Security Features**: Command restrictions and user permission controls

## Setup Instructions

### 1. Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name (e.g., "Domain92 Bot")
3. Go to the "Bot" section in the left sidebar
4. Click "Add Bot"
5. Copy the bot token (you'll need this later)
6. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent (optional)

### 2. Invite Bot to Your Server

1. Go to the "OAuth2" section in the Discord Developer Portal
2. Select "bot" under Scopes
3. Select the following permissions under Bot Permissions:
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Attach Files
   - Read Message History
   - Use External Emojis
   - Add Reactions
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Bot

1. Copy the example config file:
   ```bash
   cp config.json.example config.json
   ```

2. Edit `config.json` and add your bot token:
   ```json
   {
       "bot_token": "YOUR_ACTUAL_BOT_TOKEN_HERE",
       ...
   }
   ```

### 5. Run the Bot

```bash
python discord_bot.py
```

Or set the token as an environment variable:
```bash
export DISCORD_BOT_TOKEN="your_token_here"
python discord_bot.py
```

## Usage Instructions

### Getting Started

1. In your Discord server, type `!start` to begin
2. Select your server from the dropdown menu
3. Use the available commands to interact with domain92

### Available Commands

#### Setup Commands
- `!start` - Select your server and start a session
- `!status` - Check your current session status
- `!clear_session` - Clear your current session
- `!help_domain92` - Show all available commands

#### Domain92 Commands
- `!domain92` - Interactive domain92 interface with buttons and forms
- `!domain92_auto <number> [webhook] [auto]` - Run domain92 automatically
  - Example: `!domain92_auto 5 none y`
  - Parameters:
    - `number`: Number of links to create
    - `webhook`: Discord webhook URL or "none" (optional)
    - `auto`: "y" for automatic captcha solving, "n" for manual (optional)

#### System Commands
- `!terminal <command>` - Execute safe terminal commands
  - Allowed commands: `ls`, `pwd`, `whoami`, `date`, `uptime`, `df`, `free`, `ps`
  - Example: `!terminal ls -la`

### Interactive Interface

The bot provides an interactive interface with:
- **Dropdown Menus**: Select your server easily
- **Buttons**: Quick access to common actions
- **Modals/Forms**: Input forms for detailed configuration
- **Embeds**: Rich, formatted responses with status information

### Multi-User Features

- Each user has their own session
- Sessions are isolated to prevent conflicts
- Automatic session cleanup after inactivity
- Concurrent usage supported for all users

## Security Features

### Command Restrictions
- Terminal commands are restricted to safe, read-only operations
- No file modification or system administration commands allowed
- Command timeout after 30 seconds

### User Sessions
- Individual user sessions prevent data mixing
- Session timeouts for inactive users
- Unique output files per user to avoid conflicts

### Permission Controls
- Bot token security through environment variables or config files
- Configurable user restrictions (can be added to config)
- Logging of all bot activities

## Configuration Options

Edit `config.json` to customize:

```json
{
    "bot_token": "your_token",
    "command_prefix": "!",
    "allowed_users": [],  // Empty = allow all users
    "log_level": "INFO",
    "servers": {
        // Add or modify server configurations
        "Custom Server": "1.2.3.4"
    },
    "security": {
        "allowed_terminal_commands": [
            // Add or remove allowed commands
        ],
        "max_concurrent_sessions": 10,
        "session_timeout_minutes": 30
    }
}
```

## Troubleshooting

### Common Issues

1. **Bot doesn't respond**
   - Check if the bot is online in your server
   - Verify the bot token is correct
   - Ensure the bot has necessary permissions

2. **"No active session" error**
   - Use `!start` to select a server first
   - Check `!status` to see your current session

3. **Domain92 errors**
   - Ensure all dependencies are installed
   - Check if freedns.afraid.org is accessible
   - Verify the selected IP address is correct

4. **Permission errors**
   - Check Discord bot permissions in server settings
   - Ensure the bot role is above other roles if needed

### Logs

The bot logs activities to the console. Set `log_level` in config.json to:
- `DEBUG` - Detailed debugging information
- `INFO` - General information (default)
- `WARNING` - Only warnings and errors
- `ERROR` - Only errors

## Original Domain92 Functionality

This bot integrates all the original domain92 features:
- Automatic freedns.afraid.org account creation
- Domain link generation
- Captcha solving (automatic and manual)
- Multiple domain support
- Webhook notifications
- Proxy and Tor support

For detailed information about domain92 functionality, see the [community wiki](https://github.com/sebastian-92/domain92/wiki).

## Support

For issues related to:
- **Discord Bot**: Create an issue in this repository
- **Original Domain92**: See the [original repository](https://github.com/sebastian-92/domain92)
- **Discord.py**: Check the [discord.py documentation](https://discordpy.readthedocs.io/)

## License

This project maintains the same license as the original domain92: [GNU AGPL v3.0](LICENSE)