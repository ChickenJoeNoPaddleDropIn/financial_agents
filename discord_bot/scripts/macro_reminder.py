import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from main import DiscordBot

# Get channel ID from environment variable
CHANNEL_ID = int(os.getenv("TRADING_CHANNEL_ID"))  # Convert to integer since Discord IDs are numbers

def get_message_content(time_str):
    # Special time-based messages
    if time_str == "9:30":
        return "Ding! Ding! Ding! 🔔\nWhat do you see? 👁️"
    elif time_str == "11:30":
        return "Lunch Time 🍱\nWhat do you see? 👁️"
    elif time_str == "3:15":
        return "3:15-3:45 Macro ⏰\nWhat do you see? 👁️"
    elif time_str == "3:50":
        return "Market On Close 📊\nWhat do you see? 👁️"
    
    # Regular macro time messages
    return f"{time_str} Macro Time! 🎯\nWhat do you see? 👁️"

async def send_macro_reminder(time_str):
    if not CHANNEL_ID:
        print("Error: CHANNEL_ID not set. Please set the CHANNEL_ID at the top of the script.")
        return

    bot = DiscordBot()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN not set")
        return

    print("Starting bot...")
    
    @bot.event
    async def on_ready():
        print("Bot is ready, sending macro reminder...")
        try:
            channel = bot.get_channel(CHANNEL_ID)
            
            if channel:
                message = get_message_content(time_str)
                await channel.send(message)
                print("Macro reminder sent successfully!")
            else:
                print(f"Error: Could not find channel with ID {CHANNEL_ID}")
        except Exception as e:
            print(f"Error sending macro reminder: {e}")
        finally:
            await bot.close()
            print("Bot shutting down...")
    
    try:
        await bot.start(token)
    except Exception as e:
        print(f"Error running bot: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python macro_reminder.py <time>")
        print("Valid times: 7, 8, 9, 9:30, 10, 11, 11:30, 12, 1, 2, 3, 3:15, 3:50")
        sys.exit(1)
    
    time_str = sys.argv[1]
    valid_times = ["7", "8", "9", "9:30", "10", "11", "11:30", "12", "1", "2", "3", "3:15", "3:50"]
    
    if time_str not in valid_times:
        print(f"Error: Invalid time. Must be one of: {', '.join(valid_times)}")
        sys.exit(1)
    
    asyncio.run(send_macro_reminder(time_str)) 