import discord
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime
import os
import asyncio
import random
import json
import aiohttp  # For fetching API data
import embed as em
import functools

TRIVIA_SCORES_FILE = "trivia_scores.json"
TRIVIA_STREAK_FILE = "trivia_streaks.json"

# Load and save functions
def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

async def fetch_trivia_questions(category):
    """Fetches a maximum of 5 trivia questions from an API based on the selected category."""
    url = f"https://opentdb.com/api.php?amount=5&category={category}&type=multiple"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if data["response_code"] == 0:
                return data["results"]
            return []

class Trivia(commands.Cog):
    def __init__(self, bot, add_badge):
        self.bot = bot
        self.trivia_scores = load_json(TRIVIA_SCORES_FILE)
        self.trivia_streak = load_json(TRIVIA_STREAK_FILE)
        self.trivia_sessions = {}  # Track active trivia sessions
        self.add_badge = add_badge

    def get_leaderboard(self):
        sorted_scores = sorted(self.trivia_scores.items(), key=lambda x: x[1], reverse=True)
        leaderboard = ""
        for idx, (user_id, points) in enumerate(sorted_scores[:10]):
            rank = "<:GoldenMedal:1318253949681406013>" if idx == 0 else "<:SilverMedal:1318253966420607018>" if idx == 1 else "<:BronzeMedal:1318254131710001223>" if idx == 2 else f"#{idx+1}"
            leaderboard += f"{rank} <@{user_id}>: {points} points\n"
        return leaderboard or "No scores recorded yet."

    async def handle_trivia(self, ctx, questions):
        user_id = str(ctx.author.id)
        streak = self.trivia_streak.get(user_id, 0)
        points = 0
        speed_answers = 0

        for question in questions:
            question["question"] = question["question"].replace("&quot;", "**")
            question["question"] = question["question"].replace("&#039;", "`")
            start_time = datetime.utcnow()
            formatted_question = discord.Embed(title="Trivia Question", description=question["question"], color=int(em.embed(), 16))

            options = question["incorrect_answers"] + [question["correct_answer"]]
            for i in range(0,4):
            	options[i] = options[i].replace("&deg;", "°")
            	options[i] = options[i].replace("&ndash;", "–")
            	options[i] = options[i].replace("&#039;", "'")
            random.shuffle(options)
            formatted_question.add_field(name="Choices", value="\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options)))

            await ctx.send(embed=formatted_question)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                message = await self.bot.wait_for("message", timeout=30, check=check)
                user_answer = message.content.strip().lower()
                correct_answer = question["correct_answer"].lower()

                if user_answer == correct_answer or user_answer in [str(i+1) for i, opt in enumerate(options) if opt.lower() == correct_answer]:
                    points += 1
                    streak += 1
                    elapsed_time = (datetime.utcnow() - start_time).total_seconds()
                    if elapsed_time <= 10:
                        speed_answers += 1

                    await ctx.send("Correct! You earned 1 point! 🎉")
                else:
                    streak = 0
                    await ctx.send(f"Wrong! The correct answer was: `{question['correct_answer']}`")
            except asyncio.TimeoutError:
                streak = 0
                await ctx.send(f"Time's up! The correct answer was: `{question['correct_answer']}`")

        self.trivia_streak[user_id] = streak
        self.trivia_scores[user_id] = self.trivia_scores.get(user_id, 0) + points

        save_json(TRIVIA_SCORES_FILE, self.trivia_scores)
        save_json(TRIVIA_STREAK_FILE, self.trivia_streak)

        # Badge Awarding System
        await self.check_and_award_badges(ctx, points, speed_answers, streak)

        embed = discord.Embed(title="Trivia Results", color=int(em.embed(), 16))
        embed.add_field(name="Your Score", value=f"{points} points", inline=False)
        await ctx.send(embed=embed)

        self.trivia_sessions.pop(user_id, None)

    async def check_and_award_badges(self, ctx, points, speed_answers, streak):
        """Checks conditions and awards badges to the user."""
        if points >= 100:
            await self.add_badge(ctx.author.id, "Trivia-Master")  # Earned if score is 8+
        if speed_answers >= 5:
            await self.add_badge(ctx.author.id, "Speedster")  # Earned if 5+ answers were given within 10 seconds
        if streak >= 25:
            await self.add_badge(ctx.author.id, "Streak-King")  # Earned if 10+ correct answers in a row

    @commands.hybrid_command(name="trivia")
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def trivia(self, ctx):
        """Starts a trivia session. Choose a category to begin."""
        view = View()
        categories = {
            "General Knowledge": 9,
            "Science & Nature": 17,
            "Computers": 18,
            "Mathematics": 19
        }
        sub = ""

        for name, category in categories.items():
            button = Button(label=name, custom_id=str(category))

            async def category_callback(interaction, category=category):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("This is not your trivia session!", ephemeral=True)
                    return

                if str(ctx.author.id) in self.trivia_sessions:
                    await interaction.response.send_message("You have a trivia session ongoing!", ephemeral=True)
                    return
                
                match category:
                    case 9:
                        sub = "General Knowledge"
                    case 17:
                        sub = "Science & Nature"
                    case 18:
                        sub = "Computers"
                    case 19:
                        sub = "Mathematics"
                        
                await interaction.response.send_message(f"Fetching questions for {sub}...", ephemeral=True)
                self.trivia_sessions[str(ctx.author.id)] = True
                questions = await fetch_trivia_questions(category)
                if not questions:
                    await ctx.send("No questions available. Try another category.")
                    return

                await self.handle_trivia(ctx, questions)

            button.callback = functools.partial(category_callback)
            view.add_item(button)

        embed = discord.Embed(title="Choose a Trivia Category!", description="Select a category to begin your trivia session.", color=int(em.embed(), 16))
        await ctx.send(embed=embed, view=view)

    @trivia.error
    async def trivia_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"You're on cooldown! Try again in {round(error.retry_after)} seconds <a:cooldown:1321812580679024663>")

    @commands.hybrid_command(name="leaderboard", aliases=["lb"])
    async def leaderboard(self, ctx):
        """Displays the trivia leaderboard."""
        embed = discord.Embed(title="Trivia Leaderboard", description=self.get_leaderboard(), color=discord.Color.gold())
        await ctx.send(embed=embed)

async def setup(bot):
    add_badge = bot.add_badge
    await bot.add_cog(Trivia(bot, add_badge))
    await bot.tree.sync()