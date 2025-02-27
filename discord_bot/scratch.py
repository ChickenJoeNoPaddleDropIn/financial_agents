import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}!')

# Get token from environment variable
bot.run(os.getenv('DISCORD_TOKEN'))
