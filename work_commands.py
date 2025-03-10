import random
import discord
from discord.ext import commands
import os
import json
import time
from datetime import datetime
import work_minigames as w
from levels import LevelSystem

class WorkCommands(commands.Cog):
    def __init__(self, bot, add_badge, get_user_data, save_data):
        self.bot = bot
        self.get_user_data = get_user_data
        self.save_data = save_data
        self.add_badge = add_badge
        self.level_system = LevelSystem()
        self.cooldowns = {}
        self.active_tasks = {} 
        self.badges = {
                "Trivia-Master": {"emoji": "<:triviamaster:1337825827139616861>", "description": "Answer 100 questions correctly"},
                "Speedster": {"emoji": "<:speedster:1337809091619328103>", "description": "Answer 10 questions correctly within 10 seconds each"},
                "Streak-King": {"emoji": "<:streakking:1337825849277153300>", "description": "Achieve a streak of 25 consecutive correct answers"},
            	"Task-Master": {"emoji": "<:taskmaster:1338010209682980864>", "description": "Successfully work 10 times in a row!"}
            }

    WORK_STREAK_FILE = "work_streaks.json"

    def load_work_streak(self):
        if os.path.exists(self.WORK_STREAK_FILE):
            with open(self.WORK_STREAK_FILE, "r") as file:
                return json.load(file)
        else:
            return {}

    def save_work_streak(self, streak):
        with open(self.WORK_STREAK_FILE, "w") as file:
            json.dump(streak, file, indent=4)

    def check_cooldown(self, user_id):
        current_time = time.time()
        if user_id in self.cooldowns:
            last_used = self.cooldowns[user_id]
            if current_time - last_used < 3600:
                return False, (3600 - (current_time - last_used))
        return True, 0

    def update_cooldown(self, user_id):
        self.cooldowns[user_id] = time.time()

    async def work_logic(self, ctx):
        user_id = str(ctx.author.id)
        user_data = self.get_user_data(ctx.author.id)
        work_streak = self.load_work_streak()
        yield_amount = random.randint(100, 250)
        old_yield = yield_amount
        if user_id in work_streak:
            streak = work_streak[user_id]
        else:
            streak = 0
        # Check for active effects
        effect = 0
        effects = user_data.get("effects", {})
        salary_boost = effects.get("salary_boost")
        if salary_boost:
            expires_at = salary_boost.get("expires_at", 0)
            if datetime.utcnow().timestamp() < expires_at:
                yield_amount = int(yield_amount * salary_boost["multiplier"])
                effect = 1
            else:
                del user_data["effects"]["salary_boost"]

        yield_amount = await w.play_minigame(ctx, ctx.send, yield_amount)
        if yield_amount == old_yield:
            streak += 1
        elif yield_amount == (old_yield // 2):
            streak = 0
        user_data["wallet"] += yield_amount
        work_streak[user_id] = streak
        self.save_work_streak(work_streak)

        if work_streak[user_id] >= 10:
            await self.add_badge(ctx, user_id, "Task-Master")
        self.save_data()

        embed = discord.Embed(title="Task Complete <a:check:1312421527706406952>", color=int("69c9ce", 16))
        effect_text = "[<:Coffee:1322192609665486868>]" if effect == 1 else ""
        embed.add_field(name=f"Yield {effect_text}", value=f"{yield_amount} <:credits:1313261430266658867>", inline=True)
        embed.add_field(name="Updated Cache", value=f"{user_data['wallet']} <:credits:1313261430266658867>", inline=True)
        await ctx.send(embed=embed)

    async def balance_logic(self, ctx):
        user_data = self.get_user_data(ctx.author.id)
        embed = discord.Embed(title="Status", color=int("69c9ce", 16))
        embed.add_field(name="<:CreditCard:1321830790966939730> Cache", value=f"{user_data['wallet']} <:credits:1313261430266658867>", inline=True)
        embed.add_field(name="<:Locker:1321834186927247423> Vault", value=f"{user_data['bank']} <:credits:1313261430266658867>", inline=True)
        await ctx.send(embed=embed)

    async def deposit_logic(self, ctx, amount):
        user_data = self.get_user_data(ctx.author.id)
        # If "max" is provided, deposit the full wallet balance
        if amount and amount.lower() == "max":
            amount = user_data["wallet"]
            
        if amount != None:
            amount = int(amount)
        if amount is None or amount <= 0:
            await ctx.send("<:discord_cross:1321809722151534645> | Kindly enter a valid amount of credits")
            return
        
        if amount > user_data["wallet"]:
            await ctx.send("<a:notice:1312428458290319503> | Storage failed. Insufficient Credits in your Cache")
            return
        
        user_data["wallet"] -= amount
        user_data["bank"] += amount
        self.save_data()

        embed = discord.Embed(title="Storing Complete <a:check:1312421527706406952>", color=discord.Color.green())
        embed.add_field(name="Amt Stored", value=f"{amount} <:credits:1313261430266658867>", inline=True)
        embed.add_field(name="Updated Vault", value=f"{user_data['bank']} <:credits:1313261430266658867>", inline=True)
        await ctx.send(embed=embed)

    async def withdraw_logic(self, ctx, amount):
        user_data = self.get_user_data(ctx.author.id)
        # If "max" is provided, withdraw the full bank balance
        if amount and amount.lower() == "max":
            amount = user_data["bank"]
            
        if amount != None:
            amount = int(amount)
        if amount is None or amount <= 0:
            await ctx.send("<:discord_cross:1321809722151534645> | Kindly enter a valid amount of credits")
            return

        if amount > user_data["bank"]:
            await ctx.send("<a:notice:1312428458290319503> | Extraction failed. Insufficient Credits in Vault")
            return

        user_data["bank"] -= amount
        user_data["wallet"] += amount
        self.save_data()

        embed = discord.Embed(title="Extraction Complete <a:check:1312421527706406952>", color=discord.Color.green())
        embed.add_field(name="Amt Extracted", value=f"{amount} <:credits:1313261430266658867>", inline=True)
        embed.add_field(name="Updated Cache", value=f"{user_data['wallet']} <:credits:1313261430266658867>", inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="task", description="Complete tasks to earn credits!")
    @commands.guild_only()
    async def task(self, ctx):
        user_id = ctx.author.id

        # Prevent multiple tasks from running simultaneously
        if user_id in self.active_tasks:
            await ctx.send("<:warn:1312326746527240265> | You already have an active task. Please complete it before starting a new one.")
            return

        # Check cooldown
        can_use, remaining_time = self.check_cooldown(user_id)
        if not can_use:
            mins = remaining_time // 60
            secs = remaining_time % 60
            embed = discord.Embed(
                title="<:warn:1312326746527240265> Cooldown in progress..",
                color=int("69c9ce", 16)
            )
            embed.add_field(
                name="**Please wait,**",
                value=f"`{mins:.0f}` min `{secs:.2f}` s for reactivation <:Timer:1321812327309381704> ..\n",
                inline=False
            )
            await ctx.send(embed=embed)
            return

        # Mark task as active
        self.active_tasks[user_id] = True

        # Run the task logic
        await self.work_logic(ctx)

        # Mark task as completed (remove from active tasks)
        del self.active_tasks[user_id]
        self.update_cooldown(user_id)

    @commands.hybrid_command(name="status", description="Displays your Cache and Vault balance")
    @commands.guild_only()
    async def status(self, ctx):
        await self.balance_logic(ctx)

    @commands.hybrid_command(name="store", description="Deposit credits into your Vault")
    @commands.guild_only()
    async def store(self, ctx, amount: str = None):
        await self.deposit_logic(ctx, amount)

    @commands.hybrid_command(name="extract", description="Withdraw credits from your Vault")
    @commands.guild_only()
    async def extract(self, ctx, amount: str = None):
        await self.withdraw_logic(ctx, amount)

async def setup(bot):
    add_badge = bot.add_badge
    get_user_data = bot.get_user_data  # Replace with your actual function
    save_data = bot.save_data  # Replace with your actual function
    await bot.add_cog(WorkCommands(bot, add_badge, get_user_data, save_data))
    await bot.tree.sync()
