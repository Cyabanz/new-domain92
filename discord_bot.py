import discord
from discord.ext import commands
import asyncio
import subprocess
import os
import json
from typing import Dict, Optional
import logging
from datetime import datetime
import sys
import importlib.util

# Import domain92 functionality
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import specific functions we need from domain92
import importlib.util
spec = importlib.util.spec_from_file_location("domain92_main", "domain92/__main__.py")
domain92_main = importlib.util.module_from_spec(spec)

# Mock the version function to avoid import errors
def mock_version(package):
    return "1.2.0"

# Temporarily replace the version function
import importlib.metadata
original_version = importlib.metadata.version
importlib.metadata.version = mock_version

try:
    spec.loader.exec_module(domain92_main)
finally:
    # Restore original version function
    importlib.metadata.version = original_version

# Import the functions we need
checkprint = domain92_main.checkprint
finddomains = domain92_main.finddomains
createlinks = domain92_main.createlinks
client = domain92_main.client
domainlist = domain92_main.domainlist
domainnames = domain92_main.domainnames

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Server configurations with IP addresses
SERVERS = {
    "PeteZah": "62.72.3.251",
    "Shadow": "104.243.38.18", 
    "Lunar": "199.180.255.67",
    "Lunar Alt": "172.93.101.294"
}

# Active user sessions to prevent conflicts
active_sessions: Dict[int, Dict] = {}

class ServerSelectView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=300)  # 5 minute timeout
        self.user_id = user_id
    
    @discord.ui.select(
        placeholder="Select your server",
        options=[
            discord.SelectOption(
                label="PeteZah", 
                value="62.72.3.251",
                description="PeteZah's server"
            ),
            discord.SelectOption(
                label="Shadow", 
                value="104.243.38.18",
                description="Shadow's server"
            ),
            discord.SelectOption(
                label="Lunar", 
                value="199.180.255.67",
                description="Lunar's server"
            ),
            discord.SelectOption(
                label="Lunar Alt", 
                value="172.93.101.294",
                description="Lunar's alternative server"
            ),
        ]
    )
    async def select_callback(self, interaction, select):
        selected_ip = select.values[0]
        server_name = None
        
        # Find server name by IP
        for name, ip in SERVERS.items():
            if ip == selected_ip:
                server_name = name
                break
        
        # Store user session
        active_sessions[self.user_id] = {
            'server_name': server_name,
            'server_ip': selected_ip,
            'timestamp': datetime.now()
        }
        
        embed = discord.Embed(
            title="Server Selected",
            description=f"Selected **{server_name}** ({selected_ip})",
            color=0x00ff00
        )
        embed.add_field(
            name="Available Commands",
            value="• `!domain92` - Run domain92 with interactive prompts\n"
                  "• `!domain92_auto <number> [options]` - Run domain92 automatically\n"
                  "• `!terminal <command>` - Execute terminal command\n"
                  "• `!status` - Check your current session\n"
                  "• `!clear_session` - Clear your current session",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=None)

class Domain92CommandView(discord.ui.View):
    def __init__(self, user_id: int, server_ip: str):
        super().__init__(timeout=600)  # 10 minute timeout
        self.user_id = user_id
        self.server_ip = server_ip
    
    @discord.ui.button(label="Create Links", style=discord.ButtonStyle.primary)
    async def create_links(self, button, interaction):
        await interaction.response.defer()
        
        try:
            # Create a modal for input
            modal = Domain92InputModal(self.user_id, self.server_ip, "create_links")
            await interaction.followup.send("Please fill in the details:", view=None)
            await interaction.user.send("Opening input form...", view=modal)
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")
    
    @discord.ui.button(label="Check Status", style=discord.ButtonStyle.secondary)
    async def check_status(self, button, interaction):
        session = active_sessions.get(self.user_id)
        if session:
            embed = discord.Embed(
                title="Session Status",
                description=f"Server: {session['server_name']} ({session['server_ip']})\n"
                           f"Started: {session['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
                color=0x0099ff
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("No active session found.", ephemeral=True)

class Domain92InputModal(discord.ui.Modal):
    def __init__(self, user_id: int, server_ip: str, action: str):
        super().__init__(title="Domain92 Configuration")
        self.user_id = user_id
        self.server_ip = server_ip
        self.action = action
        
        self.number_input = discord.ui.TextInput(
            label="Number of links to create",
            placeholder="Enter number (e.g., 5)",
            required=True,
            max_length=10
        )
        self.add_item(self.number_input)
        
        self.webhook_input = discord.ui.TextInput(
            label="Webhook URL (optional)",
            placeholder="Discord webhook URL or 'none'",
            required=False,
            max_length=500
        )
        self.add_item(self.webhook_input)
        
        self.auto_captcha = discord.ui.TextInput(
            label="Auto-solve captchas? (y/n)",
            placeholder="y for automatic, n for manual",
            required=False,
            max_length=1,
            default="y"
        )
        self.add_item(self.auto_captcha)
    
    async def on_submit(self, interaction):
        await interaction.response.defer()
        
        try:
            number = int(self.number_input.value)
            webhook = self.webhook_input.value or "none"
            auto = self.auto_captcha.value.lower() == "y"
            
            # Execute domain92 with the provided parameters
            result = await run_domain92_async(
                ip=self.server_ip,
                number=number,
                webhook=webhook,
                auto=auto,
                user_id=self.user_id
            )
            
            # Send result back to user
            if len(result) > 2000:
                # Split long messages
                chunks = [result[i:i+1900] for i in range(0, len(result), 1900)]
                for chunk in chunks:
                    await interaction.followup.send(f"```\n{chunk}\n```")
            else:
                await interaction.followup.send(f"```\n{result}\n```")
                
        except ValueError:
            await interaction.followup.send("Invalid number provided. Please enter a valid integer.")
        except Exception as e:
            await interaction.followup.send(f"Error executing domain92: {str(e)}")

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='start')
async def start_command(ctx):
    """Start using the domain92 bot"""
    user_id = ctx.author.id
    
    embed = discord.Embed(
        title="Welcome to Domain92 Discord Bot",
        description="This bot allows you to run domain92 commands on different servers.\n"
                   "Please select your server to get started:",
        color=0x0099ff
    )
    
    view = ServerSelectView(user_id)
    await ctx.send(embed=embed, view=view)

@bot.command(name='domain92')
async def domain92_command(ctx):
    """Run domain92 with interactive interface"""
    user_id = ctx.author.id
    
    if user_id not in active_sessions:
        await ctx.send("Please select a server first using `!start`")
        return
    
    session = active_sessions[user_id]
    server_ip = session['server_ip']
    server_name = session['server_name']
    
    embed = discord.Embed(
        title=f"Domain92 - {server_name}",
        description=f"Running on server: {server_name} ({server_ip})",
        color=0x00ff00
    )
    
    view = Domain92CommandView(user_id, server_ip)
    await ctx.send(embed=embed, view=view)

@bot.command(name='domain92_auto')
async def domain92_auto_command(ctx, number: int, webhook: str = "none", auto: str = "y"):
    """Run domain92 automatically with specified parameters"""
    user_id = ctx.author.id
    
    if user_id not in active_sessions:
        await ctx.send("Please select a server first using `!start`")
        return
    
    session = active_sessions[user_id]
    server_ip = session['server_ip']
    
    await ctx.send(f"Running domain92 on {session['server_name']} ({server_ip})...")
    
    try:
        result = await run_domain92_async(
            ip=server_ip,
            number=number,
            webhook=webhook,
            auto=(auto.lower() == "y"),
            user_id=user_id
        )
        
        # Send result
        if len(result) > 2000:
            chunks = [result[i:i+1900] for i in range(0, len(result), 1900)]
            for chunk in chunks:
                await ctx.send(f"```\n{chunk}\n```")
        else:
            await ctx.send(f"```\n{result}\n```")
            
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command(name='terminal')
async def terminal_command(ctx, *, command: str):
    """Execute a terminal command (restricted for security)"""
    user_id = ctx.author.id
    
    if user_id not in active_sessions:
        await ctx.send("Please select a server first using `!start`")
        return
    
    # Security check - only allow safe commands
    safe_commands = ['ls', 'pwd', 'whoami', 'date', 'uptime', 'df', 'free', 'ps']
    command_parts = command.split()
    
    if not command_parts or command_parts[0] not in safe_commands:
        await ctx.send(f"Command '{command_parts[0] if command_parts else command}' is not allowed for security reasons.\n"
                      f"Allowed commands: {', '.join(safe_commands)}")
        return
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout if result.stdout else result.stderr
        if not output:
            output = "Command executed successfully (no output)"
        
        if len(output) > 1900:
            output = output[:1900] + "\n... (output truncated)"
        
        await ctx.send(f"```\n{output}\n```")
        
    except subprocess.TimeoutExpired:
        await ctx.send("Command timed out after 30 seconds")
    except Exception as e:
        await ctx.send(f"Error executing command: {str(e)}")

@bot.command(name='status')
async def status_command(ctx):
    """Check your current session status"""
    user_id = ctx.author.id
    session = active_sessions.get(user_id)
    
    if session:
        embed = discord.Embed(
            title="Session Status",
            description=f"**Server:** {session['server_name']} ({session['server_ip']})\n"
                       f"**Started:** {session['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
            color=0x0099ff
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("No active session found. Use `!start` to begin.")

@bot.command(name='clear_session')
async def clear_session_command(ctx):
    """Clear your current session"""
    user_id = ctx.author.id
    
    if user_id in active_sessions:
        del active_sessions[user_id]
        await ctx.send("Session cleared. Use `!start` to select a new server.")
    else:
        await ctx.send("No active session to clear.")

@bot.command(name='help_domain92')
async def help_command(ctx):
    """Show help for domain92 bot commands"""
    embed = discord.Embed(
        title="Domain92 Discord Bot Help",
        description="Available commands:",
        color=0x0099ff
    )
    
    embed.add_field(
        name="Setup Commands",
        value="• `!start` - Select your server and start a session\n"
              "• `!status` - Check your current session\n"
              "• `!clear_session` - Clear your current session",
        inline=False
    )
    
    embed.add_field(
        name="Domain92 Commands", 
        value="• `!domain92` - Interactive domain92 interface\n"
              "• `!domain92_auto <number> [webhook] [auto]` - Run automatically\n"
              "  Example: `!domain92_auto 5 none y`",
        inline=False
    )
    
    embed.add_field(
        name="System Commands",
        value="• `!terminal <command>` - Execute safe terminal commands\n"
              "  Allowed: ls, pwd, whoami, date, uptime, df, free, ps",
        inline=False
    )
    
    embed.add_field(
        name="Available Servers",
        value="• **PeteZah**: 62.72.3.251\n"
              "• **Shadow**: 104.243.38.18\n" 
              "• **Lunar**: 199.180.255.67\n"
              "• **Lunar Alt**: 172.93.101.294",
        inline=False
    )
    
    await ctx.send(embed=embed)

async def run_domain92_async(ip: str, number: int, webhook: str = "none", auto: bool = True, user_id: int = None):
    """Run domain92 asynchronously and return the output"""
    try:
        # Create a temporary args object similar to the CLI
        import argparse
        temp_args = argparse.Namespace(
            ip=ip,
            number=number,
            webhook=webhook,
            auto=auto,
            silent=True,  # Reduce output for Discord
            proxy="none",
            use_tor=False,
            outfile=f"domainlist_{user_id}_{datetime.now().timestamp()}.txt",
            type="A",
            pages="1-10",
            subdomains="random",
            single_tld=None
        )
        
        # Temporarily replace global args
        global args
        original_args = args
        args = temp_args
        
        # Capture output
        output_lines = []
        
        def capture_print(text):
            output_lines.append(str(text))
        
        # Replace checkprint temporarily
        global checkprint
        original_checkprint = checkprint
        checkprint = capture_print
        
        try:
            # Run the main domain creation logic
            finddomains(temp_args.pages)
            createlinks(temp_args.number)
            
            # Read the output file if it exists
            if os.path.exists(temp_args.outfile):
                with open(temp_args.outfile, 'r') as f:
                    file_content = f.read()
                output_lines.append(f"\nGenerated domains:\n{file_content}")
                
                # Clean up the file
                os.remove(temp_args.outfile)
            
            result = "\n".join(output_lines) if output_lines else "Domain92 completed successfully"
            
        finally:
            # Restore original functions
            args = original_args
            checkprint = original_checkprint
        
        return result
        
    except Exception as e:
        return f"Error running domain92: {str(e)}"

# Load bot token from environment or config file
def load_config():
    """Load bot configuration"""
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f)
    return {}

def main():
    """Main function to run the bot"""
    config = load_config()
    token = config.get('bot_token') or os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        print("Error: No bot token found!")
        print("Please either:")
        print("1. Set the DISCORD_BOT_TOKEN environment variable")
        print("2. Create a config.json file with 'bot_token' field")
        return
    
    try:
        bot.run(token)
    except Exception as e:
        print(f"Error running bot: {e}")

if __name__ == "__main__":
    main()