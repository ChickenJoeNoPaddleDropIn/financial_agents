from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        """Says hello to the user"""
        await ctx.send(f'Hello {ctx.author.name}!')
    
    @commands.command()
    async def ping(self, ctx):
        """Check bot's latency"""
        await ctx.send(f'Pong! Latency: {round(self.bot.latency * 1000)}ms')

async def setup(bot):
    await bot.add_cog(General(bot))
