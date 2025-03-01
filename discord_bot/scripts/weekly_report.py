import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from main import DiscordBot

async def run_report():
    bot = DiscordBot()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN not set")
        return

    print("Starting bot...")
    
    @bot.event
    async def on_ready():
        print("Bot is ready, sending report...")
        try:
            reports_cog = bot.get_cog("Reports")
            if reports_cog:
                await reports_cog.weekly_report(None)
                print("Report sent successfully!")
            else:
                print("Error: Reports cog not found")
        except Exception as e:
            print(f"Error sending report: {e}")
        finally:
            await bot.close()
            print("Bot shutting down...")
    
    try:
        await bot.start(token)
    except Exception as e:
        print(f"Error running bot: {e}")

if __name__ == "__main__":
    asyncio.run(run_report()) 