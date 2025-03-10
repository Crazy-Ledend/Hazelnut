import random 
import discord
from discord.ext import commands

def minigame_commands(bot, get_user_data, save_data):
    @bot.command(name="simulate")
    async def simulate(ctx, bet: int=None):
        if bet == None:
            await ctx.send("<:discord_cross:1321809722151534645> | Invalid amt of credits to wager")
            return
        games = ["rps", "highlow"]
        chosen_game = random.choice(games)

        user_data = get_user_data(ctx.author.id)

        if bet <= 0 or bet > user_data["wallet"]:
            await ctx.send("Wager must be a positive amount within your Cache <a:notice:1312428458290319503>")
            return

        if chosen_game == "rps":
            # Start Rock-Paper-Scissors game
            await ctx.send("Rock, Paper, Scissors! Choose `r`, `p`, or `s` (rock, paper, scissors).")
            try:
                response = await bot.wait_for(
                    "message",
                    check=lambda message: message.author == ctx.author and message.content.lower() in ["r", "p", "s"],
                    timeout=30,
                )
            except TimeoutError:
                await ctx.send("Time's up! You didn't respond in time.")
                return

            user_choice = response.content.lower()
            choice_map = {"r": "rock", "p": "paper", "s": "scissors"}
            user_choice_full = choice_map[user_choice]
            bot_choice = random.choice(["rock", "paper", "scissors"])
            emoji_map = {"rock": ":rock:", "paper": ":page_facing_up:", "scissors": ":scissors:"}
            await ctx.send(f"**My choice:** {bot_choice} {emoji_map[bot_choice]}")

            if (user_choice_full == "rock" and bot_choice == "scissors") or \
               (user_choice_full == "paper" and bot_choice == "rock") or \
               (user_choice_full == "scissors" and bot_choice == "paper"):
                user_data["wallet"] += bet
                embed = discord.Embed(title="Victory", color=discord.Color.green())
            elif user_choice_full == bot_choice:
                embed = discord.Embed(title="Draw", color=discord.Color.yellow())
            else:
                user_data["wallet"] -= bet
                embed = discord.Embed(title="Defeat", color=discord.Color.red())

            embed.add_field(name="Updated Cache", value=f"{user_data['wallet']} <:credits:1313261430266658867>", inline=True)
            save_data()
            await ctx.send(embed=embed)

        elif chosen_game == "highlow":
            # Start HighLow game
            actual_number = random.randint(1, 100)
            display_number = random.randint(1, 100)

            await ctx.send(f"Displayed Number: {display_number}")
            await ctx.send("Is the actual number `higher` or `lower`? Type your guess (high/low).")

            try:
                response = await bot.wait_for(
                    "message",
                    check=lambda message: message.author == ctx.author and message.content.lower() in ["high", "low"],
                    timeout=30,
                )
            except TimeoutError:
                await ctx.send("<a:notice:1312428458290319503> Time's up! You didn't respond in time")
                return

            guess = response.content.lower()
            if (guess == "high" and actual_number > display_number) or \
               (guess == "low" and actual_number < display_number):
                user_data["wallet"] += bet
                embed = discord.Embed(title="Victory", color=discord.Color.green())
                result_text = f"You guessed correctly! The actual number was {actual_number}."
            else:
                user_data["wallet"] -= bet
                embed = discord.Embed(title="Defeat", color=discord.Color.red())
                result_text = f"You guessed wrong! The actual number was {actual_number}."

            embed.add_field(name="Result", value=result_text, inline=False)
            embed.add_field(name="Updated Cache Balance", value=f"{user_data['wallet']} <:credits:1313261430266658867>", inline=True)
            save_data()
            await ctx.send(embed=embed)

    # Start Coin Flip Command
    @bot.command(name="cf")
    async def coinflip(ctx):
        result = random.choice(['Heads <:heads:1313272604202897430>', 'Tails <:tails:1313272619180621855>'])
        await ctx.send(f"The coin landed on: {result}")
