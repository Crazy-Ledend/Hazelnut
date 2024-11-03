import discord
from discord.ext import commands, tasks
import random
import json
import os
from datetime import datetime, timedelta

ADMIN_ROLE_ID = 1300577397657305239

def has_admin_role(ctx):
    return any(role.id == ADMIN_ROLE_ID for role in ctx.author.roles)

# Constants
BANK_INTEREST_RATE = 0.05  # 5% interest
INTEREST_INTERVAL = 604800  # One week in seconds
DATA_FILE = "economy_data.json"

# Load or initialize data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        economy_data = json.load(f)
else:
    economy_data = {}

# Save data to JSON file
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(economy_data, f)

# Create a Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Helper functions
def get_user_data(user_id):
    if str(user_id) not in economy_data:
        economy_data[str(user_id)] = {
            "wallet": 100,
            "bank": 0,
            "last_interest_time": datetime.now().isoformat()
        }
        save_data()
    return economy_data[str(user_id)]

def update_interest(user_data):
    last_interest_time = datetime.fromisoformat(user_data["last_interest_time"])
    if datetime.now() - last_interest_time >= timedelta(seconds=INTEREST_INTERVAL):
        interest_amount = user_data["bank"] * BANK_INTEREST_RATE
        user_data["bank"] += interest_amount
        user_data["last_interest_time"] = datetime.now().isoformat()
        save_data()

# Commands
@bot.command(name="addcoins")
async def add_coins(ctx, user: discord.User, amount: int):
    if not has_admin_role(ctx):
        await ctx.send("You do not have permission to use this command.")
        return

    user_data = get_user_data(user.id)
    user_data["wallet"] += amount
    save_data()

    await ctx.send(f"Added {amount} coins to {user.mention}'s wallet.")

# Command to remove coins from a user
@bot.command(name="removecoins")
async def remove_coins(ctx, user: discord.User, amount: int):
    if not has_admin_role(ctx):
        await ctx.send("You do not have permission to use this command.")
        return

    user_data = get_user_data(user.id)
    if amount > user_data["wallet"]:
        await ctx.send("This user does not have enough coins to remove that amount.")
        return

    user_data["wallet"] -= amount
    save_data()

    await ctx.send(f"Removed {amount} coins from {user.mention}'s wallet.")

# Command to set the exact number of coins for a user
@bot.command(name="editcoins")
async def edit_coins(ctx, user: discord.User, amount: int):
    if not has_admin_role(ctx):
        await ctx.send("You do not have permission to use this command.")
        return

    user_data = get_user_data(user.id)
    user_data["wallet"] = amount
    save_data()

    await ctx.send(f"Set {user.mention}'s wallet to {amount} coins.")

@bot.command(name="balance")
async def balance(ctx):
    user_data = get_user_data(ctx.author.id)
    embed = discord.Embed(title="Balance Information", color=discord.Color.blue())
    embed.add_field(name="<:wallet:1295431127951085631> Wallet", value=f"{user_data['wallet']} coins", inline=True)
    embed.add_field(name="<:Forkes_bank:1295431072485478580> Bank", value=f"{user_data['bank']} coins", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="deposit")
async def deposit(ctx, amount: int):
    user_data = get_user_data(ctx.author.id)
    if amount <= 0:
        await ctx.send("You must deposit a positive amount.")
        return
    if amount > user_data["wallet"]:
        await ctx.send("You don't have enough coins in your wallet.")
        return
    user_data["wallet"] -= amount
    user_data["bank"] += amount
    save_data()
    
    embed = discord.Embed(title="Deposit Successful", color=discord.Color.green())
    embed.add_field(name="Amount Deposited", value=f"{amount} coins", inline=True)
    embed.add_field(name="New Bank Balance", value=f"{user_data['bank']} coins", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="withdraw")
async def withdraw(ctx, amount: int):
    user_data = get_user_data(ctx.author.id)
    if amount <= 0:
        await ctx.send("You must withdraw a positive amount.")
        return
    if amount > user_data["bank"]:
        await ctx.send("You don't have enough coins in the bank.")
        return
    user_data["bank"] -= amount
    user_data["wallet"] += amount
    save_data()
    
    embed = discord.Embed(title="Withdrawal Successful", color=discord.Color.green())
    embed.add_field(name="Amount Withdrawn", value=f"{amount} coins", inline=True)
    embed.add_field(name="New Wallet Balance", value=f"{user_data['wallet']} coins", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="work")
async def work(ctx):
    user_data = get_user_data(ctx.author.id)
    earnings = random.randint(50, 100)
    user_data["wallet"] += earnings
    save_data()
    
    embed = discord.Embed(title="Work Successful", color=discord.Color.green())
    embed.add_field(name="Earnings", value=f"{earnings} coins", inline=True)
    embed.add_field(name="New Wallet Balance", value=f"{user_data['wallet']} coins", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="rps")
async def rps(ctx, choice: str, bet: int):
    valid_choices = ["rock", "paper", "scissors"]
    if choice not in valid_choices:
        await ctx.send("Invalid choice! Choose rock, paper, or scissors.")
        return
    
    user_data = get_user_data(ctx.author.id)
    
    if bet <= 0 or bet > user_data["wallet"]:
        await ctx.send("You must bet a positive amount that you can afford.")
        return

    bot_choice = random.choice(valid_choices)
    await ctx.send(f"I chose {bot_choice}!")

    if (choice == "rock" and bot_choice == "scissors") or \
       (choice == "paper" and bot_choice == "rock") or \
       (choice == "scissors" and bot_choice == "paper"):
        user_data["wallet"] += bet
        embed = discord.Embed(title="You Win!", color=discord.Color.green())
        embed.add_field(name="Wager", value=f"{bet} coins", inline=True)
        embed.add_field(name="New Wallet Balance", value=f"{user_data['wallet']} coins", inline=True)
        await ctx.send(embed=embed)
    elif choice == bot_choice:
        embed = discord.Embed(title="It's a Draw!", color=discord.Color.yellow())
        await ctx.send(embed=embed)
    else:
        user_data["wallet"] -= bet
        embed = discord.Embed(title="You Lose!", color=discord.Color.red())
        embed.add_field(name="Wager", value=f"{bet} coins", inline=True)
        embed.add_field(name="New Wallet Balance", value=f"{user_data['wallet']} coins", inline=True)
        await ctx.send(embed=embed)
    
    save_data()

# Background task to update interest weekly
@tasks.loop(hours=168)  # Every week
async def update_all_interests():
    for user_id in economy_data:
        user_data = economy_data[user_id]
        update_interest(user_data)
    save_data()

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user.name}")
    update_all_interests.start()

# Run the bot
bot.run("BOT TOKEN")