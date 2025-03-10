import discord
from discord.ext import commands
from discord.ui import Select, View
import admin_commands
import embed as em

def help_commands(bot):
    @bot.command(name="guide", aliases=["help"])
    async def help(ctx):
        # Embed for dropdown explanation
        embed = discord.Embed(
            title="Command Guide",
            description="Use the dropdown below to view categorized help sections.",
            color=int(em.embed(), 16)
        )
        # Send the embed with the image
        file = discord.File("help_desk.jpeg", filename="help_desk.jpeg")
        embed.set_image(url="attachment://help_desk.jpeg")

        # Dropdown Menu
        options = [
            discord.SelectOption(label="Credits", description="Learn about credits and related commands", emoji="<:dGem:1312309674011525150>"),
            discord.SelectOption(label="Minigames", description="Discover fun minigames to play", emoji="<a:minigames:1312298010549555270>"),
            discord.SelectOption(label="CryoStock Trading", description="Helps you understand CryoStocks", emoji="<a:Stocks:1328040520374550633>"),
            discord.SelectOption(label="Term Integration", description="A Virtual dictionary for the bot's terms", emoji="<a:Dictionary:1328048949617229968>"),
            discord.SelectOption(label="Fun & Utility", description="Have fun with the interactive commands!", emoji="<a:Fun:1328041308375220305>"),
            discord.SelectOption(label="Badges", description="Get the description of all the existing badges in the bot", emoji="<:badges18:1330123650053050471>")
        ]

        select = Select(
            placeholder="Choose a category...",
            options=options
        )

        # Handle dropdown selection
        async def select_callback(interaction):
            new_embed = None
            if select.values[0] == "Term Integration":
                new_embed = discord.Embed(
                    title="<a:Dictionary:1328048949617229968> Terminal Integration",
                    description=(
                        "\n**Definitions:**\n \n"
                        "<:gDot:1295454804839239730> **Credits** \nThe universal currency for transactions and upgrades \n \
                        <:gDot:1295454804839239730> **Cache** \nA temporary storage for Credits, designed for immediate usage \n \
                        <:gDot:1295454804839239730> **Vault** \nA secure storage for Credits, offering protection and weekly savings boosts \n \
                        <:gDot:1295454804839239730> **Tasks** \nMissions that help users gather Credits to drive their progression \n \
                        <:gDot:1295454804839239730> **Simulation** \nEngages users in minigames like `rps` and `HighLow`, wager is enabled\n \
                        <:gDot:1295454804839239730> **CryoStocks** \nVirtual stocks whose value fluctuates, offering a dynamic trading experience \n \
                        <:gDot:1295454804839239730> **Trivia** \nA source of knowledge and entertainment, rewarding users with points for their iq"
                    ),
                    color=int(em.embed(), 16)
                )

            elif select.values[0] == "Credits":
                new_embed = discord.Embed(
                    title="<:dGem:1312309674011525150> Credits",
                    description=(
                        "\n**Commands:**\n"
                        "<:gDot:1295454804839239730> `;task` \nEarn credits by completing tasks \n \n"
                        "<:gDot:1295454804839239730> `;status` \nView your current Cache and Vault balance \n \n"
                        "<:gDot:1295454804839239730> `;store <amt>` \nDeposit into your Vault \n \n"
                        "<:gDot:1295454804839239730> `;extract <amt>` \nWithdraw from your Vault to your Cache \n \n"
                        "<:gDot:1295454804839239730> `;profile` \nViews your credits, inventory and net progress \n \n"
                        "<:gDot:1295454804839239730> `;shop` \nDisplays the items available in the shop \n \n"
                        "<:gDot:1295454804839239730> `;purchase <item>/ ;p <item>` \nBuy the items for credits from the shop! \n \n"
                        "<:gDot:1295454804839239730> `;use <item>` \nUse the items that you hav collected in your inventory! \n \n"
                        "<:gDot:1295454804839239730> `;give <user> <amt>` \nShare your credits with other players! \n \n"
                        "<:gDot:1295454804839239730> `;gift <user> <item> <amt>` \nGift items to other playerss!"
                    ),
                    color=int(em.embed(), 16)
                )

            elif select.values[0] == "Minigames":
                new_embed = discord.Embed(
                    title="<a:minigames:1312298010549555270> Minigames",
                    description=(
                        "\n**Commands:**\n"
                        "<:gDot:1295454804839239730> `;simulate <bet_amt>` \nRandomly selects a minigame like RPS or HighLow.\n \n"
                        "<:gDot:1295454804839239730> `;trivia` \nAnswer trivia questions for rewards.\n \n"
                        "<:gDot:1295454804839239730> `;leaderboard` / `;lb` \nSee trivia rankings.\n \n"
                        "<:gDot:1295454804839239730> `;blackjack <bet_amt>` / `;bj <bet_amt>` \nPull the chances to win big with blackjack wagerings!\n \n"
                        "<:gDot:1295454804839239730> `;space` \nExplore the undiscovered and find some cool rewards!\n \n"
                        "<:gDot:1295454804839239730> `;cf` \nFlip a coin and predict the outcome."
                    ),
                    color=int(em.embed(), 16)
                )

            elif select.values[0] == "CryoStock Trading":
                new_embed = discord.Embed(
                    title="<a:Stocks:1328040520374550633> CryoStock Trading",
                    description=(
                        "\n**Commands:**\n \n \
                        <:gDot:1295454804839239730> `;stocks` \nDrops down the list of CryoStocks available in the bot \n \n \
                        <:gDot:1295454804839239730> `;buy <Ctk> <qty>` \nPurchase the CryoStocks, widening the exploration through CryoStock Nexus \n \n \
                        <:gDot:1295454804839239730> `;sell <Ctk> <qty>` \nSell the CryoStocks that is in your possession \n \n \
                        <:gDot:1295454804839239730> `;portfolio` \nDisplays your status in CryoStocks \n \n \
                        <:gDot:1295454804839239730> `;virtualize` \nVisually depict the value fluctuations of virtual entities!"
                    ),
                    color=int(em.embed(), 16)
                )

            elif select.values[0] == "Fun & Utility":
                new_embed = discord.Embed(
                    title="<a:Fun:1328041308375220305> Just for fun",
                    description=(
                        "\n**Utility Commands:**\n \n \
                        <:gDot:1295454804839239730> `;anime_list <anime_name>` View the list of episodes of an Anime that we have recognized\n \
                        \n**Fun Commands:**\n \n \
                        <:gDot:1295454804839239730> `;wave <user>` *Oi oii helo!* \n \
                        <:gDot:1295454804839239730> `;pat <user>` *pat pat pat!* \n \
                        <:gDot:1295454804839239730> `;hug <user>` *Deep n warm hugs* \n \
                        <:gDot:1295454804839239730> `;kiss <user>` *Smooch smooooocchhhh* \n \
                        <:gDot:1295454804839239730> `;lick <user>` *Slurrpp mm* \n \
                        <:gDot:1295454804839239730> `;bite <user>` *Myum yum yumm* \n \
                        <:gDot:1295454804839239730> `;cuddle <user>` *Nyam nyaaamm* \n \
                        <:gDot:1295454804839239730> `;slap <user>` :skull: \n \
                        <:gDot:1295454804839239730> `;punch <user>` :skull: \n \
                        <:gDot:1295454804839239730> `;kick <user>` :skull: \n \
                        <:gDot:1295454804839239730> `;stab <user>` :skull: \n \
                        <:gDot:1295454804839239730> `;kill <user>` :skull:"
                    ),
                    color=int(em.embed(), 16)
                )
                
            elif select.values[0] == "Badges":
                new_embed = discord.Embed(
                    title="<:badges18:1330123650053050471> Badges",
                    description=(
                        "\n**Commands:**\n \n \
                        <:triviamaster:1337825827139616861> | **Trivia Master** - Score 100 trivia points\n \n \
                        <:speedster:1337809091619328103> | **Speedster** - Answer 10 trivia questions correctly within 10 seconds each\n \n \
                        <:streakking:1337825849277153300> | **Streak King** - Achieve a streak of 25 consecutive correct answers in trivia\n \n \
                        <:taskmaster:1338010209682980864> | **Task Master** - Successfully work 10 times in a row!"
                    ),
                    color=int(em.embed(), 16)
                )
                
            new_embed.set_image(url=None)  # Remove the image for subsequent embeds
            await interaction.response.edit_message(embed=new_embed, view=view, attachments=[])
                
        select.callback = select_callback
        view = View()
        view.add_item(select)

        await ctx.send(file=file, embed=embed, view=view)
