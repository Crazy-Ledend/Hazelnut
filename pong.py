import time
from datetime import timedelta
from discord.ext import commands

# Store the bot's start time
start_time = time.time()

def pong(bot):
    @bot.command()
    async def ping(ctx):
        """Ping command to check if the bot is responsive."""
        latency = round(bot.latency * 1000)  # Latency in milliseconds
        await ctx.send(f"Pong! Latency is {latency}ms.")

    @bot.command()
    async def uptime(ctx):
        """Uptime command to show how long the bot has been online."""
        uptime_duration = timedelta(seconds=int(time.time() - start_time))
        await ctx.send(f"I'm online for: {uptime_duration}")
