import discord
from discord.ext import commands

class Trade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_user_data = bot.get_user_data  # Function from main file
        self.save_data = bot.save_data  # Function from main file

    @commands.hybrid_command(name="give", description="Give credits to another user.")
    async def give(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("Amount must be greater than zero!")

        giver_id = str(ctx.author.id)
        receiver_id = str(member.id)

        giver_data = self.get_user_data(giver_id)
        receiver_data = self.get_user_data(receiver_id)

        if giver_data["wallet"] < amount:
            return await ctx.send("You don't have enough credits to give!")

        # Transfer credits
        giver_data["wallet"] -= amount
        receiver_data["wallet"] += amount

        self.save_data()

        await ctx.send(f"{ctx.author.mention} has given `{amount}` credits <:credits:1313261430266658867> to {member.mention}!")

    @commands.hybrid_command(name="gift", description="Gift an item to another user.")
    async def gift(self, ctx, member: discord.Member, item: str, amount: int=1):
        if amount <= 0:
            return await ctx.send("Amount must be greater than zero!")

        giver_id = str(ctx.author.id)
        receiver_id = str(member.id)

        giver_data = self.get_user_data(giver_id)
        receiver_data = self.get_user_data(receiver_id)
        addons = ""
        if item in ["rose", "pink-rose", "love-letter", "chocolate", "chocolate-box", "teddy-bear", "teddy-heart", "valentine-gem"]:
            addons = ":sparkling_heart:"
        
        # Ensure giver has the item and enough quantity
        if item not in giver_data.get("inventory", {}) or giver_data["inventory"][item] < amount:
            return await ctx.send("You don't have enough of this item to gift!")

        # Deduct item from giver
        giver_data["inventory"][item] -= amount
        if giver_data["inventory"][item] == 0:
            del giver_data["inventory"][item]

        # Add item to receiver
        receiver_data.setdefault("inventory", {})
        receiver_data["inventory"][item] = receiver_data["inventory"].get(item, 0) + amount

        self.save_data()

        await ctx.send(f"{ctx.author.mention} has gifted `{amount}` {item}(s) to {member.mention} {addons}!")

async def setup(bot):
    await bot.add_cog(Trade(bot))
