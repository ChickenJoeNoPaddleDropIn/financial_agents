from discord.ext import commands
import discord
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import csv
from io import StringIO

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_dotenv()
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = 'https://www.alphavantage.co/query'
        
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

    @commands.command()
    async def calendar(self, ctx, days: int = 7):
        """Get earnings calendar events for the next N days
        Usage: !calendar [days]"""
        try:
            url = f'{self.base_url}?function=EARNINGS_CALENDAR&horizon=3month&apikey={self.api_key}'
            
            response = requests.get(url)
            if response.status_code != 200:
                await ctx.send(f"Error fetching data: {response.status_code}")
                return

            csv_data = StringIO(response.text)
            reader = csv.DictReader(csv_data)
            events = list(reader)

            today = datetime.now().date()
            end_date = today + timedelta(days=days)
            
            # Group events by date
            date_groups = {}
            for event in events:
                # Filter for major index stocks only
                if event['symbol'] not in self.major_stocks:
                    continue
                
                event_date = datetime.strptime(event['reportDate'], '%Y-%m-%d').date()
                if today <= event_date <= end_date:
                    if event_date not in date_groups:
                        date_groups[event_date] = []
                    date_groups[event_date].append(event)

            if not date_groups:
                await ctx.send("No major index earnings events found for this period.")
                return

            current_embed = discord.Embed(
                title=f"📅 Major Index Earnings Calendar - Next {days} Days",
                description="Showing earnings for major S&P 500, NASDAQ-100, and Dow Jones companies",
                color=0x00ff00
            )
            
            for date in sorted(date_groups.keys()):
                date_events = ""
                for event in sorted(date_groups[date], key=lambda x: x['symbol']):
                    event_text = f"• {event['name']} ({event['symbol']})\n"
                    if event.get('estimate'):
                        event_text += f"  Est. EPS: ${event['estimate']}\n"
                    event_text += "\n"
                    
                    if len(date_events + event_text) > 1024:
                        current_embed.add_field(
                            name=date.strftime("%Y-%m-%d"),
                            value=date_events.strip(),
                            inline=False
                        )
                        date_events = event_text
                    else:
                        date_events += event_text

                if date_events:
                    current_embed.add_field(
                        name=date.strftime("%Y-%m-%d"),
                        value=date_events.strip(),
                        inline=False
                    )

            await ctx.send(embed=current_embed)

        except Exception as e:
            await ctx.send(f"Error fetching calendar data: {str(e)}")
            import traceback
            print(traceback.format_exc())

    @commands.command()
    async def today(self, ctx):
        """Get today's major index earnings reports"""
        await self.calendar(ctx, days=1)

    @commands.command()
    async def components(self, ctx):
        """Show the number of index components being tracked"""
        message = (
            f"Currently tracking {len(self.major_stocks)} major companies:\n"
            f"• S&P 500 components: {len(self.sp500_stocks)}\n"
            f"• Additional NASDAQ-100: {len(self.nasdaq100_additional)}\n"
            f"• Additional Dow 30: {len(self.dow30_additional)}"
        )
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(Economy(bot)) 