import discord
from discord.ext import commands
import json

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

# Create bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Test bot ready: {bot.user}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def test(ctx):
    await ctx.send('Test bot is working!')

if __name__ == "__main__":
    print("Starting test bot...")
    bot.run(config['bot_token'])