import discord
from discord.ext import commands

# Constants
ADMIN_ROLE_ID = 1300577397657305239
OWNER_ID = 891319231436685342

class AdminCommands(commands.Cog):
    def __init__(self, bot, get_user_data, save_data):
        self.bot = bot
        self.get_user_data = get_user_data
        self.save_data = save_data

    def has_admin_role(self, ctx):
        return any(ctx.author.id == OWNER_ID or role.id == ADMIN_ROLE_ID for role in ctx.author.roles)
    
    @commands.hybrid_command(name="sync", description="Sync bot commands (Owner Only).")
    async def sync(self, ctx):
        """Sync bot commands to Discord (Owner Only)."""
        if not await self.bot.is_owner(ctx.author):
            return await ctx.send("❌ **You are not authorized to use this command.**", ephemeral=True)

        try:
            await self.bot.tree.sync()
            await ctx.send("✅ **Command tree synced successfully!**", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ **Failed to sync commands:** ```{e}```", ephemeral=True) 

    @commands.hybrid_command(name="inject")
    async def add_coins(self, ctx, user: discord.User, type: str, amount: int = None, item: str = None):
        """Adds credits, stocks, or items to a user's inventory."""
        if not self.has_admin_role(ctx):
            return await ctx.send("**Access Denied:** Missing Admin permissions")

        if amount is None:
            return await ctx.send("Invalid syntax, usage: `;inject <user> <credits/stocks/inventory> <amount> <item: if any>`")

        user_data = self.get_user_data(user.id)
        type = type.lower()

        if type != "credits" and item is None:
            return await ctx.send("<:discord_cross:1321809722151534645> | Invalid syntax. Please provide an item name")

        if type == "credits":
            user_data.setdefault("wallet", 0)
            user_data["wallet"] += amount
            message = f"Injected {amount} credits to {user.mention}'s Cache"

        elif type == "stocks":
            user_data.setdefault("portfolio", {})
            user_data["portfolio"][item] = user_data["portfolio"].get(item, 0) + amount
            message = f"Injected {amount} {item} stocks to {user.mention}'s Portfolio"

        elif type == "inventory":
            user_data.setdefault("inventory", {})
            item = item.lower()
            user_data["inventory"][item] = user_data["inventory"].get(item, 0) + amount
            message = f"Injected {amount} {item} to {user.mention}'s Inventory"

        self.save_data()
        await ctx.send(message)

    @commands.hybrid_command(name="drain")
    async def remove_coins(self, ctx, user: discord.User, type: str, amount: int = None, item: str = None):
        """Removes credits, stocks, or items from a user's inventory."""
        if not self.has_admin_role(ctx):
            return await ctx.send("**Access Denied:** Missing Admin permissions")

        if amount is None:
            return await ctx.send("Invalid syntax, usage: `;drain <user> <credits/stocks/inventory> <amount> <item: if any>`")

        user_data = self.get_user_data(user.id)
        type = type.lower()

        if type != "credits" and item is None:
            return await ctx.send("<:discord_cross:1321809722151534645> | Invalid syntax. Please provide an item name")

        if type == "credits":
            user_data.setdefault("wallet", 0)
            user_data["wallet"] -= amount
            message = f"Drained {amount} credits from {user.mention}'s Cache"

        elif type == "stocks":
            user_data.setdefault("portfolio", {})
            user_data["portfolio"][item] = max(0, user_data["portfolio"].get(item, 0) - amount)
            if user_data["portfolio"][item] == 0:
                del user_data["portfolio"][item]
            message = f"Drained {amount} {item} stocks from {user.mention}'s Portfolio"

        elif type == "inventory":
            user_data.setdefault("inventory", {})
            item = item.lower()
            user_data["inventory"][item] = max(0, user_data["inventory"].get(item, 0) - amount)
            if user_data["inventory"][item] == 0:
                del user_data["inventory"][item]
                if not user_data["inventory"]:
                    del user_data["inventory"]
            message = f"Drained {amount} {item} from {user.mention}'s Inventory"

        self.save_data()
        await ctx.send(message)

    @commands.hybrid_command(name="override")
    async def edit_coins(self, ctx, user: discord.User, type: str, amount: int = None, item: str = None):
        """Sets the exact number of credits, stocks, or items a user has."""
        if not self.has_admin_role(ctx):
            return await ctx.send("**Access Denied:** Missing Admin permissions")

        if amount is None:
            return await ctx.send("Invalid syntax, usage: `;override <user> <credits/stocks/inventory> <amount> <item: if any>`")

        user_data = self.get_user_data(user.id)
        type = type.lower()

        if type != "credits" and item is None:
            return await ctx.send("<:discord_cross:1321809722151534645> | Invalid syntax. Please provide an item name")

        if type == "credits":
            user_data["wallet"] = amount
            message = f"Updated {user.mention}'s Cache to {amount} credits"

        elif type == "stocks":
            user_data.setdefault("portfolio", {})
            user_data["portfolio"][item] = amount
            if user_data["portfolio"][item] == 0:
                del user_data["portfolio"][item]
            message = f"Updated {user.mention}'s Portfolio: {item} set to {amount}"

        elif type == "inventory":
            user_data.setdefault("inventory", {})
            item = item.lower()
            user_data["inventory"][item] = amount
            if user_data["inventory"][item] == 0:
                del user_data["inventory"][item]
                if not user_data["inventory"]:
                    del user_data["inventory"]
            message = f"Updated {user.mention}'s Inventory: {item} set to {amount}"

        self.save_data()
        await ctx.send(message)
        await self.bot.tree.sync()

async def setup(bot):
    get_user_data = bot.get_user_data  
    save_data = bot.save_data 
    await bot.add_cog(AdminCommands(bot, get_user_data, save_data))
