from discord.ext import commands
import random
import asyncio

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx, dice: str = "1d20"):
        """Roll some dice! Format: NdM (e.g., 2d6)"""
        try:
            rolls, limit = map(int, dice.split('d'))
            if rolls > 100:  # Prevent spam
                await ctx.send("I can't roll that many dice!")
                return
            result = [str(random.randint(1, limit)) for r in range(rolls)]
            await ctx.send(f'🎲 Results: {", ".join(result)}')
        except Exception:
            await ctx.send('Format has to be in NdM! (e.g., 2d6)')

    @commands.command()
    async def flip(self, ctx):
        """Flip a coin!"""
        result = random.choice(['Heads', 'Tails'])
        await ctx.send(f'🪙 {result}!')

    @commands.command()
    async def rps(self, ctx, choice: str = None):
        """Play Rock, Paper, Scissors!"""
        options = ['rock', 'paper', 'scissors']
        if choice is None or choice.lower() not in options:
            await ctx.send('Please choose rock, paper, or scissors!')
            return
            
        bot_choice = random.choice(options)
        choice = choice.lower()
        
        if choice == bot_choice:
            result = "It's a tie!"
        elif (choice == 'rock' and bot_choice == 'scissors') or \
             (choice == 'paper' and bot_choice == 'rock') or \
             (choice == 'scissors' and bot_choice == 'paper'):
            result = "You win!"
        else:
            result = "I win!"
            
        await ctx.send(f'You chose {choice}, I chose {bot_choice}. {result}')

async def setup(bot):
    await bot.add_cog(Fun(bot))
