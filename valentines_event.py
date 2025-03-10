import discord
import random
import asyncio
import numpy as np
from discord.ext import commands

class ValentineActivity(commands.Cog):
    def __init__(self, bot, get_user_data, save_data):
        self.bot = bot
        self.get_user_data = get_user_data
        self.save_data = save_data
        self.message_counts = {}  # Tracks message count per user

    async def spawn_valentine_embed(self, message):
        """Spawns a themed love letter event."""
        user = message.author
        channel = message.channel

        image_paths = {
            "Empress": "valentine/empress.png",
            "Mermaid": "valentine/mermaid.png",
            "Angel": "valentine/angel.png"
        }

        # Using NumPy for random selections
        women = np.array(["Empress", "Mermaid", "Angel"])
        woman = np.random.choice(women)
        image_path = image_paths[woman]

        descriptions = np.array([
            f"A Love Letter, kissed by the moonlight, finds its way to you—sent by the {woman}! 💌 Will you accept its call?",
            f"Nestled between rose petals, a {woman} has left behind a Love Letter just for you! 💌 Dare to read its whispered words?",
            f"As the night air hums with desire, a Love Letter appears—sealed with longing by the {woman}! 💌 Let it steal your heart.",
            f"The {woman} has woven her emotions into ink and paper, crafting a Love Letter just for you! 💌 Do you dare open it?",
            f"A breeze carries the scent of perfume and ink—a Love Letter from a {woman} flutters into your hands! 💌 Read it before it fades!",
            f"Bathed in candlelight, a Love Letter trembles with untold emotions, penned by the {woman}! 💌 Will you hold it close?",
            f"A {woman} has poured her heart onto this Love Letter, every word dripping with devotion! 💌 Will you be the one to answer?",
            f"Between the pages of fate, a Love Letter from the {woman} waits for your touch! 💌 Let its words embrace your soul.",
            f"Under the silver glow of the stars, a {woman} has sent you a Love Letter! 💌 Will you let her words wrap around your heart?",
            f"The {woman} has sent you a Love Letter, every word laced with passion! 💌 Read it, and feel the fire of her longing.",
            f"In the hush of the evening, a {woman} whispers through ink and parchment—a Love Letter written just for you! 💌 Will you answer her call?",
            f"A single red wax seal binds this Love Letter, hiding the desires of the {woman}! 💌 Dare you break the seal?",
            f"As music drifts through the air, a {woman} has left you a Love Letter! 💌 Will you dance with her words?",
            f"The {woman} has stolen a piece of her soul and wrapped it in ink—a Love Letter awaits! 💌 Will you claim her heart?",
            f"In a moment of fearless passion, a {woman} has sent you a Love Letter! 💌 Will you surrender to its romance?"
        ])
        adjectives = np.array(["Gorgeous", "Cute", "Lovely", "Mysterious", "Kind", "Hot", "Beautiful"])
        actions = np.array([
            "whispers your name", "calls out softly", "leaves a love note",
            "gazes longingly", "smiles mysteriously", "steps into moonlight",
            "vanishes in mist", "sends a soft sigh", "waits under starlight",
            "paints dreams in air", "writes in the wind", "drapes night in longing",
            "leaves roses behind", "glances your way", "disappears in twilight"
        ])

        # Generate embed message
        file = discord.File(image_path, filename=image_path.split("/")[-1])
        image_url = f"attachment://{image_path.split('/')[-1]}"

        embed = discord.Embed(
            title=f"A {np.random.choice(adjectives)} {woman} {np.random.choice(actions)}",
            description=f"{np.random.choice(descriptions)}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Hurry! This love letter will disappear in a few seconds!")
        embed.set_thumbnail(url=image_url)

        view = ValentineButton(self.get_user_data, self.save_data, woman, channel)

        msg = await channel.send(embed=embed, view=view, file=file)

        await asyncio.sleep(20)  # Wait for 20 seconds
        await msg.delete()

        await view.send_rewards_summary()

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listens for messages and spawns a love letter embed after 20-25 messages."""
        if message.author.bot:
            return

        user_id = message.author.id
        self.message_counts[user_id] = self.message_counts.get(user_id, 0) + 1

        if self.message_counts[user_id] >= np.random.randint(20, 26):  # Trigger event
            self.message_counts[user_id] = 0  # Reset counter
            await self.spawn_valentine_embed(message)

class ValentineButton(discord.ui.View):
    def __init__(self, get_user_data, save_data, woman, channel):
        super().__init__(timeout=20)
        self.get_user_data = get_user_data
        self.save_data = save_data
        self.click_counts = {}
        self.theme = woman
        self.channel = channel

    @discord.ui.button(label="Love Letter", emoji="💖", style=discord.ButtonStyle.red)
    async def love_letter_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handles button clicks and immediately distributes rewards."""
        user_id = interaction.user.id
        user_name = interaction.user.display_name

        self.click_counts[user_id] = self.click_counts.get(user_id, {"name": user_name, "clicks": 0})
        self.click_counts[user_id]["clicks"] += 1
        clicks = self.click_counts[user_id]["clicks"]

        user_data = self.get_user_data(user_id)

        # Reward logic
        if clicks <= 10:
            reward = np.random.randint(10, 15)
            user_data["wallet"] += reward
            reward_text = f"**{reward} credits**"
        elif clicks <= 15:
            reward = np.random.randint(1, 3)
            item = np.random.choice(["rose", "pink-rose"])
            user_data.setdefault("inventory", {}).setdefault(item, 0)
            user_data["inventory"][item] = user_data["inventory"].get(item, 0) + reward
            reward_text = f"**{reward} {item}(s)**"
        elif clicks <= 20:
            reward = np.random.randint(1, 2)
            item = "love-letter"
            user_data.setdefault("inventory", {}).setdefault(item, 0)
            user_data["inventory"][item] = user_data["inventory"].get(item, 0) + reward
            reward_text = f"**{reward} {item}(s)**"
        else:
            reward = np.random.randint(0, 2)
            item = "valentines-box"
            user_data.setdefault("inventory", {}).setdefault(item, 0)
            user_data["inventory"][item] = user_data["inventory"].get(item, 0) + reward
            reward_text = f"**{reward} {item}(s)**"

        self.save_data()

        await interaction.response.send_message(f"💖 You've clicked the **Love Letter** from {self.theme} {clicks} times! Your reward: {reward_text}", ephemeral=True)

        await asyncio.sleep(3)
        try:
            await interaction.delete_original_response()
        except discord.errors.NotFound:
            pass  # Ignore if already deleted

    async def send_rewards_summary(self):
        """Sends an embed stating that all rewards have been handed out."""
        embed = discord.Embed(
            title="💌 All rewards have been handed out!",
            description="Here's how many times you've clicked:",
            color=discord.Color.red()
        )

        for user_id, data in self.click_counts.items():
            user_name = data["name"]
            clicks = data["clicks"]
            reward_text = f"{clicks} clicks"

            embed.add_field(name=user_name, value=reward_text, inline=False)

        await self.channel.send(embed=embed)

async def setup(bot):
    get_user_data = bot.get_user_data  
    save_data = bot.save_data  
    await bot.add_cog(ValentineActivity(bot, get_user_data, save_data))
