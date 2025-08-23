import discord
from discord.ext import commands
import asyncio
import subprocess
import os
import json
from typing import Dict, Optional, List
import logging
from datetime import datetime
import sys
import importlib.util
import re
from database import db

# Import domain92 functionality - using subprocess approach to avoid import conflicts
# We'll use subprocess calls instead of direct imports to avoid execution conflicts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Server configurations with IP addresses and custom emojis
SERVERS = {
    "PeteZah": "62.72.3.251",
    "Shadow": "104.243.38.18", 
    "Lunar": "172.93.101.294",
    "Vapor": "199.180.255.67",
    "gn-math": "107.174.34.44",
    "Frogiees Arcade": "152.53.81.196",
    "ExtremeMath": "152.53.38.152"
}

# Custom emojis for servers and UI
EMOJIS = {
    "shadow": "<:IMG_0342:1408216293865164810>",
    "gn_math": "<:IMG_0345:1408216292414062612>", 
    "vapor": "<:IMG_0346:1408216290752987197>",
    "lunar": "<:IMG_0347:1408216520034881536>",
    "frogiees": "<:emoji_5:1408292931579678821>",
    "extrememath": "<:emoji_6:1408295630727806996>",
    "petezah": "<:emoji_7:1408297382570889227>",
    "loading": "<:1320138023291060386:1403395950625427519>"
}

# Active user sessions to prevent conflicts
active_sessions: Dict[int, Dict] = {}

# Bot configuration
UNLIMITED_USER_ID = 1058841701495615630  # User with unlimited usage
ALLOWED_SERVER_ID = 1394337103441301524  # Only server where bot can be used

class ServerSelectView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=300)  # 5 minute timeout
        self.user_id = user_id
    
    @discord.ui.select(
        placeholder="🎯 Select your server",
        options=[
            discord.SelectOption(
                label="PeteZah", 
                value="62.72.3.251",
                description="PeteZah's server",
                emoji=EMOJIS["petezah"]
            ),
            discord.SelectOption(
                label="Shadow", 
                value="104.243.38.18",
                description="Shadow's server",
                emoji=EMOJIS["shadow"]
            ),
            discord.SelectOption(
                label="Lunar", 
                value="172.93.101.294",
                description="Lunar's server",
                emoji=EMOJIS["lunar"]
            ),
            discord.SelectOption(
                label="Vapor", 
                value="199.180.255.67",
                description="Vapor server",
                emoji=EMOJIS["vapor"]
            ),
            discord.SelectOption(
                label="gn-math", 
                value="107.174.34.44",
                description="gn-math server (Kahoot)",
                emoji=EMOJIS["gn_math"]
            ),
            discord.SelectOption(
                label="Frogiees Arcade", 
                value="152.53.81.196",
                description="Frogiees Arcade server",
                emoji=EMOJIS["frogiees"]
            ),
            discord.SelectOption(
                label="ExtremeMath", 
                value="152.53.38.152",
                description="ExtremeMath server",
                emoji=EMOJIS["extrememath"]
            ),
        ]
    )
    async def server_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        try:
            selected_ip = select.values[0]
            server_name = None
            
            # Find server name by IP - use the same method as test
            for option in select.options:
                if option.value == selected_ip:
                    server_name = option.label
                    break
        
            # Store user session
            active_sessions[self.user_id] = {
                'server_name': server_name,
                'server_ip': selected_ip,
                'timestamp': datetime.now()
            }
            
            # Get the appropriate emoji for the server
            server_emoji = ""
            if server_name == "Shadow":
                server_emoji = EMOJIS["shadow"]
            elif server_name == "PeteZah":
                server_emoji = EMOJIS["petezah"]  # PeteZah emoji
            elif server_name == "Lunar":
                server_emoji = EMOJIS["lunar"]
            elif server_name == "Vapor":
                server_emoji = EMOJIS["vapor"]  # Vapor emoji for Vapor server
            elif server_name == "gn-math":
                server_emoji = EMOJIS["gn_math"]  # gn-math emoji for kahoot server
            elif server_name == "Frogiees Arcade":
                server_emoji = EMOJIS["frogiees"]  # Frogiees emoji for arcade server
            elif server_name == "ExtremeMath":
                server_emoji = EMOJIS["extrememath"]  # ExtremeMath emoji
            
            embed = discord.Embed(
                title=f"{server_emoji} Server Selected",
                description=f"Selected **{server_name}** ({selected_ip})",
                color=0x00ff00
            )
            embed.add_field(
                name="🚀 Available Commands",
                value=f"• `!domain92` - Interactive interface (with subdomain options)\n"
                      f"• `!domain92_auto 5` - Create 5 links automatically\n"
                      f"• `!domain92_subs 3 api,test,demo` - Create with specific subdomains\n"
                      f"• `!terminal ls` - Execute safe terminal commands\n"
                      f"• `!status` - Check your current session\n"
                      f"• `!clear_session` - Clear your current session",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Dropdown error: {str(e)}", ephemeral=True)

class Domain92CommandView(discord.ui.View):
    def __init__(self, user_id: int, server_ip: str):
        super().__init__(timeout=600)  # 10 minute timeout
        self.user_id = user_id
        self.server_ip = server_ip
    
    @discord.ui.button(label="Create Links", style=discord.ButtonStyle.primary)
    async def create_links(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Create a modal for input
            modal = Domain92InputModal(self.user_id, self.server_ip, "create_links")
            await interaction.response.send_modal(modal)
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="Check Status", style=discord.ButtonStyle.secondary)
    async def check_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        session = active_sessions.get(self.user_id)
        if session:
            # Get server emoji
            server_name = session['server_name']
            server_emoji = ""
            if server_name == "Shadow":
                server_emoji = EMOJIS["shadow"]
            elif server_name == "PeteZah":
                server_emoji = EMOJIS["petezah"]  # PeteZah emoji
            elif server_name == "Lunar":
                server_emoji = EMOJIS["lunar"]
            elif server_name == "Vapor":
                server_emoji = EMOJIS["vapor"]  # Vapor emoji for Vapor server
            elif server_name == "gn-math":
                server_emoji = EMOJIS["gn_math"]  # gn-math emoji for kahoot server
            elif server_name == "Frogiees Arcade":
                server_emoji = EMOJIS["frogiees"]  # Frogiees emoji for arcade server
            elif server_name == "ExtremeMath":
                server_emoji = EMOJIS["extrememath"]  # ExtremeMath emoji
                
            embed = discord.Embed(
                title=f"{server_emoji} Session Status",
                description=f"Server: {server_name} ({session['server_ip']})\n"
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
        
        self.pages_input = discord.ui.TextInput(
            label="Pages to scrape (optional)",
            placeholder="e.g., 1-5 or 1,3,5 (default: 1-5)",
            required=False,
            max_length=20,
            default="1-5"
        )
        self.add_item(self.pages_input)
        
        self.subdomains_input = discord.ui.TextInput(
            label="Subdomains (optional)",
            placeholder="e.g., api,test,demo,www,mail (default: random)",
            required=False,
            max_length=100,
            default="random"
        )
        self.add_item(self.subdomains_input)
    
    async def on_submit(self, interaction):
        await interaction.response.defer()
        
        try:
            number = int(self.number_input.value)
            webhook = self.webhook_input.value or "none"
            auto = self.auto_captcha.value.lower() == "y"
            pages = self.pages_input.value or "1-5"
            subdomains = self.subdomains_input.value or "random"
            
            # Execute domain92 with the provided parameters
            result, created_domains, raw_output = await run_domain92_async(
                ip=self.server_ip,
                number=number,
                webhook=webhook,
                auto=auto,
                pages=pages,
                subdomains=subdomains,
                user_id=self.user_id,
                username=interaction.user.name,
                server_name=active_sessions[self.user_id]['server_name']
            )
            
            # Send clickable links to user's DM if domains were created
            if created_domains:
                dm_result = await send_links_to_user_dm(
                    interaction.user, 
                    created_domains, 
                    active_sessions[self.user_id]['server_name'],
                    self.server_ip,
                    raw_output
                )
                
                # Notify about DM with embed
                success_embed = discord.Embed(
                    title="✅ Domains Created Successfully!",
                    description=f"**{len(created_domains)} domain(s)** created on **{active_sessions[self.user_id]['server_name']}**",
                    color=0x00ff00,
                    timestamp=datetime.now()
                )
                success_embed.add_field(
                    name="📩 Check Your DMs",
                    value="Your clickable domain links with IDs have been sent to your DMs!",
                    inline=False
                )
                success_embed.add_field(
                    name="🔗 Manage Your Domains",
                    value="Use `!mylinks` to view and manage your active domains",
                    inline=False
                )
                success_embed.set_footer(text="Domain92 Discord Bot")
                
                await interaction.followup.send(embed=success_embed)
            else:
                # Send result back to user if no domains were extracted
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

def is_allowed_server(ctx):
    """Check if command is being used in the allowed server"""
    if ctx.guild and ctx.guild.id == ALLOWED_SERVER_ID:
        return True
    return False

async def check_server_restriction(ctx):
    """Check server restriction and send error if not allowed"""
    if not is_allowed_server(ctx):
        embed = discord.Embed(
            title="❌ Server Restriction",
            description="This bot can only be used in the authorized server.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return False
    return True

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot commands: {[cmd.name for cmd in bot.commands]}')
    print(f'Allowed server ID: {ALLOWED_SERVER_ID}')
    print(f'Unlimited user ID: {UNLIMITED_USER_ID}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    print(f'Received message: "{message.content}" from {message.author} in server: {message.guild.id if message.guild else "DM"}')
    
    # Process commands
    await bot.process_commands(message)

@bot.command(name='start')
async def start_command(ctx):
    """Start using the domain92 bot"""
    # Check server restriction
    if not await check_server_restriction(ctx):
        return
        
    user_id = ctx.author.id
    
    # Check if user has unlimited access
    unlimited_notice = ""
    if user_id == UNLIMITED_USER_ID:
        unlimited_notice = "\n🌟 **You have unlimited link creation!**"
    
    embed = discord.Embed(
        title="🎮 Welcome to Domain92 Discord Bot",
        description="This bot allows you to run domain92 commands on different servers.\n"
                   f"Please select your server to get started:{unlimited_notice}",
        color=0x0099ff
    )
    embed.add_field(
        name="🖥️ Available Servers",
        value=f"{EMOJIS['petezah']} **PeteZah** - 62.72.3.251\n"
              f"{EMOJIS['shadow']} **Shadow** - 104.243.38.18\n"
              f"{EMOJIS['lunar']} **Lunar** - 172.93.101.294\n"
              f"{EMOJIS['vapor']} **Vapor** - 199.180.255.67\n"
              f"{EMOJIS['gn_math']} **gn-math** - 107.174.34.44\n"
              f"{EMOJIS['frogiees']} **Frogiees Arcade** - 152.53.81.196\n"
              f"{EMOJIS['extrememath']} **ExtremeMath** - 152.53.38.152",
        inline=False
    )
    
    view = ServerSelectView(user_id)
    await ctx.send(embed=embed, view=view)

@bot.command(name='domain92')
async def domain92_command(ctx):
    """Run domain92 with interactive interface"""
    # Check server restriction
    if not await check_server_restriction(ctx):
        return
        
    user_id = ctx.author.id
    
    if user_id not in active_sessions:
        await ctx.send("Please select a server first using `!start`")
        return
    
    session = active_sessions[user_id]
    server_ip = session['server_ip']
    server_name = session['server_name']
    
    # Get server emoji
    server_emoji = ""
    if server_name == "Shadow":
        server_emoji = EMOJIS["shadow"]
    elif server_name == "PeteZah":
        server_emoji = EMOJIS["petezah"]  # PeteZah emoji
    elif server_name == "Lunar":
        server_emoji = EMOJIS["lunar"]
    elif server_name == "Vapor":
        server_emoji = EMOJIS["vapor"]  # Vapor emoji for Vapor server
    elif server_name == "gn-math":
        server_emoji = EMOJIS["gn_math"]  # gn-math emoji for kahoot server
    elif server_name == "Frogiees Arcade":
        server_emoji = EMOJIS["frogiees"]  # Frogiees emoji for arcade server
    elif server_name == "ExtremeMath":
        server_emoji = EMOJIS["extrememath"]  # ExtremeMath emoji
    
    embed = discord.Embed(
        title=f"{server_emoji} Domain92 - {server_name}",
        description=f"Running on server: **{server_name}** ({server_ip})",
        color=0x00ff00
    )
    
    view = Domain92CommandView(user_id, server_ip)
    await ctx.send(embed=embed, view=view)

@bot.command(name='domain92_auto')
async def domain92_auto_command(ctx, number: int, webhook: str = "none", auto: str = "y"):
    """Run domain92 automatically with specified parameters"""
    # Check server restriction
    if not await check_server_restriction(ctx):
        return
        
    user_id = ctx.author.id
    
    if user_id not in active_sessions:
        await ctx.send("Please select a server first using `!start`")
        return
    
    session = active_sessions[user_id]
    server_ip = session['server_ip']
    
    await ctx.send(f"Running domain92 on {session['server_name']} ({server_ip})...")
    
    try:
        result, created_domains, raw_output = await run_domain92_async(
            ip=server_ip,
            number=number,
            webhook=webhook,
            auto=(auto.lower() == "y"),
            pages="1-5",  # Default pages for auto command
            subdomains="random",  # Default subdomains for auto command
            user_id=user_id,
            username=ctx.author.name,
            server_name=session['server_name']
        )
        
        # Send clickable links to user's DM if domains were created
        if created_domains:
            dm_result = await send_links_to_user_dm(
                ctx.author, 
                created_domains, 
                session['server_name'],
                server_ip,
                raw_output
            )
            
            # Notify about DM with embed
            success_embed = discord.Embed(
                title="✅ Domains Created Successfully!",
                description=f"**{len(created_domains)} domain(s)** created on **{session['server_name']}**",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            success_embed.add_field(
                name="📩 Check Your DMs",
                value="Your clickable domain links with IDs have been sent to your DMs!",
                inline=False
            )
            success_embed.add_field(
                name="🔗 Manage Your Domains",
                value="Use `!mylinks` to view and manage your active domains",
                inline=False
            )
            success_embed.set_footer(text="Domain92 Discord Bot")
            
            await ctx.send(embed=success_embed)
        else:
            # Send result if no domains were extracted
            if len(result) > 2000:
                chunks = [result[i:i+1900] for i in range(0, len(result), 1900)]
                for chunk in chunks:
                    await ctx.send(f"```\n{chunk}\n```")
            else:
                await ctx.send(f"```\n{result}\n```")
            
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command(name='domain92_subs')
async def domain92_subs_command(ctx, number: int, subdomains: str, webhook: str = "none", auto: str = "y"):
    """Run domain92 with specific subdomains"""
    # Check server restriction
    if not await check_server_restriction(ctx):
        return
        
    user_id = ctx.author.id
    
    if user_id not in active_sessions:
        await ctx.send("Please select a server first using `!start`")
        return
    
    session = active_sessions[user_id]
    server_ip = session['server_ip']
    
    # Validate subdomains format
    if not subdomains or subdomains == "random":
        subdomain_display = "random subdomains"
    else:
        subdomain_display = f"subdomains: {subdomains}"
    
    await ctx.send(f"🚀 Creating {number} domains with {subdomain_display} on {session['server_name']} ({server_ip})...")
    
    try:
        result, created_domains, raw_output = await run_domain92_async(
            ip=server_ip,
            number=number,
            webhook=webhook,
            auto=(auto.lower() == "y"),
            pages="1-5",
            subdomains=subdomains,
            user_id=user_id,
            username=ctx.author.name,
            server_name=session['server_name']
        )
        
        # Send clickable links to user's DM if domains were created
        if created_domains:
            dm_result = await send_links_to_user_dm(
                ctx.author, 
                created_domains, 
                session['server_name'],
                server_ip,
                raw_output
            )
            
            # Notify about DM with embed
            success_embed = discord.Embed(
                title="✅ Domains Created Successfully!",
                description=f"**{len(created_domains)} domain(s)** created on **{session['server_name']}** with subdomains: `{subdomains}`",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            success_embed.add_field(
                name="📩 Check Your DMs",
                value="Your clickable domain links with IDs have been sent to your DMs!",
                inline=False
            )
            success_embed.add_field(
                name="🔗 Manage Your Domains",
                value="Use `!mylinks` to view and manage your active domains",
                inline=False
            )
            success_embed.set_footer(text="Domain92 Discord Bot")
            
            await ctx.send(embed=success_embed)
        else:
            # Send result if no domains were extracted
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
    # Check server restriction
    if not await check_server_restriction(ctx):
        return
        
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
    # Check server restriction
    if not await check_server_restriction(ctx):
        return
        
    user_id = ctx.author.id
    session = active_sessions.get(user_id)
    
    if session:
        # Get server emoji
        server_name = session['server_name']
        server_emoji = ""
        if server_name == "Shadow":
            server_emoji = EMOJIS["shadow"]
        elif server_name == "PeteZah":
            server_emoji = EMOJIS["petezah"]  # PeteZah emoji
        elif server_name == "Lunar":
            server_emoji = EMOJIS["lunar"]
        elif server_name == "Vapor":
            server_emoji = EMOJIS["vapor"]  # Vapor emoji for Vapor server
        elif server_name == "gn-math":
            server_emoji = EMOJIS["gn_math"]  # gn-math emoji for kahoot server
        elif server_name == "Frogiees Arcade":
            server_emoji = EMOJIS["frogiees"]  # Frogiees emoji for arcade server
        elif server_name == "ExtremeMath":
            server_emoji = EMOJIS["extrememath"]  # ExtremeMath emoji
        
        embed = discord.Embed(
            title=f"{server_emoji} Session Status",
            description=f"**Server:** {server_name} ({session['server_ip']})\n"
                       f"**Started:** {session['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
            color=0x0099ff
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("No active session found. Use `!start` to begin.")

@bot.command(name='clear_session')
async def clear_session_command(ctx):
    """Clear your current session"""
    # Check server restriction
    if not await check_server_restriction(ctx):
        return
        
    user_id = ctx.author.id
    
    if user_id in active_sessions:
        del active_sessions[user_id]
        await ctx.send("Session cleared. Use `!start` to select a new server.")
    else:
        await ctx.send("No active session to clear.")

@bot.command(name='mylinks')
async def mylinks_command(ctx):
    """Show user's active domain links"""
    # Check server restriction
    if not await check_server_restriction(ctx):
        return
        
    user_id = ctx.author.id
    username = ctx.author.name
    
    # Add user to database if not exists
    db.add_user(user_id, username)
    
    # Get user links and stats
    user_links = db.get_user_links(user_id, active_only=True)
    user_stats = db.get_user_stats(user_id)
    
    if not user_links:
        embed = discord.Embed(
            title="📋 Your Domain Links",
            description="You don't have any active domain links yet.\n\nUse `!start` to select a server and create some domains!",
            color=0x0099ff
        )
        await ctx.send(embed=embed)
        return
    
    # Create embed with user's links
    if user_id == UNLIMITED_USER_ID:
        description = f"**{user_stats['active_links']}** active links • 🌟 **UNLIMITED ACCESS**"
    else:
        description = f"**{user_stats['active_links']}/3** active links • **{user_stats['remaining_slots']}** slots remaining"
        
    embed = discord.Embed(
        title="📋 Your Active Domain Links",
        description=description,
        color=0x00ff00,
        timestamp=datetime.now()
    )
    
    # Add links with clickable format (limit to prevent Discord embed size errors)
    link_text = ""
    limited_links = user_links[:8]  # Limit to 8 links to stay under character limit
    
    for i, link in enumerate(limited_links, 1):
        domain = link['domain_name']
        server = link['server_name']
        created = link['created_at']
        
        # Format creation date
        try:
            date_obj = datetime.fromisoformat(created.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime('%m/%d/%Y')
        except:
            formatted_date = created[:10]
        
        clickable_url = f"http://{domain}" if not domain.startswith(('http://', 'https://')) else domain
        link_text += f"{i}. [{domain}]({clickable_url}) • {server} • {formatted_date}\n"
    
    # Add note if there are more links
    if len(user_links) > 8:
        link_text += f"\n... and {len(user_links) - 8} more links"
    
    embed.add_field(
        name="🔗 Your Domains",
        value=link_text,
        inline=False
    )
    
    embed.add_field(
        name="📊 Stats",
        value=f"• Total created: {user_stats['total_links_created']}\n"
              f"• Member since: {user_stats['first_seen'][:10]}",
        inline=False
    )
    
    embed.set_footer(text="Use !removelink <domain> to remove a link • Click domains to visit")
    
    await ctx.send(embed=embed)

@bot.command(name='removelink')
async def removelink_command(ctx, *, domain_name: str = None):
    """Remove a specific domain link"""
    # Check server restriction
    if not await check_server_restriction(ctx):
        return
        
    user_id = ctx.author.id
    
    if not domain_name:
        await ctx.send("❌ Please specify a domain to remove.\nUsage: `!removelink example.domain.com`")
        return
    
    # Clean up domain name
    domain_name = domain_name.strip().replace('http://', '').replace('https://', '')
    
    # Get user's links to verify ownership
    user_links = db.get_user_links(user_id, active_only=True)
    
    # Check if user owns this domain
    owned_domains = [link['domain_name'] for link in user_links]
    
    if domain_name not in owned_domains:
        await ctx.send(f"❌ You don't own the domain `{domain_name}`\n\nUse `!mylinks` to see your active domains.")
        return
    
    # Deactivate the link
    db.deactivate_user_link(user_id, domain_name)
    
    # Get updated stats
    user_stats = db.get_user_stats(user_id)
    
    embed = discord.Embed(
        title="🗑️ Link Removed",
        description=f"Successfully removed: **{domain_name}**",
        color=0xff9900
    )
    
    embed.add_field(
        name="📊 Updated Stats",
        value=f"• Active links: {user_stats['active_links']}/3\n"
              f"• Available slots: {user_stats['remaining_slots']}",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='mystats')
async def mystats_command(ctx):
    """Show detailed user statistics"""
    # Check server restriction
    if not await check_server_restriction(ctx):
        return
        
    user_id = ctx.author.id
    username = ctx.author.name
    
    # Add user to database if not exists
    db.add_user(user_id, username)
    
    user_stats = db.get_user_stats(user_id)
    
    embed = discord.Embed(
        title="📊 Your Domain92 Statistics",
        description=f"Statistics for **{username}**",
        color=0x0099ff,
        timestamp=datetime.now()
    )
    
    # Show different stats for unlimited user
    if user_id == UNLIMITED_USER_ID:
        link_usage = f"• Active links: **{user_stats['active_links']}** 🌟\n" \
                    f"• Access level: **UNLIMITED** ♾️\n" \
                    f"• Total created: **{user_stats['total_links_created']}**"
    else:
        link_usage = f"• Active links: **{user_stats['active_links']}/3**\n" \
                    f"• Available slots: **{user_stats['remaining_slots']}**\n" \
                    f"• Total created: **{user_stats['total_links_created']}**"
    
    embed.add_field(
        name="🔗 Link Usage",
        value=link_usage,
        inline=False
    )
    
    embed.add_field(
        name="📅 Account Info",
        value=f"• Member since: {user_stats['first_seen'][:10]}\n"
              f"• Last active: {user_stats['last_active'][:10]}",
        inline=False
    )
    
    embed.set_footer(text="Use !mylinks to manage your domains")
    
    await ctx.send(embed=embed)

@bot.command(name='help_domain92')
async def help_command(ctx):
    """Show help for domain92 bot commands"""
    # Check server restriction
    if not await check_server_restriction(ctx):
        return
        
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
              "  Example: `!domain92_auto 5 none y`\n"
              "• `!domain92_subs <number> <subdomains> [webhook] [auto]` - Run with specific subdomains\n"
              "  Example: `!domain92_subs 3 api,test,demo none y`",
        inline=False
    )
    
    embed.add_field(
        name="Link Management Commands",
        value="• `!mylinks` - View your active domains (3 link limit)\n"
              "• `!removelink <domain>` - Remove a specific domain\n"
              "• `!mystats` - View your detailed statistics",
        inline=False
    )
    
    embed.add_field(
        name="System Commands",
        value="• `!terminal <command>` - Execute safe terminal commands\n"
              "  Allowed: ls, pwd, whoami, date, uptime, df, free, ps",
        inline=False
    )
    
    embed.add_field(
        name="🖥️ Available Servers",
        value=f"• {EMOJIS['petezah']} **PeteZah**: 62.72.3.251\n"
              f"• {EMOJIS['shadow']} **Shadow**: 104.243.38.18\n" 
              f"• {EMOJIS['lunar']} **Lunar**: 172.93.101.294\n"
              f"• {EMOJIS['vapor']} **Vapor**: 199.180.255.67\n"
              f"• {EMOJIS['gn_math']} **gn-math**: 107.174.34.44\n"
              f"• {EMOJIS['frogiees']} **Frogiees Arcade**: 152.53.81.196\n"
              f"• {EMOJIS['extrememath']} **ExtremeMath**: 152.53.38.152",
        inline=False
    )
    
    await ctx.send(embed=embed)

def extract_domains_from_output(output: str) -> List[str]:
    """Extract domain names from domain92 output"""
    domains = []
    
    # Look for URLs in the output (http:// or https://)
    url_pattern = r'https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    url_matches = re.findall(url_pattern, output)
    domains.extend(url_matches)
    
    # Look for domain patterns (domain.tld format)
    domain_pattern = r'\b([a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
    domain_matches = re.findall(domain_pattern, output)
    domains.extend(domain_matches)
    
    # Remove duplicates and clean up
    unique_domains = list(set(domains))
    return [domain.strip() for domain in unique_domains if domain.strip()]

async def send_links_to_user_dm(user, domains: List[str], server_name: str, server_ip: str, raw_output: str = ""):
    """Send clickable domain links to user's DM"""
    try:
        if not domains:
            return
        
        # Create embed with clickable links
        embed = discord.Embed(
            title=f"{EMOJIS['loading']} Your Domain92 Links Are Ready!",
            description=f"Created {len(domains)} domain(s) on **{server_name}** ({server_ip})",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        # Extract domain IDs from raw output if available
        domain_ids = []
        if raw_output:
            # Look for domain IDs in the output (sequences of numbers in quotes)
            id_pattern = r"'(\d+)'"
            domain_ids = re.findall(id_pattern, raw_output)
        
        # Add domain IDs if found (limit to prevent Discord embed size errors)
        if domain_ids:
            # Limit to first 50 IDs to stay under Discord's 1024 character limit
            limited_ids = domain_ids[:50]
            # Split into chunks of 10 for better formatting
            id_chunks = [limited_ids[i:i+10] for i in range(0, len(limited_ids), 10)]
            id_text = ""
            for chunk in id_chunks:
                id_text += ", ".join(chunk) + "\n"
            
            # Add note if there are more IDs
            if len(domain_ids) > 50:
                id_text += f"\n... and {len(domain_ids) - 50} more IDs"
            
            embed.add_field(
                name="🎯 Generated Domain IDs",
                value=f"```{id_text.strip()}```",
                inline=False
            )
        
        # Add clickable links (limit to prevent Discord embed size errors)
        link_text = ""
        limited_domains = domains[:10]  # Limit to 10 links to stay under character limit
        
        for i, domain in enumerate(limited_domains, 1):
            # Ensure domain has protocol
            if not domain.startswith(('http://', 'https://')):
                clickable_url = f"http://{domain}"
            else:
                clickable_url = domain
                
            link_text += f"{i}. [{domain}]({clickable_url})\n"
        
        # Add note if there are more domains
        if len(domains) > 10:
            link_text += f"\n... and {len(domains) - 10} more domains"
        
        embed.add_field(
            name="🔗 Clickable Links",
            value=link_text,
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Info",
            value=f"• All domains point to: `{server_ip}`\n"
                  f"• Type: A Records\n"
                  f"• Status: Active",
            inline=False
        )
        
        embed.set_footer(text="Domain92 Discord Bot • Click links to visit your domains")
        
        await user.send(embed=embed)
        
    except discord.Forbidden:
        return "❌ Cannot send DM - user has DMs disabled"
    except Exception as e:
        return f"❌ Error sending DM: {str(e)}"

async def run_domain92_async(ip: str, number: int, webhook: str = "none", auto: bool = True, pages: str = "1-5", subdomains: str = "random", user_id: int = None, username: str = None, server_name: str = None):
    """Run domain92 asynchronously using subprocess for maximum speed"""
    try:
        # Check user limits before creating (unless unlimited user)
        if user_id != UNLIMITED_USER_ID:
            can_create, remaining, current_count = db.can_user_create_links(user_id, number)
            
            if not can_create:
                return f"❌ **Link Limit Exceeded!**\n\n" \
                       f"• You have {current_count}/3 active links\n" \
                       f"• You can create {remaining} more links\n" \
                       f"• Requested: {number} links\n\n" \
                       f"Use `!mylinks` to manage your existing links.", []
        
        # Build command arguments for domain92 with all required parameters
        cmd = [
            "python3", "-m", "domain92",
            "--ip", ip,
            "--number", str(number),
            "--webhook", webhook,
            "--silent",  # Reduce output for Discord
            "--pages", pages,  # Use provided pages parameter
            "--subdomains", subdomains  # Use provided subdomains parameter
        ]
        
        if auto:
            cmd.append("--auto")
            
        # Add output file
        outfile = f"domainlist_{user_id}_{int(datetime.now().timestamp())}.txt"
        cmd.extend(["--outfile", outfile])
        
        # Run domain92 as subprocess for speed and isolation
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/workspace"
        )
        
        stdout, stderr = await process.communicate()
        
        # Collect output
        output_lines = []
        if stdout:
            output_lines.append(stdout.decode())
        if stderr:
            output_lines.append(f"Errors: {stderr.decode()}")
        
        # Read the output file and extract domains
        created_domains = []
        if os.path.exists(outfile):
            with open(outfile, 'r') as f:
                file_content = f.read()
            output_lines.append(f"\n🎯 Generated domains:\n{file_content}")
            
            # Extract domains from file content
            created_domains = extract_domains_from_output(file_content)
            
            # Clean up the file
            os.remove(outfile)
        
        # If no domains found in file, try to extract from stdout
        if not created_domains and stdout:
            created_domains = extract_domains_from_output(stdout.decode())
        
        # Save domains to database if any were created
        if created_domains and user_id and username and server_name:
            db.add_user_links(user_id, username, created_domains, server_name, ip)
        
        result = "\n".join(output_lines) if output_lines else "✅ Domain92 completed successfully"
        
        # Get raw output for domain IDs
        raw_output = ""
        if stdout:
            raw_output = stdout.decode()
        elif os.path.exists(outfile.replace('.txt', '_raw.txt')):
            with open(outfile.replace('.txt', '_raw.txt'), 'r') as f:
                raw_output = f.read()
        
        # Return result, created domains, and raw output
        return result, created_domains, raw_output
        
    except Exception as e:
        return f"❌ Error running domain92: {str(e)}", [], ""

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