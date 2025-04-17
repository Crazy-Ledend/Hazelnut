import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
import random
import json
import os
import asyncio
import time
from datetime import datetime, timedelta
import work_commands as work
#import trade
import shop_commands as shop
import admin_commands
from stocks_plot import stock_commands
from minigames import minigame_commands
from help_commands import help_commands
#import trivial
from itertools import cycle
from fun_commands import setup as fun_commands_setup
from discord.ext import commands
import importlib
from levels import LevelSystem
#import info_commands
#from playlist_commands import playlist_commands
from pong import pong
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, Request

import json
import discord
import uvicorn
from fastapi import FastAPI, Request, Header
from discord.ext import commands

app = FastAPI()

WEBHOOK_AUTH = "###G@m3rz"  # Set this in DiscordBotList
LOG_CHANNEL_ID = 1351249529306873929  # Replace with a channel ID to log votes

# TOKEN
# Load the .env file
load_dotenv()
# Get the token from environment variables
TOKEN = os.getenv("TOKEN")

# CUSTOM STATUS
# Cycle of statuses
bot_status = cycle(["I need you..", "Fairytale..", "Donut by Twice..", "Meaw <3", "APT.", "Love maze..", "Die With A Smile.."])

# Constants
BANK_INTEREST_RATE = 0.05  # 5% interest
INTEREST_INTERVAL = 604800  # One week in seconds
DATA_FILE = "economy_data.json"
STOCKS_FILE = "stocks_data.json"
PETS_FILE = "pets.json"
POKEMON_TYPES_FILE = "pokemon_types.json"

def load_json(filename):
    """Load JSON safely."""
    if not os.path.exists(filename):
        return {}
    with open(filename, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_json(filename, data):
    """Save JSON safely."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Load or initialize data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        economy_data = json.load(f)
else:
    economy_data = {}

# Stocks
# Initialize stock data
stocks = {
    "Hazel.Inc": {"price": 100, "symbol": "HZL", "price_history": [100], "demand": 0},
    "Codex": {"price": 75, "symbol": "CDX", "price_history": [75], "demand": 0},
    "DataSphere": {"price": 50, "symbol": "DTS", "price_history": [50], "demand": 0},
}

# Load stock data from file
if os.path.exists("stocks_data.json"):
    with open("stocks_data.json", "r") as f:
        loaded_stocks = json.load(f)
        for stock_name, stock_data in loaded_stocks.items():
            if "price_history" not in stock_data:
                stock_data["price_history"] = [stock_data["price"]]
            if "demand" not in stock_data:
                stock_data["demand"] = 0
        stocks.update(loaded_stocks)

# Data storing
# Save data to JSON file
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(economy_data, f)

# Save stock data to file
def save_stocks():
    with open(STOCKS_FILE, "w") as f:
        json.dump(stocks, f)

# Creating a Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=';', intents=discord.Intents.all(), help_command=None)

# Initialize Level System
level_system = LevelSystem()

# Cooldown tracker (user ID mapped to the last message timestamp)
cooldown_tracker = {}

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    current_time = time.time()

    # Check for cooldown
    if user_id in cooldown_tracker:
        last_message_time = cooldown_tracker[user_id]
        if current_time - last_message_time < 2:  # 2-second cooldown
            return

    # Update the cooldown tracker
    cooldown_tracker[user_id] = current_time

    # Add XP for the message
    xp_to_add = 5  # Fixed XP per message (adjust as needed)
    level_up = await level_system.add_xp(user_id, xp_to_add)

    # If the user leveled up, notify them
    if level_up:
        user_id = str(message.author.id)
        current_level = level_system.get_level(user_id)
        await message.channel.send(f"> Congratulations {message.author.mention}, you've climbed up to **Level {current_level}**! <a:celebrate2:1332821148899217509>")

    # Process commands
    await bot.process_commands(message)

# Commands
@bot.command()
async def level(ctx):
    """Check the user's current level and XP and send an embed with the user's level, XP, and avatar."""
    user_id = str(ctx.author.id)
    current_level = level_system.get_level(user_id)
    current_xp, next_level_xp = level_system.get_progress(user_id)
    avatar_url = ctx.author.avatar.url

    embed = discord.Embed(
        title=f"{ctx.author.name}'s Level Card",
        description=f"**Level**: {current_level} <:level:1350903399733919815>\n**XP**: {current_xp}/{next_level_xp} <:XP:1350904276343586897>",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=avatar_url)

    await ctx.send(embed=embed)

@bot.hybrid_command(name="profile", description="View your profile with stats and details.")
async def profile(ctx):
    user_id = str(ctx.author.id)
    level_system.check_and_update_level(user_id)

    # Fetch updated data
    current_level = level_system.get_level(user_id)
    current_xp, next_level_xp = level_system.get_progress(user_id)
    progress = int((current_xp / next_level_xp) * 100)

    # Initialize the progress bar based on the calculated percentage
    if progress <= 15:
        progress_bar = "<:bar1:1334369116093550713><:bar2:1334369119797116939><:bar2:1334369119797116939><:bar2:1334369119797116939><:bar3:1334369130786197615>"
    elif progress > 15 and progress <= 35:
        progress_bar = "<a:bar4:1334368993066221639><:bar2:1334369119797116939><:bar2:1334369119797116939><:bar2:1334369119797116939><:bar3:1334369130786197615>"
    elif progress > 35 and progress <= 55:
        progress_bar = "<a:bar4:1334368993066221639><a:bar5:1334369012137594912><:bar2:1334369119797116939><:bar2:1334369119797116939><:bar3:1334369130786197615>"
    elif progress > 55 and progress <= 75:
        progress_bar = "<a:bar4:1334368993066221639><a:bar5:1334369012137594912><a:bar5:1334369012137594912><:bar2:1334369119797116939><:bar3:1334369130786197615>"
    elif progress > 75 and progress <= 95:
        progress_bar = "<a:bar4:1334368993066221639><a:bar5:1334369012137594912><a:bar5:1334369012137594912><a:bar5:1334369012137594912><:bar3:1334369130786197615>"
    elif progress > 95 and progress <= 100:
        progress_bar = "<a:bar4:1334368993066221639><a:bar5:1334369012137594912><a:bar5:1334369012137594912><a:bar5:1334369012137594912><a:bar6:1334368998896173126>"

    user = ctx.author  # The user who invoked the command
    user_data = get_user_data(ctx.author.id)  # Fetch user data (assumes this function exists)

    # Handle cases where no user data is found
    if not user_data:
        await ctx.send("No profile data found for you. Start engaging to build your profile!")
        return

    # Extract user data fields
    wallet = user_data.get("wallet", 0)
    bank_balance = user_data.get("bank", 0)
    stocks = user_data.get("portfolio", {})  # Example: {"AAPL": 10, "TSLA": 5}
    user_badges = user_data.get("badges", [])

    # Calculate inventory net worth
    total_value = 0
    if "inventory" in user_data:
        for item_name, amount in user_data["inventory"].items():
            item_value = amount * shop.items[item_name]["price"]
            total_value += item_value

    # Format stocks for display
    stocks_display = "\n- ".join([f"{symbol}: {quantity}" for symbol, quantity in stocks.items()]) or "No stocks owned."

    badges_display = None  # Initialize before condition

    work_cog = bot.get_cog("WorkCommands")
    if work_cog:
        badges = work_cog.badges
        badges_display = " ".join([badges[badge]["emoji"] for badge in user_badges if badge in badges]) if user_badges else None

    # Create the profile embed
    embed = discord.Embed(
        title=f"{user.name}'s Profile",
        color=discord.Color.blue(),
    )
    embed.set_thumbnail(url=user.avatar.url)  # Set user's profile picture
    embed.add_field(name="<:Rank:1350903724809388073> | Level", value=f"**Level**: {current_level} <:level:1350903399733919815>\n**Experience**: `{current_xp}/{next_level_xp}`\n{progress_bar}")
    embed.add_field(name="<:creditcard:1350902997454032909> | Cache balance", value=f"{wallet} <:credits:1313261430266658867>", inline=False)
    embed.add_field(name="<:Vault:1350903009709654046> | Vault", value=f"{bank_balance} <:credits:1313261430266658867>", inline=False)
    embed.add_field(name="<a:Graphical:1350903990400847882> | Portfolio list", value=f"\n- {stocks_display}", inline=False)
    embed.add_field(name="<:bag:1350902222661357670> | Inventory Net Worth", value=f"{total_value} <:credits:1313261430266658867>", inline=False)

    if badges_display:  # This check is now safe
        embed.add_field(name="Badges", value=f"\n{badges_display}", inline=False)
        
    embed.set_footer(text=f"Profile requested by {user.name}", icon_url=user.avatar.url)
    await ctx.send(embed=embed)

# Reload command
@bot.command(name="reload")
@commands.is_owner()  # Restrict this command to the bot owner
async def reload(ctx, module_name: str = None):
    if module_name == None:
        await ctx.send("<:discord_cross:1321809722151534645> | `Invalid syntax`")
        return
    try:
        # Unload if the module was previously loaded as an extension
        await bot.unload_extension(module_name)
    except commands.ExtensionNotLoaded:
        pass  # Ignore if it wasn't already loaded

    try:
        # Reload the module using importlib
        module = importlib.import_module(module_name)
        importlib.reload(module)

        # Load the extension back
        await bot.load_extension(module_name)
        await ctx.send(f"✅ `{module_name}` reloaded successfully!")
    except ModuleNotFoundError:
        await ctx.send(f"❌ `{module_name}` not found. Make sure it's importable and named correctly.")
    except Exception as e:
        await ctx.send(f"❌ Failed to reload `{module_name}`: `{e}`")

# Helper functions
def get_user_data(user_id):
    if str(user_id) not in economy_data:
        economy_data[str(user_id)] = {
            "wallet": 100,
            "bank": 0,
            "last_interest_time": datetime.now().isoformat(),
            "portfolio": {}
        }
        save_data()
    return economy_data[str(user_id)]

async def add_badge(ctx, user_id, badge_name):
    user_data = get_user_data(user_id)
    if "badges" not in user_data:
        user_data["badges"] = []
    if badge_name not in user_data["badges"]:
        user_data["badges"].append(badge_name)
        await ctx.send(f"<a:sparklee:1329027895615688744> | You earned the {badge_name} Badge!")
        save_data()  # Save updated data to the JSON file

def has_badge(user_id, badge_name):
    user_data = get_user_data(user_id)
    return badge_name in user_data.get("badges", [])

def update_interest(user_data):
    last_interest_time = datetime.fromisoformat(user_data["last_interest_time"])
    if datetime.now() - last_interest_time >= timedelta(seconds=INTEREST_INTERVAL):
        interest_amount = user_data["bank"] * BANK_INTEREST_RATE
        interest_amount = round(interest_amount, 2)
        user_data["bank"] += interest_amount
        user_data["last_interest_time"] = datetime.now().isoformat()
        save_data()
bot.get_user_data = get_user_data
bot.save_data = save_data
bot.add_badge = add_badge

# Task loops
# Update stock prices based on demand and random fluctuation
@tasks.loop(hours=6)
async def update_stock_prices():
    for stock_name, stock in stocks.items():
        # Adjust price based on demand
        price_change = stock["demand"] * 2  # Demand factor
        maxim = int(round((stock["price"] * 0.05), 0)) 
        minim = int(round((-1 * maxim), 0)) 
        fluctuation = random.randint(minim, maxim) # price fluctuation
        new_price = max(1, stock["price"] + price_change + fluctuation)
        stock["price"] = new_price

        # Reset demand after update
        stock["demand"] = 0

        # Update price history
        stock["price_history"].append(new_price)

    save_stocks()

@tasks.loop(minutes=60)
async def decrease_hunger_happiness():
    pets = load_json(PETS_FILE)
    pokemon_types = load_json(POKEMON_TYPES_FILE)
    current_time = time.time()

    for user_id, user_pets in pets.items():
        for pet_name, pet_data in user_pets.items():
            pokemon_id = str(pet_data["pokemon_id"])
            pokemon_type = pokemon_types.get(pokemon_id, "normal")
            hunger_rates = {"grass": 4, "fire": 6, "normal": 5}
            hunger_drop_rate = hunger_rates.get(pokemon_type, 5)
            happiness_drop_rate = 3

            pet_data["hunger"] = max(0, pet_data["hunger"] - hunger_drop_rate)
            pet_data["happiness"] = max(0, pet_data["happiness"] - happiness_drop_rate)

            # Initialize timestamps if missing
            if "last_warning_time" not in pet_data:
                pet_data["last_warning_time"] = current_time
            if "last_care_time" not in pet_data:
                pet_data["last_care_time"] = current_time

            # Check if user should be warned
            if pet_data["hunger"] <= 0 and pet_data["happiness"] <= 0:
                time_since_warning = current_time - pet_data["last_warning_time"]
                if time_since_warning >= 6 * 3600:  # 6 hours
                    user = await bot.fetch_user(user_id)
                    await user.send(f"Your `{pet_name.lower().capitalize()}` is suffering from neglect! 🥺 Please care for it soon.")
                    pet_data["last_warning_time"] = current_time

                # Level penalty after 36 hours of neglect
                time_since_care = current_time - pet_data["last_care_time"]
                if time_since_care >= 36 * 3600:
                    if pet_data.get("level", 1) > 1:
                        pet_data["level"] -= 1
                        await user.send(f"⚠️ `{pet_name.lower().capitalize()}` has lost a level due to neglect...")
                        # Reset last care time so it doesn't keep dropping
                        pet_data["last_care_time"] = current_time

    save_json(PETS_FILE, pets)
    print("✅ Updated pet hunger and happiness.")

@decrease_hunger_happiness.before_loop
async def before_loop():
    await bot.wait_until_ready()  # Ensures bot is fully ready before starting

# Background task to update interest weekly
@tasks.loop(hours=168)  # Every week
async def update_all_interests():
    for user_id in economy_data:
        user_data = economy_data[user_id]
        update_interest(user_data)
    save_data()

# Updating Bot presence
@tasks.loop(seconds=1800)
async def change_bot_status():
    current_status = next(bot_status)
    activity = discord.Activity(
        type=discord.ActivityType.listening,
        name=current_status
    )
    await bot.change_presence(status=discord.Status.idle, activity=activity)
    print(f"Changed presence to: {current_status}")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")
    print("------")
    await setup_hook()
    print(f"Cogs: {bot.cogs}")
    print("------")
    change_bot_status.start()  # Starts the status update loop
    update_stock_prices.start()  # Start price updater
    decrease_hunger_happiness.start() # Start pets undater

@app.post("/dbl-vote")
async def dbl_webhook(request: Request, authorization: str = Header(None)):
    if authorization != WEBHOOK_AUTH:
        return {"error": "Unauthorized"}, 403

    data = await request.json()
    user_id = str(data.get("id"))

    if user_id:
        user_data = get_user_data(user_id)
        user_data["wallet"] += 250
        save_data()

        # Use bot.loop.create_task instead
        bot.loop.create_task(send_vote_dm(user_id))
        bot.loop.create_task(log_vote(user_id))

        return {"success": True}
    
    return {"error": "Invalid request"}, 400


async def send_vote_dm(user_id):
    await bot.wait_until_ready()
    try:
        user = await bot.fetch_user(int(user_id))
        await user.send(f"🎉 Thank you for voting! You received 250 coins 🍪, <@{user_id}>.")
    except discord.Forbidden:
        print(f"❌ Cannot DM user {user_id} — they likely have DMs off.")
    except Exception as e:
        print(f"❌ Failed to send DM: {e}")


async def log_vote(user_id):
    await bot.wait_until_ready()
    try:
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            await channel.send(f"📬 Vote received from <@{user_id}>. 250 coins awarded!")
    except Exception as e:
        print(f"❌ Failed to log vote in channel: {e}")


@app.get("/")
def home():
    return {"message": "Hello, FastAPI is working!"}

# Start FastAPI in a separate thread
import threading

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=21471)

threading.Thread(target=run_fastapi, daemon=True).start()

# Ensure that load_extension is awaited properly
async def setup_extensions():
    await bot.load_extension("fun_commands")  # Load the fun commands cog asynchronously
    # await bot.load_extension("music")  # Load the music cog
    await bot.load_extension("work_commands")
    await bot.load_extension("info_commands")
    await bot.load_extension("admin_commands")
    await bot.load_extension("trade")
    await bot.load_extension("anime")
    await bot.load_extension("mafia")
    await bot.load_extension("trivial")
    await bot.load_extension("blackjack")
    await bot.load_extension("space")
    await bot.load_extension("pets")
    await bot.load_extension("easter")
    await bot.load_extension("hunt")
    # valentines event (next 3 lines)
    #if "valentines_event" in bot.extensions:
        #return  # Prevent reloading if it's already loaded
    #await bot.load_extension("valentines_event")

async def setup_hook():
    await setup_extensions()  # Now it is awaited properly

# Loading commands from other files
#work.work_commands(bot, add_badge, get_user_data, save_data)
shop.shop_commands(bot, get_user_data, save_data)
minigame_commands(bot, get_user_data, save_data)
stock_commands(bot, get_user_data, save_data, save_stocks, stocks)
#trivial_commands(bot, add_badge, get_user_data, save_data)
#playlist_commands(bot)
help_commands(bot)
pong(bot)

# Running the bot
bot.run(TOKEN)
