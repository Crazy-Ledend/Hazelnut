import discord
import os
import json
from discord.ext import commands
from datetime import datetime, timedelta
import effects as e

# Shop items
shop_items = {
    'coffee': {'emoji': "<:Coffee:1322192609665486868>", 'price': 100, 'description': 'Keeps you dedicated at work, earning u extra credits'},
    'soda': {'emoji': "<:Soda:1322192620872667146>",'price': 150, 'description': 'Hav a sip at this cold delicacy!'},
    'dice': {'emoji': "<:Dice:1322193544055881740>",'price': 50, 'description': 'Thinking of playing a game? pick the die!'},
    #'valentines-box': {'emoji': "<a:GiftBox:1338190780124102718>",'price': 250,'description': "A box that is filled with love and commitment!"},
    'jackpot-coin': {'emoji': "<a:coinn:1334244164203712548>",'price': 20000, 'description': 'Gamble your chances to double the credits in your wallet!'},
    'phone': {'emoji': "<:Phone:1326046330170249267>",'price': 20000, 'description': 'A multi purpose TechTool to be used!'}
}

items = {
    'coffee': {'emoji': "<:Coffee:1322192609665486868>", 'price': 100, 'description': 'Keeps you dedicated at work, earning u extra credits'},
    'soda': {'emoji': "<:Soda:1322192620872667146>",'price': 150, 'description': 'Hav a sip at this cold delicacy!'},
    'dice': {'emoji': "<:Dice:1322193544055881740>",'price': 50, 'description': 'Thinking of playing a game? pick the die!'},
    'jackpot-coin': {'emoji': "<a:coinn:1334244164203712548>",'price': 20000, 'description': 'Gamble your chances to double the credits in your wallet!'},
    'phone': {'emoji': "<:Phone:1326046330170249267>",'price': 20000, 'description': 'A multi purpose TechTool to be used!'},
    'rose': {'emoji': "<a:redrose:1338179361299239024>",'price': 143,'description': "A timeless symbol of love, perfect for expressing your deepest feelings"},
    'pink-rose': {'emoji': "<a:pinkrose:1338179366596907080>",'price': 143,'description': "A delicate pink rose, representing admiration and sweet affection"},
    'love-letter': {'emoji': "<:loveletter:1338179935801446462>",'price': 143,'description': "A heartfelt letter filled with words of love and devotion"},
    'chocolate': {'emoji': "<:chocolate:1338180103892369522>",'price': 143,'description': "Sweet, rich, and irresistible—just like your love"},
    'chocolate-box': {'emoji': "<a:ChocolateBox:1338180115817041960>",'price': 143,'description': "A box of chocolates, because love should always be a little sweet"},
    'teddy-bear': {'emoji': "<:teddybear:1338182716818198705>",'price': 143,'description': "A cuddly teddy bear to remind your special someone of your warmth"},
    'teddy-heart': {'emoji': "<:teddyheart:1338182761231417405>",'price': 143,'description': "A teddy bear holding a heart, symbolizing love and comfort"},
    'valentine-gem': {'emoji': "<a:ValentineHeart:1338183796716994632>",'price': 9999,'description': "A rare and precious gem, shining as bright as true love"},
    'valentines-box': {'emoji': "<a:GiftBox:1338190780124102718>",'price': 250,'description': "A box that is filled with love and commitment!"},
    'room-card': {'emoji': "<:room_card:1343316996741271622>",'price': 100,'description': "Start a game of Blackout and hav fun with your friends!"}
}


def shop_commands(bot, get_user_data, save_data):
    # Shop commands
    @bot.command()
    async def shop(ctx):
        embed = discord.Embed(title="**<:shop:1324983208982351872> Hazel Stores**", colour=discord.Colour(0xcd974f))
        for item, details in shop_items.items():
            embed.add_field(name=f"{shop_items[item]['emoji']} {item.capitalize()}", value=f"{shop_items[item]['description']}\n`;purchase {item} <amt>`\nCost: {shop_items[item]['price']} <:credits:1313261430266658867>", inline=False)
        
        embed.set_image(url="attachment://hazel.stores.jpeg")

        # Send the embed with the image
        file = discord.File("hazel.stores.jpeg", filename="hazel.stores.jpeg")
        await ctx.send(file=file, embed=embed)

    @bot.command(name="purchase", aliases=["p"])
    async def buy(ctx, item_name: str = None, amount=1):
        user_id = ctx.author.id
        user_data = get_user_data(user_id)
        
        if item_name == None:
            await ctx.send("No items mentioned!")
            return
        
        item_name = item_name.lower()

        if item_name not in items:
            await ctx.send("Item not found in the shop!")
            return
        
        item_price = shop_items[item_name]['price'] * amount
        if user_data["wallet"] < item_price:
            await ctx.send("You don't have enough credits to buy this item!")
            return
        
        # Purchase the item
        user_data["wallet"] -= item_price
        user_data.setdefault("inventory", {}).setdefault(item_name, 0)
        user_data["inventory"][item_name] += amount
        save_data()

        if amount == 1:
            if item_name[0] in 'aeiou': 
                await ctx.send(f"{ctx.author.mention}, you bought an {item_name}! {items[item_name]["emoji"]}")
            else:
                await ctx.send(f"{ctx.author.mention}, you bought a {item_name}! {items[item_name]["emoji"]}")
        
        else:
            await ctx.send(f"{ctx.author.mention}, you bought `{amount}` {item_name}s! {items[item_name]["emoji"]}")

    @bot.command(name = "inventory", aliases = ["inv"])
    async def inventory(ctx):
        user_id = ctx.author.id
        user_data = get_user_data(user_id)

        if "inventory" not in user_data:
            await ctx.send("Your inventory is empty!")
            return
        
        embed = discord.Embed(title="Inventory", color=discord.Color(0xae5919))
        total_value = 0
        for item_name, amount in user_data["inventory"].items():
            item_value = amount * items[item_name]["price"]
            total_value += item_value

            embed.add_field(name=f"{items[item_name]["emoji"]} {item_name.capitalize()}", value=f"Quantity: `x{amount}`, Value: {item_value} <:credits:1313261430266658867>", inline=False)

        embed.add_field(name="Net Value", value=f"{total_value} <:credits:1313261430266658867>", inline=False)
        await ctx.send(embed=embed)

    @bot.command()
    async def use(ctx, item_name: str = None, receiver: discord.Member = None):
        user_id = ctx.author.id
        user_data = get_user_data(user_id)

        if not user_data["inventory"]:
            await ctx.send("Your inventory is empty!")
        if item_name is None:
            await ctx.send("Please specify an item to use.")
            return

        item_name = item_name.lower()

        if item_name not in user_data["inventory"] or user_data["inventory"][item_name] <= 0:
            await ctx.send(f"You don't have any {item_name}s in your inventory!")
            return

        # Use item logic
        if item_name != 'phone':
            user_data["inventory"][item_name] -= 1
            if user_data["inventory"][item_name] == 0:
                del user_data["inventory"][item_name]

        # Apply effects
        if item_name == 'coffee':
            await ctx.send(e.coffee(ctx, user_data))
        elif item_name == 'phone':
            await e.phone(ctx, bot)
        elif item_name == 'jackpot-coin':
            await ctx.send(e.jackpot_coin(ctx, user_data, save_data))
        elif item_name == 'dice':
            await ctx.send(e.dice(ctx))
        elif item_name == 'valentines-box':
            await ctx.send(e.valentines_box(ctx, user_data))
        elif item_name == 'love-letter':
            await e.love_letter(ctx)
        elif item_name == 'chocolate':
            await ctx.send(e.chocolate(ctx, user_data))
        elif item_name == 'rose' or item_name == 'pink-rose':
            if receiver == None:
                user_data["inventory"][item_name] += 1
                await ctx.send("*Oh come on.. Tag someone...*")
            else:
            	await e.rose(ctx, receiver)
        else:
            await ctx.send(f"{ctx.author.mention}, you used a {item_name}! {items[item_name]["emoji"]}")
        save_data()
