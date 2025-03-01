from discord.ext import commands, tasks
import discord
from datetime import datetime, timedelta
import yfinance as yf
from typing import List, Dict
import asyncio
import os
import pandas as pd

class Reports(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Get channel ID from environment variable
        channel_id_str = os.getenv('DISCORD_CHANNEL_ID')
        self.channel_id = int(channel_id_str) if channel_id_str else None
        if not self.channel_id:
            print("Warning: DISCORD_CHANNEL_ID not set")
        
    async def get_earnings_data(self, timeframe: str = "day") -> List[Dict]:
        """Fetch earnings data for the specified timeframe"""
        today = datetime.now().date()
        
        if timeframe == "week":
            end_date = today + timedelta(days=7)
        else:  # day
            end_date = today
            
        earnings_list = []
        try:
            # You might want to maintain a list of stocks you're interested in
            # For now, we'll use some example tickers
            tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]  # Add your desired tickers
            
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    calendar = stock.calendar
                    if calendar is not None and isinstance(calendar, pd.DataFrame) and not calendar.empty:
                        earnings_date = calendar.index[0].date()
                        if today <= earnings_date <= end_date:
                            earnings_list.append({
                                "ticker": ticker,
                                "date": earnings_date,
                                "name": stock.info.get("longName", ticker)
                            })
                except Exception as e:
                    print(f"Error fetching data for {ticker}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching earnings data: {e}")
            
        return earnings_list

    async def generate_report(self, is_weekly: bool = False):
        """Generate and send the market report to the configured channel"""
        if not self.channel_id:
            print("Error: Discord channel ID not configured")
            return
            
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print(f"Error: Could not find channel with ID {self.channel_id}")
            return
            
        timeframe = "week" if is_weekly else "day"
        today = datetime.now().date()
        
        # Send header message
        header = f"🌟 **Market Report for {today.strftime('%A, %B %d, %Y')}**\n\n"
        await channel.send(header)
        
        # Create earnings embed
        earnings_embed = discord.Embed(
            title="📊 Earnings Report",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        # Add earnings section
        earnings = await self.get_earnings_data(timeframe)
        if earnings:
            description = f"Here are the companies reporting earnings this {'week' if is_weekly else 'today'}:\n\n"
            earnings_text = "\n".join([f"• {e['name']} ({e['ticker']}) - {e['date'].strftime('%A, %B %d')}" 
                                     for e in earnings])
            earnings_embed.description = description + earnings_text
        else:
            earnings_embed.description = f"No companies in our watchlist are reporting earnings this {'week' if is_weekly else 'today'}."
        
        await channel.send(embed=earnings_embed)
        
        # Add economic events section
        econ_header = f"\n🗓️ Here's the economic news for the {'week' if is_weekly else 'day'}:\n"
        await channel.send(econ_header)
        
        # Get the economy cog to access economic events
        economy_cog = self.bot.get_cog("Economy")
        if economy_cog:
            await economy_cog.econ_events(channel, timeframe)
        else:
            await channel.send("⚠️ Economic events data is currently unavailable.")
        
        # Send footer
        footer = "\n-------------------\n"
        await channel.send(footer)

    @commands.command()
    async def daily_report(self, ctx=None):
        """Generate daily market report"""
        await self.generate_report(is_weekly=False)

    @commands.command()
    async def weekly_report(self, ctx=None):
        """Generate weekly market report"""
        await self.generate_report(is_weekly=True)

async def setup(bot):
    await bot.add_cog(Reports(bot)) 