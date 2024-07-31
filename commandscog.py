from discord.ext import commands        

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="in")
    async def add(self, ctx, *args):
        # Your add command logic here
        await ctx.send("Add command executed!")

    @commands.command(name="out")
    async def remove(self, ctx, *args):
        # Your remove command logic here
        await ctx.send("Remove command executed!")