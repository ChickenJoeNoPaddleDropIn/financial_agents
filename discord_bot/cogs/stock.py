from discord.ext import commands
import yfinance as yf
import discord
from datetime import datetime, timedelta
import pandas as pd
from utils.rate_limiting import RateLimitedCache

class Stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = RateLimitedCache(cache_ttl=300, min_delay=2.0)  # 5 min cache, 2s delay

    def _get_stock_info(self, ticker):
        """Get stock info with caching and rate limiting"""
        # Check cache first
        cached_info = self.cache.get(ticker)
        if cached_info is not None:
            return cached_info

        # If not in cache or expired, fetch new data
        stock = yf.Ticker(ticker)
        try:
            info = {
                'price': stock.info.get('regularMarketPrice'),
                'high': stock.info.get('dayHigh'),
                'low': stock.info.get('dayLow'),
                'volume': stock.info.get('volume'),
                'name': stock.info.get('shortName', ticker.upper())
            }
            # Store in cache
            self.cache.set(ticker, info)
            return info
        except Exception as e:
            print(f"Error fetching {ticker}: {str(e)}")
            return None

    @commands.command()
    async def price(self, ctx, ticker: str):
        """Get current price of a stock
        Usage: !price AAPL"""
        try:
            info = self._get_stock_info(ticker)
            if not info or not info['price']:
                await ctx.send(f"Unable to get price data for {ticker}. Please try again later.")
                return
                
            await ctx.send(f"💰 {info['name']}: ${info['price']:.2f}")
        except Exception as e:
            await ctx.send(f"Error getting price for {ticker}: {str(e)}")
            import traceback
            print(traceback.format_exc())

    @commands.command()
    async def summary(self, ctx, ticker: str):
        """Get a quick summary of a stock
        Usage: !summary AAPL"""
        try:
            info = self._get_stock_info(ticker)
            if not info or not info['price']:
                await ctx.send(f"Unable to get data for {ticker}. Please try again later.")
                return
            
            embed = discord.Embed(
                title=f"{info['name']} ({ticker.upper()}) Summary", 
                color=0x808080
            )
            
            embed.add_field(
                name="Current Price", 
                value=f"${info['price']:.2f}", 
                inline=True
            )
            
            if info['high']:
                embed.add_field(
                    name="Day High",
                    value=f"${info['high']:.2f}",
                    inline=True
                )
            if info['low']:
                embed.add_field(
                    name="Day Low",
                    value=f"${info['low']:.2f}",
                    inline=True
                )
            if info['volume']:
                embed.add_field(
                    name="Volume",
                    value=f"{info['volume']:,}",
                    inline=True
                )
            
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
            if days > 30:
                await ctx.send("Please request 30 days or fewer!")
                return
            
            # Use a different cache key for historical data
            cache_key = f"{ticker}_history_{days}"
            cached_hist = self.cache.get(cache_key)
            
            if cached_hist is not None:
                hist = cached_hist
            else:
                stock = yf.Ticker(ticker)
                hist = stock.history(period=f"{days}d")
                self.cache.set(cache_key, hist)
            
            if hist.empty:
                await ctx.send(f"No historical data available for {ticker}")
                return
            
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            change = ((end_price - start_price) / start_price) * 100
            
            embed = discord.Embed(
                title=f"{ticker.upper()} {days}-Day History",
                color=0x808080
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
            import traceback
            print(traceback.format_exc())

async def setup(bot):
    await bot.add_cog(Stock(bot)) 