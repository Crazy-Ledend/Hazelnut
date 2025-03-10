import random
import discord
from discord.ext import commands
from discord.ui import View, Button

class SpaceExplorer(commands.Cog):
    def __init__(self, bot, get_user_data, save_data):
        self.bot = bot
        self.get_user_data = get_user_data
        self.save_data = save_data

    @commands.hybrid_command(aliases=["space"])
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def space_explorer(self, ctx):
        """Embark on a space exploration adventure! 🚀"""
        user_id = str(ctx.author.id)
        data = self.get_user_data(user_id)

        # Random rewards (100-150 credits)
        reward = random.randint(100, 150)

        # Space scenarios
        events = [
            ("🌌 You discovered a mysterious nebula!", True),
            ("👽 You encountered friendly aliens who shared advanced technology!", True),
            ("🚀 Your ship's engines failed mid-flight!", False),
            ("☄️ A meteor storm damaged your ship!", False),
            ("🪐 You landed on an uncharted planet and found rare minerals!", True),
            ("🌠 You got lost in a black hole! Escape seems impossible!", False),
            ("🛰️ You found an abandoned space station filled with valuable resources!", True),
            ("🔋 Your spaceship ran out of power. Emergency systems activated!", False),
            ("💎 You discovered a planet made of diamonds! Jackpot!", True),
            ("🎶 You intercepted a strange cosmic signal... it sounds like music!", True),
            ("👾 Hostile alien pirates attacked your ship! You barely escaped.", False),
            ("🕳️ You almost got pulled into a wormhole but managed to slingshot out!", True),
            ("🛸 A UFO appeared and abducted your crewmate! They might not return...", False),
            ("⚡ A solar flare disrupted your navigation system, sending you off course!", False),
            ("🏴‍☠️ You boarded a derelict spaceship and found an ancient treasure!", True)
        ]
        event, success = random.choice(events)

        # Space exploration embed
        embed = discord.Embed(title="🚀 Space Explorer", description="You launch into the vastness of space...", color=discord.Color.blue())
        embed.add_field(name="🔭 Scanning the cosmos...", value="Preparing for exploration...", inline=False)
        embed.set_footer(text="Make a choice below!")
        message = await ctx.send(embed=embed)

        # Interactive buttons
        class SpaceExplorerButtons(View):
            def __init__(self, data, save_data):
                super().__init__()
                self.data = data
                self.save_data = save_data

            def disable_all_buttons(self):
                """Disable buttons after selection."""
                for child in self.children:
                    child.disabled = True

            @discord.ui.button(label="Explore 🔎", style=discord.ButtonStyle.primary)
            async def explore(self, interaction: discord.Interaction, button: Button):
                if interaction.user.id != ctx.author.id:
                    return await interaction.response.send_message("You're not the explorer!", ephemeral=True)

                embed.clear_fields()
                embed.title = "🚀 Mission Report"
                embed.description = event

                if success:
                    embed.color = discord.Color.green()
                    embed.add_field(name="🎉 Success!", value=f"You earned **{reward} credits!**", inline=False)
                    self.data['wallet'] += reward
                else:
                    embed.color = discord.Color.red()
                    embed.add_field(name="💥 Mission Failed!", value="Better luck next time...", inline=False)

                self.save_data()
                self.disable_all_buttons()
                await interaction.response.edit_message(embed=embed, view=None)

        view = SpaceExplorerButtons(data, self.save_data)
        await message.edit(view=view)
        
    @commands.Cog.listener()
    async def command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Please wait for `{error.retry_after:.2f}` seconds before using this command again.")

async def setup(bot):
    get_user_data = bot.get_user_data
    save_data = bot.save_data
    await bot.add_cog(SpaceExplorer(bot, get_user_data, save_data))
