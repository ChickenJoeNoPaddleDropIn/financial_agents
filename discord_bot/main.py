import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Get Discord token from environment
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(command_prefix='!', intents=intents)
        
    async def setup_hook(self):
        # Load all cogs
        await self.load_extension('cogs.reports')
        await self.load_extension('cogs.economy')
        await self.load_extension('cogs.fun')
        
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is in {len(self.guilds)} guilds')

async def main():
    bot = DiscordBot()
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main()) 