import random
import discord
from discord.ext import commands, tasks
import json
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from urllib.request import urlopen
import io
import embed as em

image_url = 'https://t3.ftcdn.net/jpg/01/36/05/94/360_F_136059498_i1vEZZYQJFz4oUKMLnTRHkkQwLEaYSQ6.jpg' 
img_data = urlopen(image_url).read()
img = mpimg.imread(io.BytesIO(img_data), format='jpg')

fig, ax = plt.subplots()

# Set the image as the background
ax.imshow(img, extent=[0, 300, 0, 250], aspect='auto')


def stock_commands(bot, get_user_data, save_data, save_stocks, stocks):

    # Command to display stock prices
    @bot.command(name="stocks")
    async def show_stocks(ctx):
        embed = discord.Embed(title="<:stockr:1312679587783770132> CryoStock Nexus", color=int(em.embed(), 16))
        for stock, data in stocks.items():
            embed.add_field(name=f"{stock} ({data['symbol']})", value=f"Price: {data['price']} <:credits:1313261430266658867>", inline=False)
        await ctx.send(embed=embed)

    @bot.command(name="virtualize")
    async def virtualize(ctx):
        # Calculate number of updates for the last day (e.g., 5-minute intervals, 288 updates in a day)
        updates_per_day = 108  # 5-minute intervals in a day
        last_day = updates_per_day  # Only the last day of data

        # Dynamically adjust figure size based on filtered data
        max_length = min(last_day, max(len(data["price_history"]) for data in stocks.values()))
        width = max(6, max_length // 10)  # Adjust width, minimum is 6
        height = max(4, len(stocks) * 1.5)  # Adjust height based on number of stocks

        # Create a new figure with dynamic size
        fig, ax = plt.subplots(figsize=(width, height))
        
        # Set the background image
        ax.imshow(img, extent=[0, max_length + 10, 0, max(200, len(stocks) * 50)], aspect='auto')

        # Plot stock price histories for the last day
        for stock, data in stocks.items():
            recent_history = data["price_history"][-last_day:]  # Slice the last day of data
            ax.plot(recent_history, label=stock)

        # Add title, labels, and legend
        ax.set_title("CryoStock Price History (Last 1 Day)")
        ax.set_xlabel("Time (Updates)")
        ax.set_ylabel("Price (Credits)")
        ax.legend()

        # Save the figure and close it
        plt.savefig("stock_price_history.png", bbox_inches="tight")
        plt.close(fig)

        # Create an embed and attach the image
        embed = discord.Embed(
            title="📈 CryoStock Price History",
            description="A visualization of CryoStock trends over the last 1 day.",
            color=int("60ffff", 16)
        )
        embed.set_image(url="attachment://stock_price_history.png")

        # Send the embed with the image
        file = discord.File("stock_price_history.png", filename="stock_price_history.png")
        await ctx.send(file=file, embed=embed)

    # Command to buy stocks
    @bot.command(name="buy")
    async def buy_stock(ctx, stock_symbol: str, amount: int):
        for stock_name, data in stocks.items():
            if stock_symbol.upper() == data["symbol"]:
                user_data = get_user_data(ctx.author.id)
                total_price = data["price"] * amount

                if total_price > user_data["wallet"]:
                    await ctx.send("You don't have enough credits to buy these CryoStocks.")
                    return

                user_data["wallet"] -= total_price
                user_data.setdefault("portfolio", {}).setdefault(stock_name, 0)
                user_data["portfolio"][stock_name] += amount
                save_data()

                # Increase demand
                data["demand"] += amount

                await ctx.send(f"You bought {amount} shares of {stock_name} ({data['symbol']}) for {total_price} Credits")
                return

        await ctx.send("Invalid stock symbol. Check available CryoStocks with `!stocks`")

    # Command to sell stocks
    @bot.command(name="sell")
    async def sell_stock(ctx, stock_symbol: str, amount: int):
        for stock_name, data in stocks.items():
            if stock_symbol.upper() == data["symbol"]:
                user_data = get_user_data(ctx.author.id)
                if "portfolio" not in user_data or stock_name not in user_data["portfolio"]:
                    await ctx.send("You don't own any shares of this CryoStock")
                    return

                if user_data["portfolio"][stock_name] < amount:
                    await ctx.send("You don't own enough shares to sell this amount")
                    return

                total_price = data["price"] * amount
                user_data["wallet"] += total_price
                user_data["portfolio"][stock_name] -= amount
                if user_data["portfolio"][stock_name] == 0:
                    del user_data["portfolio"][stock_name]
                save_data()

                # Decrease demand
                data["demand"] -= amount

                await ctx.send(f"You sold {amount} shares of {stock_name} for {total_price} Credits")
                return

        await ctx.send("Invalid stock symbol. Check available CryoStocks with `!stocks`")

    # Command to view portfolio
    @bot.command(name="portfolio")
    async def portfolio(ctx):
        user_data = get_user_data(ctx.author.id)
        if "portfolio" not in user_data or not user_data["portfolio"]:
            await ctx.send("You don't own any CryoStocks yet. Buy some with `;buy`!")
            return

        embed = discord.Embed(title="📊 Your Portfolio", color=discord.Color.gold())
        total_value = 0
        for stock_name, shares in user_data["portfolio"].items():
            stock_value = shares * stocks[stock_name]["price"]
            total_value += stock_value
            embed.add_field(name=stock_name, value=f"Shares: {shares}, Value: {stock_value} <:credits:1313261430266658867>", inline=False)

        embed.add_field(name="Net Value", value=f"{total_value} <:credits:1313261430266658867>", inline=False)
        await ctx.send(embed=embed)
