import discord
from discord.ext import commands

class info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="servers", description="Displays the servers with Hazelnut.")
    async def servers(self, ctx):
        embed = discord.Embed(title=f"Servers with Hazelnut!",color=discord.Colour(0xcd974f))
        embed.add_field(name=f"", value = f"Hazelnut is currently in `{len(ctx.bot.guilds)}` servers", inline=False)
        for guild in ctx.bot.guilds:
            embed.add_field(name=f"", value = f"<a:bulletin:1338881198700761109> **{guild.name}** - (members: `{guild.member_count}`)", inline=False)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="info", description="Displays the basic information about the bot")
    async def info(self, ctx):
        embed = discord.Embed(title=f"Statistics",color=discord.Colour(0xcd974f))
        embed.add_field(name=f"<:info:1338897881414893749> __Details__", value = f"<:d3:1338913909213495347> **Owner:** crazypokeking\n<:d1:1338913912351101029> \n<:d3:1338913909213495347> **Developers:** crazypokeking\n<:d1:1338913912351101029> \n<:d3:1338913909213495347> **Web Developer:** crazypokeking\n<:d1:1338913912351101029> \n<:d3:1338913909213495347> **Dev. Helpers:** --\n<:d1:1338913912351101029> \n<:d3:1338913909213495347> **Server count:** `{len(ctx.bot.guilds)}`\n<:d1:1338913912351101029> \n<:d2:1338913906684334121> **Discord Version:** `{discord.__version__}`", inline=False)
        embed.add_field(name=f"<:links:1338897157843062916> __Links__", value = f"<a:dev:1337793382428180510> | crazypokeking \n\n \
<a:Discord:1337791992217997383> | https://discord.gg/WxvEhxG5Q5 \n\n \
<:website:1337793532945240104> | https://crazy-ledend.github.io/Hazelnut-web/", inline=False)
        await ctx.send(embed=embed)
    
async def setup(bot):
    await bot.add_cog(info(bot))