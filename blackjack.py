import random
import discord
from discord.ext import commands
from discord.ui import View, Button

# Function to get card value
def get_card_value(card):
    return 10 if card in ['J', 'Q', 'K'] else 11 if card == 'A' else int(card)

# Function to calculate hand value
def calculate_hand(hand):
    value = sum(get_card_value(card) for card in hand)
    ace_count = hand.count('A')

    while value > 21 and ace_count > 0:
        value -= 10  # Convert an Ace from 11 to 1
        ace_count -= 1

    return value

# Blackjack command
class Blackjack(commands.Cog):
    def __init__(self, bot, get_user_data, save_data):
        self.bot = bot
        self.get_user_data = get_user_data
        self.save_data = save_data

    @commands.hybrid_command(aliases=["bj"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def blackjack(self, ctx, bet: int = None):
        # Limit wagering amount
        if bet == None:
            await ctx.send("<:discord_cross:1321809722151534645> | Invalid betting amount, kindly input a valid amount")
            return
        if bet > 500:
            await ctx.send("<:discord_cross:1321809722151534645> | Exceeding Betting Limit! Wager something under 500<:credits:1313261430266658867>")
            return
        
        """Play a game of Blackjack with interactive buttons!"""
        user_id = str(ctx.author.id)
        data = self.get_user_data(user_id)

        if bet > data['wallet'] or bet <= 0:
            embed = discord.Embed(title="⛔ Invalid Bet", description="You don't have enough credits to bet that amount!", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4
        random.shuffle(deck)

        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]

        def hand_display(hand, hide_second=False):
            if hide_second:
                return f"{hand[0]} ❓"
            return ' '.join(hand) + f" (Value: {calculate_hand(hand)})"

        # Initial embed
        embed = discord.Embed(title="🃏 Blackjack!", color=discord.Color.blue())
        embed.add_field(name="Your Hand", value=hand_display(player_hand), inline=False)
        embed.add_field(name="Dealer's Hand", value=hand_display(dealer_hand, hide_second=True), inline=False)
        embed.set_footer(text="Click 'Hit' to draw a card or 'Stand' to end your turn.")
        message = await ctx.send(embed=embed)
                
        # Interactive buttons
        class BlackjackButtons(View):
            def __init__(self, data, save_data):
                super().__init__()
                self.player_busted = False
                self.game_over = False
                self.data = data
                self.save_data = save_data

            async def update_embed(self):
                """Update the embed with the latest game state."""
                embed.clear_fields()
                embed.add_field(name="Your Hand", value=hand_display(player_hand), inline=False)
                embed.add_field(name="Dealer's Hand", value=hand_display(dealer_hand, hide_second=True), inline=False)
                await message.edit(embed=embed)
            def disable_all_items(self):
                for child in self.children:
                    child.disabled = True

            @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
            async def hit(self, interaction: discord.Interaction, button: Button):
                if interaction.user.id != ctx.author.id:
                    return await interaction.response.send_message("You're not in this game!", ephemeral=True)

                player_hand.append(deck.pop())

                if calculate_hand(player_hand) > 21:
                    self.player_busted = True
                    self.game_over = True
                    embed.clear_fields()
                    embed.title = "💥 You Busted!"
                    embed.description = f"Your final hand: {hand_display(player_hand)}\nDealer wins!"
                    data['wallet'] -= bet
                    self.save_data()
                    self.disable_all_items()
                else:
                    embed.clear_fields()
                    embed.add_field(name="Your Hand", value=hand_display(player_hand), inline=False)
                    embed.add_field(name="Dealer's Hand", value=hand_display(dealer_hand, hide_second=True), inline=False)

                await interaction.response.edit_message(embed=embed, view=self if not self.game_over else None)

            @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
            async def stand(self, interaction: discord.Interaction, button: Button):
                if interaction.user.id != ctx.author.id:
                    return await interaction.response.send_message("You're not in this game!", ephemeral=True)

                self.game_over = True

                # Dealer's turn
                while calculate_hand(dealer_hand) < 17:
                    dealer_hand.append(deck.pop())

                dealer_value = calculate_hand(dealer_hand)
                player_value = calculate_hand(player_hand)

                embed.clear_fields()
                embed.title = "🏆 Game Over!"
                embed.add_field(name="Your Final Hand", value=hand_display(player_hand), inline=False)
                embed.add_field(name="Dealer's Final Hand", value=hand_display(dealer_hand), inline=False)

                if dealer_value > 21 or player_value > dealer_value:
                    embed.description = f"You won! 🎉 You earned **{bet * 2}** credits!"
                    data['wallet'] += bet * 2
                elif player_value < dealer_value:
                    embed.description = f"Dealer wins! You lost **{bet}** credits."
                    data['wallet'] -= bet
                else:
                    embed.description = "It's a tie! Your bet is refunded."

                self.save_data()
                self.disable_all_items()

                await interaction.response.edit_message(embed=embed, view=None)

        view = BlackjackButtons(data, self.save_data)
        await message.edit(view=view)
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Please wait for `{error.retry_after:.2f}` seconds before using this command again.")

async def setup(bot):
    get_user_data = bot.get_user_data
    save_data = bot.save_data
    await bot.add_cog(Blackjack(bot, get_user_data, save_data))
