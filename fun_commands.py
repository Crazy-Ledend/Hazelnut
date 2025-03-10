import discord
from discord.ext import commands
import random
import json

OWNER_ID = 891319231436685342

# Load the GIFs
def load_gifs():
    try:
        with open('gif_list.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("GIF file not found!")
        return {}

# Predefined GIF lists
GIF_LISTS = load_gifs()

# Helper function to get a random GIF from the predefined list
def get_random_gif(action):
    """Fetch a random GIF from the predefined list."""
    if action in GIF_LISTS:
        return random.choice(GIF_LISTS[action])
    return "https://64.media.tumblr.com/46c25b37ac3a4672fa97d54a5ecf9005/tumblr_oez2n47I2v1udouqko1_500.gif"  # Fallback gif

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pat")
    async def pat(self, ctx, member: discord.Member = None):
        """Pat a user"""
        await self.generic_command(ctx, member, "pat")

    @commands.command(name="hug")
    async def hug(self, ctx, member: discord.Member = None):
        """Hug a user"""
        await self.generic_command(ctx, member, "hug")

    @commands.command(name="slap")
    async def slap(self, ctx, member: discord.Member = None):
        """Slap a user"""
        await self.generic_command(ctx, member, "slap")

    @commands.command(name="kiss")
    async def kiss(self, ctx, member: discord.Member = None):
        """Kiss a user"""
        await self.generic_command(ctx, member, "kiss")

    @commands.command(name="cuddle")
    async def cuddle(self, ctx, member: discord.Member = None):
        """Cuddle a user"""
        await self.generic_command(ctx, member, "cuddle")

    @commands.command(name="wave")
    async def wave(self, ctx, member: discord.Member = None):
        """Wave at a user"""
        await self.generic_command(ctx, member, "wave")

    @commands.command(name="kick")
    async def kick(self, ctx, member: discord.Member = None):
        """Kick a user"""
        await self.generic_command(ctx, member, "kick")

    @commands.command(name="kill")
    async def kill(self, ctx, member: discord.Member = None):
        """Kill a user"""
        await self.generic_command(ctx, member, "kill")

    @commands.command(name="stab")
    async def stab(self, ctx, member: discord.Member = None):
        """Stab a user"""
        await self.generic_command(ctx, member, "stab")

    @commands.command(name="lick")
    async def lick(self, ctx, member: discord.Member = None):
        """Lick a user"""
        await self.generic_command(ctx, member, "lick")

    @commands.command(name="punch")
    async def punch(self, ctx, member: discord.Member = None):
        """Punch a user"""
        await self.generic_command(ctx, member, "punch")

    @commands.command(name="bite")
    async def bite(self, ctx, member: discord.Member = None):
        """Bite a user"""
        await self.generic_command(ctx, member, "bite")

    @commands.command(name="sniff")
    async def sniff(self, ctx, member: discord.Member = None):
        """Sniff a user"""
        await self.generic_command(ctx, member, "sniff")

    def is_owner(self, user_id):
        """Check if the user is the bot owner."""
        return user_id == OWNER_ID

    async def generic_command(self, ctx, member, action):
        """Generic handler for fun commands."""
        if member != None and member.id == 1295047885494292502:
            await ctx.send("*Shoo! You can't do that to my dear! ~Crazy*")
            return 
        
        if member is None and not self.is_owner(ctx.author.id):
            await ctx.send("*Shoo! You can't do that to my dear! ~Crazy*")
            return
        
        target = member.display_name if member else self.bot.user.display_name 
        gif_url = get_random_gif(action)

        # Define message body based on the action
        body = ''
        if action == 'hug':
            body = 'ged'
        elif action == 'slap':
            body = 'ped'
        elif action == 'cuddle':
            body = 'd with'
        elif action == 'wave':
            body = 'd at'
        elif action in ['kick', 'kill', 'punch', 'lick', 'kiss']:
            body = 'ed'
        elif action == 'stab':
            body = 'bed'
        elif action in ['bite', 'sniff', 'pat']:
            body = 's'

        # Send the embed message with the gif
        embed = discord.Embed(
            title=f"{ctx.author.display_name} {action}{body} {target}!",
            color=discord.Color.random()
        )
        embed.set_image(url=gif_url)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")

        await ctx.send(embed=embed)

# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(FunCommands(bot))
