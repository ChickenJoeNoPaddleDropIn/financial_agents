from discord.ext import commands
import discord
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import csv
from io import StringIO
import json
import glob
import pathlib

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_dotenv()
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = 'https://www.alphavantage.co/query'
        
        # Get the path relative to this file
        current_dir = pathlib.Path(__file__).parent.parent
        self.events_directory = current_dir / 'data'
        self.economic_events = {}
        
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

        self.load_events()

    def load_events(self):
        """Load economic events from all monthly JSON files"""
        try:
            # Get all JSON files in the data directory
            json_pattern = os.path.join(self.events_directory, '*_economic_events.json')
            json_files = glob.glob(json_pattern)
            
            print(f"Looking for files in: {self.events_directory}")
            print(f"Pattern searching for: {json_pattern}")
            
            if not json_files:
                print("No economic events files found")
                print(f"Directory exists: {os.path.exists(self.events_directory)}")
                if os.path.exists(self.events_directory):
                    print(f"Directory contents: {os.listdir(self.events_directory)}")
                return
            
            # Clear existing events
            self.economic_events = {}
            
            # Load and combine all JSON files
            for file_path in json_files:
                try:
                    print(f"Loading file: {file_path}")
                    with open(file_path, 'r') as f:
                        month_events = json.load(f)
                        self.economic_events.update(month_events)
                except Exception as e:
                    print(f"Error loading {file_path}: {str(e)}")
            
            if not self.economic_events:
                print("No events loaded from JSON files")
            else:
                print(f"Successfully loaded events from {len(json_files)} files")
                
        except Exception as e:
            print(f"Error loading economic events: {str(e)}")
            import traceback
            print(traceback.format_exc())
            self.economic_events = {}

    @commands.command()
    async def debug_events(self, ctx):
        """Debug command to check events loading status"""
        try:
            embed = discord.Embed(
                title="Events Debug Information",
                color=0x808080
            )
            
            embed.add_field(
                name="Events Directory",
                value=str(self.events_directory),
                inline=False
            )
            
            embed.add_field(
                name="Directory Exists",
                value=str(os.path.exists(self.events_directory)),
                inline=False
            )
            
            if os.path.exists(self.events_directory):
                files = os.listdir(self.events_directory)
                embed.add_field(
                    name="Directory Contents",
                    value="\n".join(files) if files else "Empty directory",
                    inline=False
                )
            
            embed.add_field(
                name="Loaded Events Count",
                value=str(len(self.economic_events)),
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"Error in debug: {str(e)}")
            import traceback
            print(traceback.format_exc())

    @commands.command()
    async def econ_events(self, ctx, timeframe: str = "week"):
        """Show economic events for day/week/month
        Usage: !econ_events [day|week|month]"""
        try:
            today = datetime.now().date()
            
            if timeframe.lower() == "day":
                end_date = today
                title = "Today's Economic Events"
            elif timeframe.lower() == "month":
                end_date = today + timedelta(days=30)
                title = "Economic Events - Next 30 Days"
            else:  # default to week
                end_date = today + timedelta(days=7)
                title = "Economic Events - Next 7 Days"

            embed = discord.Embed(
                title=title,
                description="Major economic events and releases",
                color=0x808080
            )

            # Filter and group events by date
            current_date = today
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                if date_str in self.economic_events:
                    events_text = ""
                    for event in self.economic_events[date_str]:
                        importance = "🔴" if event['importance'] == "High" else "🟡" if event['importance'] == "Medium" else "⚫"
                        events_text += f"{importance} {event['time']} - {event['event']}\n"
                    
                    if events_text:
                        embed.add_field(
                            name=current_date.strftime("%Y-%m-%d"),
                            value=events_text.strip(),
                            inline=False
                        )
                
                current_date += timedelta(days=1)

            if not embed.fields:
                await ctx.send(f"No economic events found for this {timeframe}.")
                return

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Error fetching economic events: {str(e)}")
            import traceback
            print(traceback.format_exc())

    @commands.command()
    async def earnings(self, ctx, timeframe: str = "week"):
        """Get earnings calendar events for day/week/month
        Usage: !earnings [day|week|month]"""
        try:
            today = datetime.now().date()
            
            if timeframe.lower() == "day":
                days = 1
                title = "Today's Earnings Calendar"
            elif timeframe.lower() == "month":
                days = 30
                title = "Earnings Calendar - Next 30 Days"
            else:  # default to week
                days = 7
                title = "Earnings Calendar - Next 7 Days"

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
                await ctx.send(f"No major index earnings events found for this {timeframe}.")
                return

            current_embed = discord.Embed(
                title=title,
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
        await self.earnings(ctx, "day")

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