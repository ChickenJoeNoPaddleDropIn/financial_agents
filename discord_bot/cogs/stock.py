from discord.ext import commands
import yfinance as yf
import discord
from datetime import datetime, timedelta
import pandas as pd

class Stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def price(self, ctx, ticker: str):
        """Get current price of a stock
        Usage: !price AAPL"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            current_price = info.get('regularMarketPrice', 0)
            
            if not current_price:
                await ctx.send(f"Unable to get current price data for {ticker}. The market might be closed.")
                return
                
            await ctx.send(f"💰 {ticker.upper()}: ${current_price:.2f}")
        except Exception as e:
            await ctx.send(f"Error getting price for {ticker}: {str(e)}")
            import traceback
            print(traceback.format_exc())

    @commands.command()
    async def summary(self, ctx, ticker: str):
        """Get a quick summary of a stock
        Usage: !summary AAPL"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get basic info first
            info = stock.info
            current_price = info.get('regularMarketPrice', 0)
            day_high = info.get('dayHigh', 0)
            day_low = info.get('dayLow', 0)
            volume = info.get('volume', 0)
            
            if not current_price:
                await ctx.send(f"Unable to get current price data for {ticker}. The market might be closed.")
                return
            
            embed = discord.Embed(title=f"{ticker.upper()} Summary", color=0x808080)
            embed.add_field(name="Current Price", value=f"${current_price:.2f}", inline=True)
            
            if day_high:
                embed.add_field(name="Day High", value=f"${day_high:.2f}", inline=True)
            if day_low:
                embed.add_field(name="Day Low", value=f"${day_low:.2f}", inline=True)
            if volume:
                embed.add_field(name="Volume", value=f"{volume:,}", inline=True)
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error getting summary for {ticker}: {str(e)}")
            import traceback
            print(traceback.format_exc())

    @commands.command()
    async def history(self, ctx, ticker: str, days: int = 7):
        """Get price history for a stock
        Usage: !history AAPL 7"""
        try:
            if days > 30:  # Limit to prevent abuse
                await ctx.send("Please request 30 days or fewer!")
                return
                
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f"{days}d")
            
            # Calculate price change
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            change = ((end_price - start_price) / start_price) * 100
            
            embed = discord.Embed(
                title=f"{ticker.upper()} {days}-Day History",
                color=0x00ff00 if change >= 0 else 0xff0000
            )
            
            embed.add_field(
                name="Price Change",
                value=f"{'📈' if change >= 0 else '📉'} {change:.2f}%",
                inline=False
            )
            embed.add_field(
                name="Start Price",
                value=f"${start_price:.2f}",
                inline=True
            )
            embed.add_field(
                name="End Price",
                value=f"${end_price:.2f}",
                inline=True
            )
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error getting history for {ticker}: {str(e)}")

async def setup(bot):
    await bot.add_cog(Stock(bot)) 