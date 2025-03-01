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
import sys
from pathlib import Path
from utils.forex_scraper import scrape_forex_factory, event_cache

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_events()

    def load_events(self):
        """Load or refresh economic events"""
        success = scrape_forex_factory()
        if not success:
            print("Failed to load economic events")

    def get_events_for_date(self, target_date, currency=None):
        """Helper to get events for a specific date with optional currency filter"""
        date_str = target_date.strftime('%Y-%m-%d')
        events = event_cache.get_events_for_date(date_str)
        
        if currency:
            events = [e for e in events if e['currency'] == currency]
        
        print(f"\nDebug: Found {len(events)} events for {date_str}")
        for event in events:
            print(f"  {event['time']} {event['currency']} - {event['event']} (Impact: {event['importance']})")
        
        return events

    @commands.command(name='day')
    async def day_events(self, ctx, *args):
        """Show economic events for a specific day"""
        try:
            # Parse arguments
            offset = 0
            currency = "USD"
            
            for arg in args:
                if arg.lstrip('-').isdigit():
                    offset = int(arg)
                else:
                    currency = arg.upper()

            target_date = datetime.now().date() + timedelta(days=offset)
            
            print(f"\n=== Debug: day command ===")
            print(f"Target date: {target_date}")
            print(f"Offset: {offset}")
            print(f"Currency: {currency}")
            
            events = self.get_events_for_date(target_date, currency)
            
            if not events:
                currency_text = f"{currency} " if currency else ""
                await ctx.send(f"No {currency_text}economic events found for {target_date.strftime('%A, %B %d')}.")
                return

            # Format and send embed
            title = f"📅 Economic Events - {target_date.strftime('%A, %B %d')}"
            description = f"{'USD Only' if currency == 'USD' else f'{currency} Only' if currency else 'All Currencies'}"
            
            embed = discord.Embed(title=title, description=description, color=0x00ff00)
            
            # Sort and format events
            events_text = ""
            for event in self.sort_events(events):
                importance_emoji = "🔴" if event['importance'] == "High" else "🟡" if event['importance'] == "Medium" else "⚫"
                events_text += f"{importance_emoji} {event['time']} {event['currency']} - {event['event']}\n"

            embed.add_field(name="Events", value=events_text.strip(), inline=False)
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Error fetching daily events: {str(e)}")
            import traceback
            print(traceback.format_exc())

    @commands.command(name='week')
    async def week_events(self, ctx, currency: str = "USD"):
        """Show economic events for the week"""
        try:
            today = datetime.now().date()
            start_date = today - timedelta(days=today.weekday())  # Monday
            end_date = start_date + timedelta(days=4)  # Friday
            
            print(f"\n=== Debug: week command ===")
            print(f"Start date: {start_date}")
            print(f"End date: {end_date}")
            print(f"Currency: {currency}")
            
            events = {}
            current_date = start_date
            while current_date <= end_date:
                day_events = self.get_events_for_date(current_date, currency)
                # Only include days with medium/high impact events
                important_events = [e for e in day_events if e['importance'] in ['High', 'Medium']]
                if important_events:
                    events[current_date.strftime('%Y-%m-%d')] = important_events
                current_date += timedelta(days=1)
            
            if not events:
                await ctx.send(f"No important economic events found for this week.")
                return

            # Format and send embed
            title = "📅 Important Economic Events - This Week"
            description = f"{start_date.strftime('%A, %B %d')} to {end_date.strftime('%A, %B %d')}\n"
            description += f"{'USD Only' if currency == 'USD' else f'{currency} Only' if currency else 'All Currencies'}"
            
            embed = discord.Embed(title=title, description=description, color=0x00ff00)
            
            for date_str, day_events in sorted(events.items()):
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                events_text = ""
                for event in self.sort_events(day_events):
                    importance_emoji = "🔴" if event['importance'] == "High" else "🟡" if event['importance'] == "Medium" else "⚫"
                    events_text += f"{importance_emoji} {event['time']} {event['currency']} - {event['event']}\n"
                
                if events_text:
                    embed.add_field(
                        name=date_obj.strftime("%A, %B %d"),
                        value=events_text.strip(),
                        inline=False
                    )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Error fetching weekly events: {str(e)}")
            import traceback
            print(traceback.format_exc())

    @commands.command(name='month')
    async def month_events(self, ctx, currency: str = "USD"):
        """Show economic events for the month"""
        try:
            today = datetime.now().date()
            current_month = event_cache.get_month('current_month')
            
            print(f"\n=== Debug: month command ===")
            print(f"Current month: {today.strftime('%B %Y')}")
            print(f"Currency: {currency}")
            
            events = {}
            for date_str, day_events in current_month.items():
                if currency.upper() != "ALL":
                    day_events = [e for e in day_events if e['currency'] == currency.upper()]
                important_events = [e for e in day_events if e['importance'] in ['High', 'Medium']]
                if important_events:
                    events[date_str] = important_events
            
            if not events:
                await ctx.send(f"No important economic events found for this month.")
                return

            # Format and send embed
            title = f"📅 Important Economic Events - {today.strftime('%B')}"
            description = f"{'USD Only' if currency == 'USD' else f'{currency} Only' if currency else 'All Currencies'}"
            
            embed = discord.Embed(title=title, description=description, color=0x00ff00)
            
            for date_str, day_events in sorted(events.items()):
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                events_text = ""
                for event in self.sort_events(day_events):
                    importance_emoji = "🔴" if event['importance'] == "High" else "🟡" if event['importance'] == "Medium" else "⚫"
                    events_text += f"{importance_emoji} {event['time']} {event['currency']} - {event['event']}\n"
                
                if events_text:
                    embed.add_field(
                        name=date_obj.strftime("%A, %B %d"),
                        value=events_text.strip(),
                        inline=False
                    )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Error fetching monthly events: {str(e)}")
            import traceback
            print(traceback.format_exc())

    def sort_events(self, events):
        """Sort events by time and importance"""
        def get_sort_key(event):
            time_str = event['time'].lower()
            
            # Define priority order
            if time_str == "all day":
                return (0, event['importance'])
            elif time_str == "tentative":
                return (999999, event['importance'])
            
            try:
                # Handle times in original format
                if ':' in time_str:
                    hour = int(time_str.split(':')[0])
                    minute = int(time_str.split(':')[1][:2])  # Handle "8:30am" format
                    if 'pm' in time_str and hour != 12:
                        hour += 12
                    return (hour * 60 + minute, event['importance'])
            except ValueError:
                return (999999, event['importance'])
            
            return (999999, event['importance'])
        
        return sorted(events, key=get_sort_key)

    @commands.command(name='debug_cache')
    async def debug_cache(self, ctx):
        """Debug command to show what's in the cache"""
        try:
            embed = discord.Embed(title="Cache Debug Info", color=0x808080)
            
            for month_key in ['previous_month', 'current_month', 'next_month']:
                month_data = event_cache.get_month(month_key)
                dates = sorted(month_data.keys())
                if dates:
                    first_date = dates[0]
                    last_date = dates[-1]
                    total_events = sum(len(events) for events in month_data.values())
                    embed.add_field(
                        name=month_key,
                        value=f"Dates: {first_date} to {last_date}\nTotal events: {total_events}",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name=month_key,
                        value="No events stored",
                        inline=False
                    )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"Error in debug: {str(e)}")
            import traceback
            print(traceback.format_exc())

async def setup(bot):
    await bot.add_cog(Economy(bot)) 