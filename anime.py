import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import json

ANIME_DATA_FILE = "anime_episodes.json"
AUTHORIZED_USERS = {866580615553482773, 891319231436685342}  # Anime Managers
ANNOUNCE_CHANNEL_ID = 1342816130867396689  # Announcement Channel

IMAGES = {"solo-leveling": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSDkjJOn78usAEIB-mMWP7WBTO0KH2gRnI6CA&s", "https://avatarfiles.alphacoders.com/231/231616.png", "https://www.gaminghouse.community/uploads/141-solo-leveling-release-date.png", "https://assets-prd.ignimgs.com/2024/03/19/solo-leveling-arise-button-1710874516793.jpg?width=300&crop=1%3A1%2Csmart&auto=webp", "https://wallpapers.com/images/hd/solo-leveling-sung-jin-woo-fanart-1sh29m5frnej0wpw.jpg"]}

def load_anime_data():
    try:
        with open(ANIME_DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_anime_data(data):
    with open(ANIME_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def is_authorized(self, ctx):
        return ctx.author.id in AUTHORIZED_USERS
    
    # Generate choices dynamically from JSON file
    def get_anime_choices():
        anime_list = load_anime_data()  # Load latest data
        return [app_commands.Choice(name=anime, value=anime) for anime in anime_list.keys()]
    
    @commands.hybrid_command(name="anime_update", description="Add a new anime episode link.")
    @app_commands.describe(anime_name="Name of the anime", season_number="Season number", episode_number="Episode number", episode_link="Link to the episode", episode_name="Optional episode title")
    async def anime_update(self, ctx, anime_name: str, season_number: int, episode_number: int, episode_link: str, episode_name: str = None):
        if not await self.is_authorized(ctx):
            await ctx.send("You are not authorized to use this command.", ephemeral=True)
            return

        anime_name = anime_name.lower()
        anime_data = load_anime_data()
        anime_data.setdefault(anime_name, {}).setdefault(str(season_number), {})[str(episode_number)] = {
            "name": episode_name if episode_name else f"Episode {episode_number}",
            "link": episode_link
        }
        save_anime_data(anime_data)

        embed = discord.Embed(title="Anime Episode Updated", color=discord.Color.green())
        embed.add_field(name="Anime", value=anime_name, inline=True)
        embed.add_field(name="Season", value=season_number, inline=True)
        embed.add_field(name="Episode", value=episode_number, inline=True)
        embed.add_field(name="Episode Name", value=episode_name or f"Episode {episode_number}", inline=False)
        embed.add_field(name="Link", value=episode_link, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="anime_downdate", description="Remove an anime episode link.")
    async def anime_downdate(self, ctx, anime_name: str, season_number: int, episode_number: int):
        if not await self.is_authorized(ctx):
            await ctx.send("You are not authorized to use this command.", ephemeral=True)
            return

        anime_name = anime_name.lower()
        anime_data = load_anime_data()
        season = anime_data.get(anime_name, {}).get(str(season_number), {})
        if str(episode_number) in season:
            del season[str(episode_number)]
            save_anime_data(anime_data)
            await ctx.send(f"Episode {episode_number} from {anime_name} Season {season_number} has been removed.")
        else:
            await ctx.send("Episode not found.")

    @commands.hybrid_command(name="anime_list", description="List all episodes of an anime.")
    @app_commands.choices(anime_name=get_anime_choices())  # Auto-suggest anime names
    async def anime_list(self, ctx: commands.Context, anime_name: str):
        anime_name = anime_name.lower()
        anime_data = load_anime_data()
        if anime_name not in anime_data:
            await ctx.send("No data found for this anime.")
            return
        # Get anime image if available
        image = random.choice(IMAGES.get(anime_name, [None]))
        # Create embed pages
        embeds = []
        for season_number, episodes in sorted(anime_data[anime_name].items(), key=lambda x: int(x[0]) if x[0].isdigit() else float('inf')):
            embed = discord.Embed(title=f"{anime_name.capitalize()} | Season {season_number}", color=discord.Color.blue())
            if image:
                embed.set_thumbnail(url=image)
            for episode_number, details in sorted(episodes.items(), key=lambda x: int(x[0])):
                embed.add_field(name="", value=f"<:bullet_2:1192903696737120306> **[{details['name']}]({details['link']})**", inline=False)
            embeds.append(embed)

        if not embeds:
            await ctx.send("No episodes found.")
            return
        index = 0
        # Handle slash commands properly
        if ctx.interaction:
            message = await ctx.interaction.response.send_message(embed=embeds[index], ephemeral=False)
            message = await ctx.interaction.original_response()  # Get the message object for editing
        else:
            message = await ctx.send(embed=embeds[index])  # Normal command response
        # Don't add reactions if only one season
        if len(embeds) == 1:
            return
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == message.id and reaction.emoji in ["⬅️", "➡️"]

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                if reaction.emoji == "⬅️" and index > 0:
                    index -= 1
                    await message.edit(embed=embeds[index])
                    await message.remove_reaction("⬅️", user)
                elif reaction.emoji == "➡️" and index < len(embeds) - 1:
                    index += 1
                    await message.edit(embed=embeds[index])
                    await message.remove_reaction("➡️", user)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break  # Stop listening after timeout
            
    @commands.hybrid_command(name="anime_announce", description="Announce the latest episode of an anime.")
    async def anime_announce(self, ctx, anime_name: str):
        if ctx.author.id not in AUTHORIZED_USERS:
            return await ctx.send("❌ | You do not have permission to use this command.")

        data = load_anime_data()
        anime_name = anime_name.lower()

        if anime_name not in data:
            return await ctx.send("❌ | No data found for this anime.")

        latest_season = sorted(data[anime_name].keys(), key=lambda x: int(x.split()[-1]))[-1]
        latest_episode = sorted(data[anime_name][latest_season].keys(), key=lambda x: int(x.split()[-1]))[-1]
        episode_name = data[anime_name][str(latest_season)][str(latest_episode)]
        
        channel = self.bot.get_channel(ANNOUNCE_CHANNEL_ID)
        if channel:
            embed = discord.Embed(title=f"📢 New Episode Released!", color=discord.Color.gold())
            embed.add_field(name="Anime", value=anime_name.title(), inline=True)
            embed.add_field(name="Season", value=latest_season, inline=True)
            embed.add_field(name="Episode", value=latest_episode, inline=True)
            embed.add_field(name="Title", value=f"[{episode_name['name']}]({episode_name['link']})", inline=False)
            await channel.send(embed=embed)
            await ctx.send("✅ Announcement sent!")
        else:
            await ctx.send("❌ | Announcement channel not found!")

async def setup(bot):
    await bot.add_cog(Anime(bot))
    await bot.tree.sync()
