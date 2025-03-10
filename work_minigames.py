import discord
import random
from discord.ext import commands
import asyncio
from datetime import timedelta

# Minigame: Memory Game
async def memory_game(ctx, response_method, yield_amount):
    # Generate a random sequence of numbers
    sequence = [random.randint(1, 9) for _ in range(5)]
    sequence_str = ' '.join(map(str, sequence))

    # Send the sequence to the user
    embed = discord.Embed(title="Memory Game", color=int("69c9ce", 16))
    embed.add_field(name="Memorize this sequence:", value=f"`{sequence_str}`", inline=False)
    embed.set_footer(text="You have 10 seconds to memorize it!")
    sent_message = await response_method(embed=embed)  # Save the sent message

    # Wait 10 seconds
    await asyncio.sleep(3)

    # Edit the embed to ask the user to recall the sequence
    new_embed = discord.Embed(title="Memory Game", color=int("69c9ce", 16))
    new_embed.add_field(name="Recall the sequence!", value="Type the sequence you just saw in order:", inline=False)
    await sent_message.edit(embed=new_embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        user_response = await ctx.bot.wait_for('message', timeout=15.0, check=check)
        if user_response.content == sequence_str:
            # Correct response
            embed = discord.Embed(title="Memory Game", color=discord.Color.green())
            embed.add_field(name="Success!", value="You recalled the sequence correctly. Full credits awarded!", inline=False)
            await response_method(embed=embed)
            return yield_amount  # Full credits
        else:
            # Incorrect response
            embed = discord.Embed(title="Memory Game", color=discord.Color.red())
            embed.add_field(name="Incorrect!", value="You failed to recall the sequence. Half credits awarded.", inline=False)
            await response_method(embed=embed)
            return yield_amount // 2  # Half credits
    except asyncio.TimeoutError:
        # Timeout
        embed = discord.Embed(title="Memory Game", color=discord.Color.red())
        embed.add_field(name="Timeout!", value="You didn't respond in time. Half credits awarded.", inline=False)
        await response_method(embed=embed)
        return yield_amount // 2  # Half credits
    
# Math Sprint Minigame
async def math_sprint(ctx, response_method, yield_amount):
    num1, num2 = random.randint(1, 50), random.randint(1, 50)
    operator = random.choice(["+", "-", "*"])

    if operator == "-":
        problem = f"{max(num1, num2)} {operator} {min(num1, num2)}"  # Ensuring non-negative results
    else:
        problem = f"{num1} {operator} {num2}"

    correct_answer = eval(problem)

    embed = discord.Embed(title="Math Sprint", color=discord.Color.blue())
    embed.add_field(name="Solve this problem:", value=f"`{problem}`", inline=False)
    embed.set_footer(text="You have 10 seconds to answer!")
    await response_method(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lstrip('-').isdigit()

    try:
        user_response = await ctx.bot.wait_for('message', timeout=10.0, check=check)

        if int(user_response.content) == correct_answer:
            embed = discord.Embed(title="Math Sprint", color=discord.Color.green())
            embed.add_field(name="Correct!", value="You solved the problem. Full credits awarded!", inline=False)
            await response_method(embed=embed)
            return yield_amount
        else:
            embed = discord.Embed(title="Math Sprint", color=discord.Color.red())
            embed.add_field(name="Wrong!", value=f"The correct answer was `{correct_answer}`. Half credits awarded.", inline=False)
            await response_method(embed=embed)
            return yield_amount // 2
    except asyncio.TimeoutError:
        embed = discord.Embed(title="Math Sprint", color=discord.Color.red())
        embed.add_field(name="Timeout!", value=f"The correct answer was `{correct_answer}`. Half credits awarded.", inline=False)
        await response_method(embed=embed)
        return yield_amount // 2

# Word Scramble Minigame
async def word_scramble(ctx, response_method, yield_amount):
    words = ["Python", "Discord", "Minigame", "Bot", "Developer", "Hazelnut", "Credits", "Vault"]
    chosen_word = random.choice(words)
    scrambled_word = ''.join(random.sample(chosen_word, len(chosen_word)))

    embed = discord.Embed(title="Word Scramble", color=discord.Color.purple())
    embed.add_field(name="Unscramble this word:", value=f"`{scrambled_word}`", inline=False)
    embed.set_footer(text="You have 15 seconds to answer!")
    sent_message = await response_method(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        user_response = await ctx.bot.wait_for('message', timeout=15.0, check=check)
        if user_response.content.lower() == chosen_word.lower():
            embed = discord.Embed(title="Word Scramble", color=discord.Color.green())
            embed.add_field(name="Correct!", value="You unscrambled the word. Full credits awarded!", inline=False)
            await response_method(embed=embed)
            return yield_amount  # Full credits
        else:
            embed = discord.Embed(title="Word Scramble", color=discord.Color.red())
            embed.add_field(name="Wrong!", value=f"The correct word was `{chosen_word}`. Half credits awarded.", inline=False)
            await response_method(embed=embed)
            return yield_amount // 2  # Half credits
    except asyncio.TimeoutError:
        embed = discord.Embed(title="Word Scramble", color=discord.Color.red())
        embed.add_field(name="Timeout!", value=f"The correct word was `{chosen_word}`. Half credits awarded.", inline=False)
        await response_method(embed=embed)
        return yield_amount // 2  # Half credits

# emoji memory
async def emoji_memory(ctx, response_method, yield_amount):
    # List of possible emojis
    emojis = ["😀", "🤖", "🚀", "🐱", "🌟", "⚡", "🍕", "🎶", "🔥", "🏆", "📚", "🎮", "🌰"]

    # Choose one random emoji
    chosen_emoji = random.choice(emojis)

    # Send the emoji to the user
    embed = discord.Embed(title="Emoji Memory", color=discord.Color.gold())
    embed.add_field(name="Memorize this emoji:", value=f"`{chosen_emoji}`", inline=False)
    embed.set_footer(text="You have 3 seconds to memorize it!")
    sent_message = await response_method(embed=embed)

    # Wait for 3 seconds before clearing the message
    await asyncio.sleep(3)

    # Edit the embed to hide the emoji and ask the user to recall it
    new_embed = discord.Embed(title="Emoji Memory", color=discord.Color.gold())
    new_embed.add_field(name="Which emoji was shown?", value="Type the emoji exactly as you saw it:", inline=False)
    new_embed.set_footer(text="You have 5 seconds to respond!")
    await sent_message.edit(embed=new_embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        user_response = await ctx.bot.wait_for('message', timeout=5.0, check=check)
        if user_response.content.strip() == chosen_emoji:
            # Correct response
            embed = discord.Embed(title="Emoji Memory", color=discord.Color.green())
            embed.add_field(name="Correct!", value="You remembered the emoji correctly! Full credits awarded!", inline=False)
            await response_method(embed=embed)
            return yield_amount  # Full credits
        else:
            # Incorrect response
            embed = discord.Embed(title="Emoji Memory", color=discord.Color.red())
            embed.add_field(name="Wrong!", value=f"The correct emoji was `{chosen_emoji}`. Half credits awarded.", inline=False)
            await response_method(embed=embed)
            return yield_amount // 2  # Half credits
    except asyncio.TimeoutError:
        # Timeout
        embed = discord.Embed(title="Emoji Memory", color=discord.Color.red())
        embed.add_field(name="Timeout!", value=f"The correct emoji was `{chosen_emoji}`. Half credits awarded.", inline=False)
        await response_method(embed=embed)
        return yield_amount // 2  # Half credits
    
# Function to handle minigame selection
async def play_minigame(ctx, response_method, yield_amount):
    minigames = [memory_game, math_sprint, word_scramble, emoji_memory]  # Add other minigames here as needed
    chosen_game = random.choice(minigames)
    return await chosen_game(ctx, response_method, yield_amount)
