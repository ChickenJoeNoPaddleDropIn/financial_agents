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
        
        # Pre-compiled list of major index components
        self.sp500_stocks = {
            # FAANG + Microsoft + Nvidia + Tesla
            'AAPL', 'AMZN', 'GOOGL', 'GOOG', 'META', 'NFLX', 'MSFT', 'NVDA', 'TSLA',
            
            # Financial Services
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'BLK', 'V', 'MA', 'AXP', 'C', 'SCHW',
            'USB', 'PNC', 'TFC', 'COF', 'BK',
            
            # Technology
            'AMD', 'INTC', 'CSCO', 'ORCL', 'CRM', 'ADBE', 'AVGO', 'QCOM', 'TXN',
            'PYPL', 'SQ', 'NOW', 'INTU', 'AMAT', 'MU', 'KLAC', 'ADI', 'LRCX',
            
            # Healthcare
            'JNJ', 'UNH', 'PFE', 'ABBV', 'MRK', 'LLY', 'TMO', 'ABT', 'BMY', 'AMGN',
            'CVS', 'CI', 'HUM', 'GILD', 'REGN', 'VRTX', 'ISRG', 'MDT', 'DHR',
            
            # Consumer
            'WMT', 'PG', 'KO', 'PEP', 'COST', 'MCD', 'DIS', 'SBUX', 'NKE', 'HD',
            'LOW', 'TGT', 'BKNG', 'ABNB', 'MAR', 'YUM', 'MO', 'PM', 'EL', 'CL',
            
            # Industrial & Energy
            'XOM', 'CVX', 'BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'FDX', 'RTX',
            'LMT', 'GD', 'DE', 'EMR', 'ETN', 'WM', 'ADP', 'COP', 'SLB', 'EOG',
            
            # Communications & Media
            'VZ', 'T', 'CMCSA', 'TMUS', 'CHTR', 'ATVI', 'EA', 'NFLX', 'PARA', 'DIS',
            
            # Financial Tech & Payment
            'PYPL', 'SQ', 'COIN', 'AFRM', 'HOOD',
            
            # Retail & E-commerce
            'AMZN', 'WMT', 'TGT', 'COST', 'HD', 'LOW', 'ETSY', 'EBAY',
            
            # Automotive
            'TSLA', 'F', 'GM', 'RIVN', 'LCID',
            
            # Others
            'BRK.B', 'UBER', 'LYFT', 'ZM', 'DASH', 'SNAP', 'PINS', 'TWTR', 'SPOT'
        }

        self.nasdaq100_additional = {
            'ASML', 'TSM', 'MRVL', 'PANW', 'SNPS', 'CDNS', 'WDAY', 'TEAM',
            'DDOG', 'ZS', 'CRWD', 'FTNT', 'LULU', 'MELI', 'ILMN', 'IDXX',
            'MRNA', 'ALGN', 'ODFL', 'ADSK', 'CPRT', 'KDP', 'MNST', 'PCAR',
            'PDD', 'JD', 'BIDU', 'NTES', 'DLTR', 'ROST', 'FAST', 'PAYX'
        }

        self.dow30_additional = {
            'TRV', 'DOW', 'WBA', 'CRM'  # Any not already in SP500 list
        }

        # Combine all indices
        self.major_stocks = self.sp500_stocks | self.nasdaq100_additional | self.dow30_additional

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

    @commands.command()
    async def list_components(self, ctx, index: str = "all"):
        """List components of major indices
        Usage: !list_components [sp500|nasdaq|dow|all]"""
        try:
            index = index.lower()
            
            if index not in ["sp500", "nasdaq", "dow", "all"]:
                await ctx.send("Please specify a valid index: sp500, nasdaq, dow, or all")
                return
            
            embeds = []
            
            if index in ["sp500", "all"]:
                # SP500 components by sector
                sp500_embed = discord.Embed(
                    title="S&P 500 Components by Sector",
                    color=0x808080
                )
                
                # FAANG + Tech Leaders
                sp500_embed.add_field(
                    name="FAANG + Tech Leaders",
                    value="• " + "\n• ".join(sorted([s for s in self.sp500_stocks if s in {
                        'AAPL', 'AMZN', 'GOOGL', 'GOOG', 'META', 'NFLX', 'MSFT', 'NVDA', 'TSLA'
                    }])),
                    inline=False
                )
                
                # Financial Services
                financials = sorted([s for s in self.sp500_stocks if s in {
                    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'BLK', 'V', 'MA', 'AXP', 'C', 'SCHW',
                    'USB', 'PNC', 'TFC', 'COF', 'BK'
                }])
                if financials:
                    sp500_embed.add_field(
                        name="Financial Services",
                        value="• " + "\n• ".join(financials),
                        inline=False
                    )
                
                # Technology
                tech = sorted([s for s in self.sp500_stocks if s in {
                    'AMD', 'INTC', 'CSCO', 'ORCL', 'CRM', 'ADBE', 'AVGO', 'QCOM', 'TXN',
                    'PYPL', 'SQ', 'NOW', 'INTU', 'AMAT', 'MU', 'KLAC', 'ADI', 'LRCX'
                }])
                if tech:
                    sp500_embed.add_field(
                        name="Technology",
                        value="• " + "\n• ".join(tech),
                        inline=False
                    )
                
                embeds.append(sp500_embed)
            
            if index in ["nasdaq", "all"]:
                # NASDAQ additional components
                nasdaq_embed = discord.Embed(
                    title="Additional NASDAQ-100 Components",
                    description="Components not already in S&P 500",
                    color=0x808080
                )
                
                if self.nasdaq100_additional:
                    nasdaq_embed.add_field(
                        name="Components",
                        value="• " + "\n• ".join(sorted(self.nasdaq100_additional)),
                        inline=False
                    )
                
                embeds.append(nasdaq_embed)
            
            if index in ["dow", "all"]:
                # DOW additional components
                dow_embed = discord.Embed(
                    title="Additional Dow 30 Components",
                    description="Components not already in S&P 500",
                    color=0x808080
                )
                
                if self.dow30_additional:
                    dow_embed.add_field(
                        name="Components",
                        value="• " + "\n• ".join(sorted(self.dow30_additional)),
                        inline=False
                    )
                
                embeds.append(dow_embed)
            
            # Send all embeds
            for embed in embeds:
                await ctx.send(embed=embed)
                
        except Exception as e:
            await ctx.send(f"Error listing components: {str(e)}")
            import traceback
            print(traceback.format_exc())

async def setup(bot):
    await bot.add_cog(Stock(bot)) 