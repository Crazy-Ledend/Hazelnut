import discord
from discord.ext import commands
import aiohttp
import random
import json
import os

class Pets(commands.Cog):
    def __init__(self, bot, get_user_data, save_data):
        self.bot = bot
        self.get_user_data = get_user_data
        self.save_data = save_data
        self.pets_file = "pets.json"
        self.evolution_file = "evolution_data.json"

        # Ensure JSON files exist
        self.ensure_json_files()

    def ensure_json_files(self):
        """Ensure pets.json and evolution_data.json exist."""
        for file in [self.pets_file, self.evolution_file]:
            if not os.path.exists(file):
                with open(file, "w", encoding="utf-8") as f:
                    json.dump({}, f)

    def load_json(self, filename):
        """Safely load JSON data."""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def save_json(self, filename, data):
        """Safely save JSON data."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    async def get_pokemon_image(self, pokemon_id, shiny=False):
        """Get Pokémon sprite URL safely."""
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/"
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["sprites"]["front_shiny" if shiny else "front_default"]
        except aiohttp.ClientError:
            return None

    async def fetch_pokemon_name(self, pokemon_id):
        """Fetch Pokémon name safely."""
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/"
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["name"].capitalize()
        except aiohttp.ClientError:
            return f"Pokemon-{pokemon_id}"

    @commands.hybrid_command()
    async def pet(self, ctx, pet_name: str):
        """Interact with a pet."""
        pets = self.load_json(self.pets_file)
        user_pets = pets.get(str(ctx.author.id), {})

        if pet_name not in user_pets:
            await ctx.send("You don't have a pet with that name!")
            return

        pet = user_pets[pet_name]
        sprite_url = await self.get_pokemon_image(pet["pokemon_id"], pet["shiny"]) or ""

        embed = discord.Embed(title=f"{pet_name}", description="Interact with your pet!", color=discord.Color.green())
        embed.set_image(url=sprite_url)
        embed.add_field(name="Hunger", value=f"🍖 {pet['hunger']}/100", inline=True)
        embed.add_field(name="Happiness", value=f"😊 {pet['happiness']}/100", inline=True)
        embed.add_field(name="EXP", value=f"⭐ {pet['exp']}/100 (Lv. {pet['level']})", inline=True)

        view = discord.ui.View()

        async def feed_callback(interaction):
            if pet["hunger"] >= 100:
                await interaction.response.send_message("Your pet is full!", ephemeral=True)
                return

            pet["hunger"] = min(pet["hunger"] + 30, 100)
            pet["exp"] += random.randint(5, 10)

            self.save_json(self.pets_file, pets)

            new_embed = embed.copy()
            new_embed.set_field_at(0, name="Hunger", value=f"🍖 {pet['hunger']}/100", inline=True)
            new_embed.set_field_at(2, name="EXP", value=f"⭐ {pet['exp']}/100 (Lv. {pet['level']})", inline=True)

            await interaction.response.edit_message(embed=new_embed, view=view)

        async def pet_callback(interaction):
            pet["happiness"] = min(pet["happiness"] + 20, 100)
            pet["exp"] += random.randint(3, 7)

            self.save_json(self.pets_file, pets)

            new_embed = embed.copy()
            new_embed.set_field_at(1, name="Happiness", value=f"😊 {pet['happiness']}/100", inline=True)
            new_embed.set_field_at(2, name="EXP", value=f"⭐ {pet['exp']}/100 (Lv. {pet['level']})", inline=True)

            await interaction.response.edit_message(embed=new_embed)

        feed_button = discord.ui.Button(label="🍖 Feed", style=discord.ButtonStyle.primary)
        feed_button.callback = feed_callback
        view.add_item(feed_button)

        pet_button = discord.ui.Button(label="😊 Pet", style=discord.ButtonStyle.secondary)
        pet_button.callback = pet_callback
        view.add_item(pet_button)

        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command()
    async def adopt(self, ctx):
        """Adopt a new Pokémon."""
        pets = self.load_json(self.pets_file)
        user_pets = pets.setdefault(str(ctx.author.id), {})

        if len(user_pets) >= 2:
            await ctx.send(f"{ctx.author.mention}, you already have 2 pets! Disown one first.")
            return

        user_data = self.get_user_data(ctx.author.id)
        if user_data["wallet"] < 1000:
            await ctx.send(f"{ctx.author.mention}, you don't have enough credits (1000 required)!")
            return

        random_pokemon_id = random.randint(1, 1025)
        shiny = random.randint(1, 100) == 1

        pet_name = await self.fetch_pokemon_name(random_pokemon_id)

        # Deduct wallet balance
        user_data["wallet"] -= 1000
        self.save_data(user_data)

        user_pets[pet_name] = {
            "pokemon_id": random_pokemon_id,
            "shiny": shiny,
            "hunger": 100,
            "happiness": 50,
            "exp": 0,
            "level": 1,
        }

        self.save_json(self.pets_file, pets)
        await ctx.send(f"{ctx.author.mention} adopted **{pet_name}**! 🎉 {'✨(Shiny!)✨' if shiny else ''}")

    @commands.hybrid_command()
    async def evolve(self, ctx, pet_name: str):
        """Evolve a Pokémon if it meets the level requirement."""
        pets = self.load_json(self.pets_file)
        user_pets = pets.get(str(ctx.author.id), {})

        if pet_name not in user_pets:
            await ctx.send("You don't have a pet with that name!")
            return

        pet = user_pets[pet_name]
        evolution_data = self.load_json(self.evolution_file).get(str(pet["pokemon_id"]))

        if not evolution_data or pet["level"] < evolution_data["level_required"]:
            await ctx.send(f"{pet_name} cannot evolve or is not at the required level yet!")
            return

        pet["pokemon_id"] = evolution_data["evolves_to"]
        pet["level"] = 1
        pet["exp"] = 0

        self.save_json(self.pets_file, pets)
        await ctx.send(f"🎉 **{pet_name} has evolved!** 🎉")
        
    @commands.hybrid_command()
    async def hello(self, ctx):
        await send("*Heluuu*")

async def setup(bot):
    await bot.add_cog(Pets(bot, bot.get_user_data, bot.save_data))
