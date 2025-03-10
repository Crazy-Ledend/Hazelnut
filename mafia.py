import discord 
from discord.ext import commands
import asyncio
import random

class MafiaGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    @commands.command()
    async def start_mafia(self, ctx):
        user_id = ctx.author.id
        user_data = self.bot.get_user_data(user_id)
        
        if 'room-card' not in user_data['inventory'] or user_data['inventory']['room-card'] <= 0:
            await ctx.send("You need a Room Card to start a Mafia game!")
            return

        user_data['inventory']['room-card'] -= 1  # Consume Room Card
        if user_data['inventory']['room-card'] <= 0:
            del user_data['inventory']['room-card']
        self.bot.save_data()
        
        embed = discord.Embed(title="Mafia Game Signup", description="React ✅ to join! 5 minutes to enter.", color=discord.Color.green())
        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")
        
        await asyncio.sleep(300)
        message = await ctx.channel.fetch_message(message.id)
        reactions = [r for r in message.reactions if str(r.emoji) == "✅"]
        players = []
        
        if reactions:
            async for user in reactions[0].users():
                if not user.bot:
                    players.append(user)
        
        if len(players) < 4:
            await ctx.send("Not enough players to start!")
            return
        
        # **Create game channel before adding it to self.games**
        game_channel = await ctx.guild.create_text_channel(f"blackout-{ctx.author.name}")
        player_list = ""
        for player in players:
            await game_channel.set_permissions(player, read_messages=True, send_messages=True)
            player_list += f"<@{player}>"
            player_list += " "
        
        self.games[game_channel.id] = {
            "players": {player.id: {"role": None, "alive": True} for player in players},
            "host": ctx.author.id,
            "started": False,
            "channel": game_channel.id
        }
        
        await self.assign_roles(game_channel.id, players)
        await ctx.send(f"Game started in {game_channel.mention}!")
        await game_channel.send(player_list)
        await self.game_loop(ctx, game_channel, players)

    async def assign_roles(self, channel_id, players):
        roles = ["Mafia", "Detective", "Doctor", "Villager", "Mafia Boss", "Mayor", "Wizard"]
        assigned_roles = {}
        
        shuffled_players = players.copy()
        random.shuffle(shuffled_players)
        
        for player in shuffled_players:
            role = random.choice(roles)
            assigned_roles[player.id] = role
            roles.remove(role) if role in roles else None
        
        for player in players:
            await player.send(f"Your role: {assigned_roles[player.id]}")
            self.games[channel_id]['players'][player.id]['role'] = assigned_roles[player.id]

    async def game_loop(self, ctx, channel, players):
        if channel.id not in self.games:
            await ctx.send("Error: Game data not found.")
            return  # Prevent crash if data isn't set up
        while len([p for p in self.games[channel.id]['players'].values() if p['alive']]) > 2:
            await self.action_phase(ctx, channel, players)
            await self.process_actions(ctx, channel)

            await self.voting_phase(ctx, channel, players)
            await asyncio.sleep(5)
        
        winner = "Villagers" if "Mafia" not in [p['role'] for p in self.games[channel.id]['players'].values() if p['alive']] else "Mafia"
        await ctx.send(f"Game over! {winner} wins!")
        await asyncio.sleep(10)
        await channel.delete()

    async def check_game_end(self, ctx, channel):
        """Checks if the game should end based on the remaining players."""
        if channel.id not in self.games:
            return  # Ensure game data exists

        alive_players = {p_id: p_data for p_id, p_data in self.games[channel.id]['players'].items() if p_data['alive']}
        mafia_alive = [p for p in alive_players if alive_players[p]['role'] in ["Mafia", "Mafia Boss"]]
        villagers_alive = [p for p in alive_players if alive_players[p]['role'] not in ["Mafia", "Mafia Boss"]]

        if len(mafia_alive) == 0:
            await channel.send("**Game over! Villagers win! 🎉**")
            await asyncio.sleep(10)
            await channel.delete()
            del self.games[channel.id]
        elif len(mafia_alive) >= len(villagers_alive):
            await channel.send("**Game over! Mafia wins! 🕵️‍♂️**")
            await asyncio.sleep(10)
            await channel.delete()
            del self.games[channel.id]

    async def action_phase(self, ctx, channel, players):
        self.games[channel.id]['actions'] = {}  # Store player actions

        for player_id, data in self.games[channel.id]['players'].items():
            if not data['alive']:  
                continue  # Skip dead players

            player = ctx.guild.get_member(player_id)
            if not player:
                continue  

            role = data['role']
            target_options = [p for p in self.games[channel.id]['players'] if p != player_id and self.games[channel.id]['players'][p]['alive']]

            # Generate Buttons for Targets
            view = discord.ui.View()
            for target_id in target_options:
                target = ctx.guild.get_member(target_id)
                if target:
                    button = discord.ui.Button(label=target.display_name, style=discord.ButtonStyle.primary)
                    button.callback = self.create_action_callback(ctx, channel, player_id, target_id)
                    view.add_item(button)

            try:
                await player.send(f"You're a **{role}**. Select a target for this round:", view=view)
            except discord.Forbidden:
                await channel.send(f"{player.mention}, please enable DMs so you can receive action prompts!")

        await asyncio.sleep(45)  # Wait for players to act

    def create_action_callback(self, ctx, channel, player_id, target_id):
        async def action_callback(interaction: discord.Interaction):
            if interaction.user.id != player_id:
                return  # Ignore actions from other users

            self.games[channel.id]['actions'][player_id] = target_id
            await interaction.response.send_message(f"Action confirmed! You selected <@{target_id}>.", ephemeral=True)

        return action_callback

    async def send_action_dm(self, player, channel_id):
        role = self.games[channel_id]['players'][player.id]['role']
        players = [p for p in self.games[channel_id]['players'].keys() if self.games[channel_id]['players'][p]['alive']]
        
        embed = discord.Embed(title=f"{role} Action", description="Click a player to perform your action.", color=discord.Color.blue())
        view = discord.ui.View()
        
        for p in players:
            button = discord.ui.Button(label=f"{p}", style=discord.ButtonStyle.primary)
            button.callback = lambda i: self.perform_action(i, channel_id, player.id, p)
            view.add_item(button)
        
        try:
            await player.send(embed=embed, view=view)
        except discord.Forbidden:
            pass  # Cannot DM player
        
    async def perform_action(self, interaction, channel_id, user_id, target_id):
        role = self.games[channel_id]['players'][user_id]['role']
        if role == "Mafia":
            self.games[channel_id]['players'][target_id]['alive'] = False
            await interaction.response.send_message(f"You have killed {target_id}", ephemeral=True)
        elif role == "Doctor":
            self.games[channel_id]['players'][target_id]['protected'] = True
            await interaction.response.send_message(f"You protected {target_id}", ephemeral=True)
            
    async def process_actions(self, ctx, channel):
        results = []

        actions = self.games[channel.id]['actions']
        players = self.games[channel.id]['players']

        # Doctor action
        protected = None
        for player_id, target_id in actions.items():
            if players[player_id]['role'] == 'Doctor':
                protected = target_id
                results.append(f"Doctor protected <@{protected}>.")

        # Mafia action
        for player_id, target_id in actions.items():
            if players[player_id]['role'] == 'Mafia' and target_id != protected:
                players[target_id]['alive'] = False
                results.append(f"**Mafia killed <@{target_id}>!**")

        # Wizard action
        for player_id, target_id in actions.items():
            if players[player_id]['role'] == 'Wizard' and 'revived' not in players[player_id]: 
                players[target_id]['alive'] = True
                players[player_id]['revived'] = True  # Wizard can only revive once
                results.append(f"**Wizard revived <@{target_id}>!**")

        # Detective action
        for player_id, target_id in actions.items():
            if players[player_id]['role'] == 'Detective':
                role_info = players[target_id]['role']
                results.append(f"Detective discovered that <@{target_id}> is a **{role_info}**.")

        # Announce results
        if results:
            await channel.send("\n".join(results))
        else:
            await channel.send("No actions took effect this round.")

    async def voting_phase(self, ctx, channel, players):
        """Handles the voting phase in the Mafia game."""

        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        # Get only alive players
        alive_players = [p_id for p_id, p_data in self.games[channel.id]['players'].items() if p_data['alive']]

        if len(alive_players) <= 1:
            await channel.send("Not enough players left to vote.")
            return

        emoji_mapping = {emojis[i]: alive_players[i] for i in range(len(alive_players))}

        # Create embed displaying player-to-emoji mapping
        description = "\n".join([f"{emoji} - <@{player_id}>" for emoji, player_id in emoji_mapping.items()])
        embed = discord.Embed(title="Voting Phase", description=f"React to vote for a player to eliminate!\n\n{description}", color=discord.Color.red())

        message = await channel.send(embed=embed)

        # Add reactions
        for emoji in emoji_mapping.keys():
            await message.add_reaction(emoji)

        await asyncio.sleep(45)  # 45 seconds for voting

        # Fetch updated reactions
        message = await channel.fetch_message(message.id)
        votes = {player_id: 0 for player_id in alive_players}
        voted_users = set()  # Track users who have already voted

        for reaction in message.reactions:
            if reaction.emoji in emoji_mapping:
                async for user in reaction.users():
                    if user.bot or user.id in voted_users or user.id not in alive_players:
                        continue  # Ignore bots and prevent multiple votes
                    votes[emoji_mapping[reaction.emoji]] += 1
                    voted_users.add(user.id)  # Mark user as voted

        # Determine eliminated player
        if votes:
            eliminated = max(votes, key=votes.get)
            self.games[channel.id]['players'][eliminated]['alive'] = False
            await channel.send(f"**<@{eliminated}> has been eliminated!**")

            # Check if the game should end
            await self.check_game_end(ctx, channel)
        else:
            await channel.send("No one was eliminated due to no votes.")

    @commands.command()
    async def end(self, ctx):
        if ctx.channel.id in self.games and self.games[ctx.channel.id]['host'] == ctx.author.id:
            await ctx.channel.delete()
            del self.games[ctx.channel.id]
        else:
            await ctx.send("Only the game host can end the game!")

async def setup(bot):
    await bot.add_cog(MafiaGame(bot))
    await bot.tree.sync()
