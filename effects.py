import discord 
import os
import json
import math
import random
from discord import ButtonStyle, Embed, Interaction, ui
from phone_apps import get_dictionary_meaning, get_weather, get_random_meme
from discord.ui import View, Button, Modal, TextInput
from PIL import Image, ImageDraw # For tictactoe
import asyncio
from datetime import datetime, timedelta
import numpy as np
import aiohttp
import ast
import sqlite3

# Const Functions
# Get author id
def author_id(ctx):
    author_id = ctx.author.id
    return author_id

# Effect items 
# Coffee function to boost salary
def coffee(ctx, user_data):
    user_data.setdefault("effects", {})
    coffee_multiplier = 1.2
    expires_at = (datetime.utcnow() + timedelta(hours=6)).timestamp()
    # Check if salary boost exists
    if "salary_boost" in user_data["effects"]:
        # Add the new multiplier to the existing one
        user_data["effects"]["salary_boost"]["multiplier"] += coffee_multiplier
        user_data["effects"]["salary_boost"]["expires_at"] = expires_at
        return f"{ctx.author.mention}, you drank another coffee! ☕ Your salary boost increased further and lasts for 6 more hours!"
    else:
        # Apply new salary boost
        user_data["effects"]["salary_boost"] = {
            "multiplier": coffee_multiplier,
            "expires_at": expires_at
        }
    user_data["effects"]["salary_boost"] = {
        "multiplier": 1.2,
        "expires_at": expires_at
    }
    return f"{ctx.author.mention}, you used a coffee! Your salary is slightly boosted for 6 hours."

# Jackpot coin
def jackpot_coin(ctx, user_data):
    rng = random.randint(1, 249)
    rng = rng + random.randint(1, 249)
    if rng%10 == 0:
        user_data["wallet"] *= 2
        return f"{ctx.author.mention}, you won the jackpot! The credits in your wallet doubled!!"
    else:
        user_data["wallet"] = int(user_data["wallet"]/1.2)
        return f"{ctx.author.mention}, you lost the jackpot! The credits in your wallet decreased by 20%."
    
# Dice function
def dice(ctx):
    choice = random.randint(1,6)
    return f"{ctx.author.mention} rolled a {choice}! <a:dice_roll:1326047959678193686>"

# Valentines Box function
def valentines_box(ctx, user_data):
    items = np.array([
        "rose", "pink-rose", "love-letter", "chocolate",
        "chocolate-box", "teddy-bear", "teddy-heart", "valentine-gem"
    ])
    weights = np.array([20, 20, 15, 15, 10, 10, 8, 0.1])

    adjectives = np.array(["pretty", "cute", "lovely", "adorable", "little", "shiny"])

    emotes = {
        'rose': "<a:redrose:1338179361299239024>",
        'pink-rose': "<a:pinkrose:1338179366596907080>",
        'love-letter': "<:loveletter:1338179935801446462>",
        'chocolate': "<:chocolate:1338180103892369522>",
        'chocolate-box': "<a:ChocolateBox:1338180115817041960>",
        'teddy-bear': "<:teddybear:1338182716818198705>",
        'teddy-heart': "<:teddyheart:1338182761231417405>",
        'valentine-gem': "<a:ValentineHeart:1338183796716994632>"
    }

    # Select an item based on weighted probability
    selected_item = np.random.choice(items, p=weights / weights.sum())

    # Select a random adjective
    selected_adjective = np.random.choice(adjectives)

    # Add the selected item to user's inventory
    user_data.setdefault("inventory", {})
    user_data["inventory"].setdefault(selected_item, 0)
    user_data["inventory"][selected_item] += 1

    return f"{ctx.author.mention}, you opened a **Valentine's Box** and received a {selected_adjective} **{selected_item.replace('-', ' ').title()}**! {emotes[selected_item]}"

# Love letter function
async def love_letter(ctx):
    titles = np.array([
        "To My Sweetheart", "To My Love", "To My Soulmate",
        "To My Forever", "To My Everything", "To My Lovebug",
        "To My Dearest", "To My Love"
    ])
    
    letters = np.array([
        "Every moment with you feels like a dream ☁️💖\n\
        Your smile lights up my world like the sun 🌞✨\n\
        Holding your hand feels like home 🏡❤️\n\
        I’m so lucky to have you, my love 💕\n\
        Forever yours, always. 💌💫",
        "You are my heart’s favorite melody 🎶❤️\n\
        Every heartbeat whispers your name 💓✨\n\
        In your arms, I find my peace 🌙🤍\n\
        Loving you is my greatest adventure 🚀💕\n\
        Always and forever, just us two. 💑💖",
        "You are the poetry my heart recites 📜💖\n\
        Each day with you is a beautiful love story 📖✨\n\
        Your love is my safe haven 🏡💕\n\
        I cherish every laugh, every touch, every moment 😍💫\n\
        With you, forever is not long enough. ⏳❤️",
        "Your love is the magic that colors my world 🎨💖\n\
        Every **I love you** from you is a treasure 💎💕\n\
        You are my sweetest thought and my happiest place 🥰✨\n\
        Holding you is like holding a piece of heaven ☁️💓\n\
        I’ll love you in every lifetime. 🌍💞",
        "You are my heart’s home, my sweetest peace 🏡💖\n\
        Every day with you is a new adventure 🌍💕\n\
        Your love is my greatest gift 🎁💓\n\
        With you, I need nothing else 🌙✨\n\
        Forever and always, my love. 💑❤️",
        "Your hugs are warmer than the coziest blanket 🤗💕\n\
        Your laughter is my favorite melody 🎶💖\n\
        Every day, you make my heart dance 💃🕺\n\
        I love you to the moon and back 🌙💓\n\
        My heart belongs to you, always. 💘✨",
        "Your love is the rhythm of my heart 💖🎵\n\
        Each day with you is a dream come true ☁️💞\n\
        You make my world shine brighter than the stars ✨🌟\n\
        No words can ever express how much I adore you 💕\n\
        You and me, forever. 💑💌",
        "You are my sunshine on the cloudiest days ☀️💖\n\
        Your love is the melody my soul hums 🎶💕\n\
        Every moment with you is pure magic ✨💓\n\
        You are my greatest love story 📖❤️\n\
        I love you more than words can say. 💌💫"
    ])

    embed = discord.Embed(title="Love Letter :love_letter:", color=discord.Color.magenta())
    embed.add_field(name=np.random.choice(titles), value=np.random.choice(letters), inline=False)
    await ctx.send(embed=embed)

# Rose (proposal) function
async def rose(ctx, receiver):
    titles = np.array([
        "Omg! It is a proposal! :love_letter:", "Aww! So sweet! :heart:",
        "A rose for you! :rose:", "A token of love! :sparkling_heart:",
        "A symbol of affection! :sparkles:"
    ])
    
    lines = np.array([
        "*With a deep breath, **{sender}** held out the ring, eyes locked onto **{receiver}**. 'Every moment, every choice, every step—it's all led me to you. Will you be my forever?'*",
        "***{sender}** reached for **{receiver}’s** hand, their heart pounding. 'No words can ever capture what you mean to me, but maybe this will—will you marry me?'*",
        "*Kneeling before **{receiver}**, **{sender}** smiled softly. 'They say love is written in the stars, but I want ours to be written in time. Will you say yes?'*",
        "*As the waves crashed behind them, **{sender}** took **{receiver}’s** hands. 'You're not just part of my story—you are my story. Will you be mine forever?'*",
        "***{sender}** looked at **{receiver}** with unwavering certainty. 'I never believed in fate until I met you. Now, I believe in forever. Will you marry me?'*",
        "*With a nervous laugh, **{sender}** opened the tiny velvet box, gazing up at **{receiver}**. 'I've thought of a thousand ways to say this, but only three words matter—marry me, please?'*",
        "***{sender}** held **{receiver}** close, their voice a whisper in the cool night air. 'You're my greatest love, my best friend, my home. Let’s make forever official—will you marry me?'*"
    ])

    emojis = {"💖": "accepted", "💔": "rejected"}
    sender = ctx.author

    embed = discord.Embed(title=np.random.choice(titles), color=discord.Color.red())
    embed.add_field(name="I love you..", value=np.random.choice(lines).format(sender=sender, receiver=receiver), inline=False)
    embed.add_field(name="", value="`React with 💖 to accept and 💔 to reject!`", inline=False)
    
    message = await ctx.send(embed=embed)
    for emoji in emojis.keys():
        await message.add_reaction(emoji)

    def check(reaction, user):
        return user == receiver and str(reaction.emoji) in emojis and reaction.message.id == message.id

    try:
        reaction, user = await ctx.bot.wait_for("reaction_add", timeout=60.0, check=check)
        if str(reaction.emoji) == "💖":
            response = f"<a:a_tada:1340692885456031825> ***{receiver}** has accepted **{sender}’s** proposal! <a:a_ring:1340693227916886100> Congratulations!*"
        else:
            response = f"<a:Heart_Broken:1340695462285541516> ***{receiver}** has rejected **{sender}’s** proposal... <:CryCry:1340694293677084702> Maybe another time?*"
        await ctx.send(response)

    except TimeoutError:
        await ctx.send(f"🕑 ***{receiver}** didn't respond in time! The proposal remains unanswered...*")
        
def chocolate(ctx, user_data):
    user_data.setdefault("effects", {})
    
    # Default multiplier for chocolate
    chocolate_multiplier = 1.1
    expires_at = (datetime.utcnow() + timedelta(hours=4)).timestamp()
    
    # Check if salary boost exists
    if "salary_boost" in user_data["effects"]:
        # Add the new multiplier to the existing one
        user_data["effects"]["salary_boost"]["multiplier"] += chocolate_multiplier
        user_data["effects"]["salary_boost"]["expires_at"] = expires_at
        return f"{ctx.author.mention}, you ate another chocolate! 🍫 Your salary boost increased further and lasts for 4 more hours!"
    else:
        # Apply new salary boost
        user_data["effects"]["salary_boost"] = {
            "multiplier": chocolate_multiplier,
            "expires_at": expires_at
        }
        return f"{ctx.author.mention}, you ate a chocolate! 🍫 Your salary is slightly boosted for 4 hours!"

# Pokedex function to fetch Pokémon data
async def pokedex(interaction):
    type_emojis = {
        'normal': '<:normal:1325097197494341706> ', 'fire': '<:fire:1325097850769510491> ', 'water': '<:water:1325097618485018684> ', 'electric': '<:electric:1325097595734986782> ',
        'grass': '<:grass:1325099488179650580> ', 'ice': '<:ice:1325099403857498223>', 'fighting': '<:fighting:1325099433469415526> ', 'poison': '<:poison:1325099415047901215> ',
        'ground': '<:ground:1325099460451373137> ', 'flying': '<:flying:1325099452721266741> ', 'psychic': '<:psychic:1325099469405945938> ', 'bug': '<:bug:1325099476070957167> ',
        'rock': '<:rock:1325102337232081098> ', 'ghost': '<:ghost:1325102293389017108> ', 'dragon': '<:dragon:1325102317065994253> ', 'dark': '<:dark:1325102328679759964> ',
        'steel': '<:steel:1325102302326951969> ', 'fairy': '<:fairy:1325102310380273685> '
    }

    class PokedexModal(Modal):
        def __init__(self):
            super().__init__(title="Enter Pokémon Name or ID")
            self.add_item(TextInput(label="Pokémon Name/ID", placeholder="e.g., Pikachu or 25"))

        async def on_submit(self, interaction: discord.Interaction):
            query = self.children[0].value.lower()
            await fetch_pokemon_data(interaction, query)

    async def fetch_pokemon_data(interaction, query):
        async with aiohttp.ClientSession() as session:
            try:
                url = f"https://pokeapi.co/api/v2/pokemon/{query}"
                async with session.get(url) as response:
                    if response.status != 200:
                        await interaction.response.send_message(content="Pokémon not found! Please try again.")
                        return
                    data = await response.json()

                species_url = data['species']['url']
                async with session.get(species_url) as species_response:
                    species_data = await species_response.json()

                name = data['name'].capitalize()
                types = " ".join([f"{type_emojis[t['type']['name']]} {t['type']['name'].capitalize()}" for t in data['types']])
                abilities = ", ".join([a['ability']['name'].capitalize() for a in data['abilities']])
                egg_groups = ", ".join([eg['name'].capitalize() for eg in species_data['egg_groups']])
                height = data['height'] / 10
                weight = data['weight'] / 10
                catch_rate = species_data['capture_rate']
                stats = '\n'.join([f"{s['stat']['name'].capitalize()}: {s['base_stat']}" for s in data['stats']])

                dex_number = data['id']
                sprite_url = (
                    data['sprites']['versions']['generation-v']['black-white']['animated']['front_default']
                    if dex_number < 650
                    else data['sprites']['other']['home']['front_default']
                )

                gen = ""
                match dex_number:
                    case dex_number if dex_number <= 151: gen = "rb"
                    case dex_number if dex_number <= 251: gen = "gs"
                    case dex_number if dex_number <= 386: gen = "rs"
                    case dex_number if dex_number <= 493: gen = "dp"
                    case dex_number if dex_number <= 649: gen = "bw"
                    case dex_number if dex_number <= 721: gen = "xy"
                    case dex_number if dex_number <= 809: gen = "sm"
                    case dex_number if dex_number <= 905: gen = "ss"
                    case dex_number if dex_number <= 1025: gen = "sv"
                    case _: gen = "sv"
                if name.endswith("-mega"):
                    gen = "xy"

                embed = discord.Embed(title=f"Pokédex Entry: {name}", color=discord.Color.green())
                embed.set_thumbnail(url=sprite_url)
                embed.add_field(name="Types", value=types, inline=True)
                embed.add_field(name="Abilities", value=abilities, inline=True)
                embed.add_field(name="Egg Groups", value=egg_groups, inline=False)
                embed.add_field(name="Height", value=f"{height} m", inline=True)
                embed.add_field(name="Weight", value=f"{weight} kg", inline=True)
                embed.add_field(name="Catch Rate", value=f"{catch_rate}", inline=True)
                embed.add_field(name="Stats", value=stats, inline=False)
                embed.add_field(name="Smogon Reference", value=f"**[Analysis <a:PokeBall:1309042882677837874>](https://www.smogon.com/dex/{gen}/pokemon/{name}/)**", inline=False)

                await interaction.response.send_message(embed=embed)

            except Exception as e:
                await interaction.followup.send_message(content=f"Error: {str(e)}")  # Use followup here!

    # Show the modal for user input
    modal = PokedexModal()
    await interaction.response.send_modal(modal)

# Phone function displaying the phone embed with buttons for Tic-Tac-Toe, Calculator, and Pokedex
async def phone(ctx, bot):
    class PhoneView(View):
        def __init__(self, user_id: int):
            super().__init__()
            self.user_id = user_id
            # Row 1
            self.add_item(Button(label="➕Calculator", style=ButtonStyle.primary, custom_id="calc_button", row=0))
            self.add_item(Button(label="⭕Tic-Tac-Toe", style=ButtonStyle.primary, custom_id="ttt_button", row=0))
            self.add_item(Button(label="📱Pokedex", style=ButtonStyle.success, custom_id="pokedex_button", row=0))
            # Row 2
            self.add_item(Button(label="📖Dictionary", style=ButtonStyle.primary, custom_id="dictionary_button", row=1))
            self.add_item(Button(label="🌦️Weather", style=ButtonStyle.primary, custom_id="weather_button", row=1))
            #self.add_item(Button(label="📝Notes", style=ButtonStyle.primary, custom_id="notes_button", row=1))
            self.add_item(Button(label="🤣Meme", style=ButtonStyle.success, custom_id="meme_button", row=1))

    phone_embed = Embed(title="<:x_:1346906348951965787>Phone", description="A modern smartphone with in-built apps!", color=discord.Color.blue())
    phone_embed.set_image(url="attachment://phone_screen.png")
    file = discord.File("phone_screen.png", filename="phone_screen.png")
    await ctx.send(file=file, embed=phone_embed, view=PhoneView(ctx.author.id))

    def check(interaction):
        return interaction.user == ctx.author and interaction.data['custom_id'] in [
            'calc_button', 'ttt_button', 'pokedex_button', 'dictionary_button', 'weather_button', 'notes_button', 'meme_button'
        ]

    try:
        while True:
            interaction = await bot.wait_for("interaction", check=check, timeout=30)
            custom_id = interaction.data['custom_id']

            if custom_id == "calc_button":
                await interaction.response.send_message(await calculator(ctx))

            elif custom_id == "ttt_button":
                await interaction.response.send_message("Please mention a user to play Tic-Tac-Toe with!")

                def user_check(m):
                    return m.author == ctx.author and m.mentions
                
                try:
                    msg = await bot.wait_for("message", check=user_check, timeout=30)
                    opponent = msg.mentions[0]
                    await tictactoe(ctx, opponent)
                except asyncio.TimeoutError:
                    await ctx.send("You took too long to mention a user!")

            elif custom_id == "pokedex_button":
                await pokedex(interaction)

            elif custom_id == "dictionary_button":
                await interaction.response.send_message("📖 **Enter a word** to look up its meaning:", ephemeral=True)

                def msg_check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                
                try:
                    msg = await bot.wait_for("message", check=msg_check, timeout=30)
                    definition = await get_dictionary_meaning(msg.content)
                    embed = Embed(title=f"📖 Definition: {msg.content}", description=definition, color=discord.Color.blue())
                    await ctx.send(embed=embed)

                except asyncio.TimeoutError:
                    await ctx.send("⏳ You took too long! Try again.")

            elif custom_id == "weather_button":
                await interaction.response.send_message("🌦️ **Enter a city** to check the weather:", ephemeral=True)

                def msg_check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                
                try:
                    msg = await bot.wait_for("message", check=msg_check, timeout=30)
                    weather_info = await get_weather(msg.content)
                    embed = Embed(title=f"<:weather:1347247857736093797> Weather in {msg.content}", description=weather_info, color=discord.Color.green())
                    await ctx.send(embed=embed)

                except asyncio.TimeoutError:
                    await ctx.send("⏳ You took too long! Try again.")

            elif custom_id == "notes_button":
                embed = Embed(title="📝 Notes Manager", description="Choose an option below:", color=discord.Color.gold())
                view = NotesView(ctx.author.id)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

            elif custom_id == "meme_button":
                meme_url = await get_random_meme()
                embed = Embed(title="🤣 Random Meme", color=discord.Color.blue()).set_image(url=meme_url)
                await interaction.response.send_message(embed=embed)

    except asyncio.TimeoutError:
        await ctx.send("Phone has entered idle time, use the command again to turn it on <a:Mobile33:1346863576195010620>.")

# Database functions
# List notes
def get_notes(user_id):
    conn = sqlite3.connect("phone.db")
    cursor = conn.cursor()
    cursor.execute("SELECT note_content FROM notes WHERE user_id = ?", (user_id,))
    notes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return notes

# Add notes
async def add_note(self, interaction: discord.Interaction):
    await interaction.response.send_message("📝 **Enter the content** of your note:", ephemeral=True)

    def check(m):
        return m.author.id == interaction.user.id and m.channel == interaction.channel

    try:
        msg = await interaction.client.wait_for("message", check=check, timeout=30)  # Waits for user input
        conn = sqlite3.connect("phone.db")
        cursor = conn.cursor()
        
        cursor.execute("CREATE TABLE IF NOT EXISTS notes (user_id INTEGER,note_content TEXT);")
        # Insert note into database
        cursor.execute("INSERT INTO notes (user_id, note_content) VALUES (?, ?)", (interaction.user.id, msg.content))
        conn.commit()
        conn.close()
        
        await interaction.followup.send("✅ **Note added successfully!**", ephemeral=True)
    except Exception as e:
        await interaction.followup.send("❌ **Failed to add note.**", ephemeral=True)

# Delete notes
async def delete_note(user_id, note_content):
    conn = sqlite3.connect("phone.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE user_id = ? AND note_content = ?", (user_id, note_content))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0  # Returns True if a note was deleted

# Embed generator for notes
def get_notes_embed(user_id):
    notes = get_notes(user_id)
    embed = discord.Embed(title="📝 Your Notes", color=discord.Color.green())

    if notes:
        for i, note in enumerate(notes, start=1):
            embed.add_field(name=f"Note {i}", value=note, inline=False)
    else:
        embed.description = "You have no notes."
    
    return embed

# Notes Configuration
class NotesView(View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(Button(label="➕ Add Note", style=discord.ButtonStyle.success, custom_id="add_note"))
        self.add_item(Button(label="📜 List Notes", style=discord.ButtonStyle.secondary, custom_id="list_notes"))
        self.add_item(Button(label="🗑️ Remove Note", style=discord.ButtonStyle.danger, custom_id="remove_note"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True  # Ensure the interaction is always allowed

    async def add_note(self, interaction: discord.Interaction):
        await interaction.response.send_message("📝 **Enter the content** of your note:", ephemeral=True)

        def check(m):
            return m.author.id == interaction.user.id and m.channel == interaction.channel

        try:
            msg = await interaction.client.wait_for("message", check=check, timeout=30)
            conn = sqlite3.connect("economy_data.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (user_id, note_content) VALUES (?, ?)", (interaction.user.id, msg.content))
            conn.commit()
            conn.close()
            await interaction.followup.send("✅ **Note added successfully!**", ephemeral=True)
        except Exception as e:
            await interaction.followup.send("❌ **Failed to add note.**", ephemeral=True)

    async def list_notes(self, interaction: discord.Interaction):
        embed = get_notes_embed(interaction.user.id)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def remove_note(self, interaction: discord.Interaction):
        await interaction.response.send_message("📌 **Enter the content** of the note to remove:", ephemeral=True)

        def check(m):
            return m.author.id == interaction.user.id and m.channel == interaction.channel

        try:
            msg = await interaction.client.wait_for("message", check=check, timeout=30)
            success = await delete_note(interaction.user.id, msg.content)

            if success:
                await interaction.followup.send("✅ **Note removed successfully!**", ephemeral=True)
            else:
                await interaction.followup.send("❌ **Note not found.**", ephemeral=True)

        except Exception as e:
            await interaction.followup.send("❌ **Failed to remove note.**", ephemeral=True)
        
# Tic-Tac-Toe Configuration

# Helper to generate the game board image
def generate_board_image(board):
    size = 300
    cell_size = size // 3
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)

    # Draw grid lines
    for i in range(1, 3):
        draw.line([(0, i * cell_size), (size, i * cell_size)], fill='black', width=5)
        draw.line([(i * cell_size, 0), (i * cell_size, size)], fill='black', width=5)

    # Draw X and O
    for row in range(3):
        for col in range(3):
            x, y = col * cell_size, row * cell_size
            if board[row][col] == 'X':
                draw.line([(x + 10, y + 10), (x + cell_size - 10, y + cell_size - 10)], fill='red', width=5)
                draw.line([(x + 10, y + cell_size - 10), (x + cell_size - 10, y + 10)], fill='red', width=5)
            elif board[row][col] == 'O':
                draw.ellipse([(x + 10, y + 10), (x + cell_size - 10, y + cell_size - 10)], outline='blue', width=5)

    img.save('board.png')

# Check win condition
def check_winner(board):
    lines = board + [[board[r][c] for r in range(3)] for c in range(3)] + [[board[i][i] for i in range(3)], [board[i][2 - i] for i in range(3)]]
    for line in lines:
        if line.count(line[0]) == 3 and line[0] != '-':
            return True
    return False

# Custom View for Buttons
class TicTacToeView(ui.View):
    def __init__(self, board, player_x, player_o):
        super().__init__()
        self.board = board
        self.player_x = player_x
        self.player_o = player_o
        self.current_player = player_x
        self.game_over = False
        self.interaction = None  # Store the interaction object
        self.timeout_task = None  # Task for timeout
        # Start the timeout immediately when the view is initialized
        self.reset_timeout()

    async def update_board(self, interaction):
        self.interaction = interaction  # Update the interaction object
        self.reset_timeout()  # Reset timeout when the board updates
        generate_board_image(self.board)
        file = discord.File('board.png', filename='board.png')
        embed = discord.Embed(title="Tic Tac Toe", description=f"{self.current_player.mention}'s turn", color=discord.Color.blue())
        embed.set_image(url="attachment://board.png")
        await interaction.response.edit_message(embed=embed, attachments=[file], view=self)

    @ui.button(label="Forfeit", style=discord.ButtonStyle.danger)
    async def forfeit(self, interaction: discord.Interaction, button: ui.Button):
        if self.current_player.id == interaction.user.id:
            loser = self.current_player
            winner = self.player_o if self.current_player == self.player_x else self.player_x
            await self.end_game(loser, winner, reason="forfeited")
        else:
            await interaction.response.send_message("This is not your turn!", ephemeral=True)

    @ui.button(label="Move", style=discord.ButtonStyle.primary)
    async def move(self, interaction: discord.Interaction, button: ui.Button):
        if self.current_player.id == interaction.user.id:
            await interaction.response.send_modal(MoveModal(self))
        else:
            await interaction.response.send_message("This is not your turn!", ephemeral=True)

    async def start_timeout(self):
        try:
            await asyncio.sleep(60)  # 1 minute timeout
            if not self.game_over and self.interaction:  # Check if game already ended
                loser = self.current_player
                winner = self.player_o if self.current_player == self.player_x else self.player_x
                await self.end_game(loser, winner, reason="took too long")
        except asyncio.CancelledError:
            pass  # Task canceled

    def reset_timeout(self):
        if self.timeout_task:
            self.timeout_task.cancel()
        self.timeout_task = asyncio.create_task(self.start_timeout())

    async def end_game(self, loser, winner, reason):
        await self.disable_all_buttons()
        await self.interaction.message.edit(content=f"{loser.mention} {reason}! {winner.mention} wins!", view=None)
        self.game_over = True

    async def disable_all_buttons(self):
        for item in self.children:
            item.disabled = True
        if self.timeout_task:
            self.timeout_task.cancel()

# Modal for entering a move
class MoveModal(Modal):
    def __init__(self, view: TicTacToeView):
        super().__init__(title="Enter your move (1-9)")
        self.view = view
        self.add_item(TextInput(label="Move", placeholder="Enter a number between 1 and 9"))

    async def on_submit(self, interaction: discord.Interaction):
        move = self.children[0].value
        try:
            move = int(move)
            if move < 1 or move > 9:
                await interaction.response.send_message("Invalid move! Please enter a number between 1 and 9.", ephemeral=True)
                return

            row, col = divmod(move - 1, 3)

            if self.view.board[row][col] != '-':
                await interaction.response.send_message(f"Cell {move} is already occupied! Please choose another cell.", ephemeral=True)
                return

            self.view.board[row][col] = 'X' if self.view.current_player == self.view.player_x else 'O'

            if check_winner(self.view.board):
                generate_board_image(self.view.board)
                file = discord.File('board.png', filename='board.png')
                await self.view.disable_all_buttons()
                embed = discord.Embed(title="Game Over!", description=f"{self.view.current_player.mention} wins!", color=discord.Color.green())
                embed.set_image(url="attachment://board.png")
                await interaction.response.edit_message(embed=embed, attachments=[file], view=self.view)
                return

            self.view.current_player = self.view.player_o if self.view.current_player == self.view.player_x else self.view.player_x
            await self.view.update_board(interaction)

        except ValueError:
            await interaction.response.send_message("Invalid input! Please enter a valid number between 1 and 9.", ephemeral=True)

# Start Game Function
async def tictactoe(ctx, opponent: discord.Member):
    board = [['-' for _ in range(3)] for _ in range(3)]
    generate_board_image(board)
    file = discord.File('board.png', filename='board.png')

    view = TicTacToeView(board, ctx.author, opponent)
    embed = discord.Embed(title="Tic Tac Toe", description=f"{ctx.author.mention}'s turn", color=discord.Color.blue())
    embed.set_image(url="attachment://board.png")
    await ctx.send(embed=embed, file=file, view=view)

# Calculator configuration

# Input modal for calculator
class InputModal(Modal):
    def __init__(self, mode, shape=None):
        super().__init__(title="Input Values")
        self.mode = mode
        self.shape = shape
        if mode == 'area' or mode == 'perimeter' or mode =='exponent':
            self.inputs = TextInput(label="Enter parameters (space separated)", placeholder="e.g., 5 10", required=True)
        elif mode == 'dmas':
            self.inputs = TextInput(label="Enter values (space separated)", placeholder="e.g., 5 + 10", required=True)
        self.add_item(self.inputs)

    async def on_submit(self, interaction: discord.Interaction):
        result = None
        try:
            # Calculation logic based on mode and shape
            
            if self.mode == 'area':
                values = [float(x.strip()) for x in self.inputs.value.split(' ')]
                if self.shape == 'square':
                    result = values[0] ** 2
                elif self.shape == 'rectangle':
                    result = values[0] * values[1]
                elif self.shape == 'circle':
                    result = 3.14 * (values[0] ** 2)
                elif self.shape == 'triangle':
                    if len(values) == 2:
                        result = 0.5 * values[0] * values[1]
                    elif len(values) == 3:
                        s = sum(values) / 2
                        result = math.sqrt(s * (s - values[0]) * (s - values[1]) * (s - values[2]))
                elif self.shape == 'trapezium':
                    result = ((values[0] + values[1]) / 2) * values[2]
            elif self.mode == 'perimeter':
                values = [float(x.strip()) for x in self.inputs.value.split(' ')]
                if self.shape == 'square':
                    result = 4 * values[0]
                elif self.shape == 'rectangle':
                    result = 2 * (values[0] + values[1])
                elif self.shape == 'circle':
                    result = 2 * 3.14 * values[0]
                else:
                    result = sum(values)
            elif self.mode == 'exponent':
                values = [float(x.strip()) for x in self.inputs.value.split(' ')]
                result = values[0] ** values[1]
            
            elif self.mode == 'dmas':
                expression = self.inputs.value
                try:
                    tree = ast.parse(expression, mode='eval')
                    if not all(isinstance(node, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.operator)) for node in ast.walk(tree)):
                        raise ValueError("Invalid input")
                    result = eval(expression)
                except Exception:
                    result = "`Invalid expression`"

            await interaction.response.send_message(f"**Result:** {result}")
        except Exception as e:
            await interaction.response.send_message(f"**Error:** {str(e)}")

async def calculator(ctx):
    # Create the embed with the options
    embed = discord.Embed(title="Calculator Options", description="Choose a mode below:", color=discord.Color.blue())
    embed.add_field(name="DMAS", value="Basic arithmetic operations.", inline=False)
    embed.add_field(name="Area", value="Calculate areas for various shapes.", inline=False)
    embed.add_field(name="Perimeter", value="Calculate perimeters for various shapes.", inline=False)
    embed.add_field(name="Exponential", value="Calculate exponentials.", inline=False)

    # Create the view instance
    view = CalculatorView(ctx)  # Use the CalculatorView class to add buttons

    # Send the embed with the buttons attached
    await ctx.send(embed=embed, view=view)

# Calculator views
class CalculatorView(View):
    author_id = 0
    def __init__(self, ctx):
        super().__init__()
        self.author_id = author_id(ctx)
    @discord.ui.button(label="DMAS", style=discord.ButtonStyle.primary)
    async def dmas_button(self, interaction: discord.Interaction, button: Button):
        if self.author_id == interaction.user.id:
            await interaction.response.send_modal(InputModal(mode='dmas'))
        else:
            await interaction.response.send_message("Hey, this is not your phone!", ephemeral=True)

    @discord.ui.button(label="Area", style=discord.ButtonStyle.primary)
    async def area_button(self, interaction: discord.Interaction, button: Button):
        if self.author_id == interaction.user.id:
            await interaction.response.send_message(
            embed=discord.Embed(title="Select Shape", description="Choose a shape:", color=discord.Color.green()),
            view=ShapeSelectionView(mode='area')  # View for selecting a shape
            )
        else:
            await interaction.response.send_message("Hey, this is not your phone!", ephemeral=True)

    @discord.ui.button(label="Perimeter", style=discord.ButtonStyle.primary)
    async def perimeter_button(self, interaction: discord.Interaction, button: Button):
        if self.author_id == interaction.user.id:
            await interaction.response.send_message(
            embed=discord.Embed(title="Select Shape", description="Choose a shape:", color=discord.Color.green()),
            view=ShapeSelectionView(mode='perimeter')  # View for selecting a shape
            )
        else:
            await interaction.response.send_message("Hey, this is not your phone!", ephemeral=True)

    @discord.ui.button(label="Exponential", style=discord.ButtonStyle.primary)
    async def exponent_button(self, interaction: discord.Interaction, button: Button):
        if self.author_id == interaction.user.id:
            await interaction.response.send_modal(InputModal(mode='exponent'))
        else:
            await interaction.response.send_message("Hey, this is not your phone!", ephemeral=True)


class ShapeSelectionView(View):
    def __init__(self, mode):
        super().__init__()
        self.mode = mode

    @discord.ui.button(label="Square", style=discord.ButtonStyle.primary)
    async def square(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(InputModal(mode=self.mode, shape='square'))

    @discord.ui.button(label="Rectangle", style=discord.ButtonStyle.primary)
    async def rectangle(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(InputModal(mode=self.mode, shape='rectangle'))

    @discord.ui.button(label="Circle", style=discord.ButtonStyle.primary)
    async def circle(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(InputModal(mode=self.mode, shape='circle'))

    @discord.ui.button(label="Triangle", style=discord.ButtonStyle.primary)
    async def triangle(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(InputModal(mode=self.mode, shape='triangle'))

    @discord.ui.button(label="Trapezium", style=discord.ButtonStyle.primary)
    async def trapezium(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(InputModal(mode=self.mode, shape='trapezium'))
