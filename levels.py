import json
import os
import math
import discord
import asyncio
from discord.ext import commands
from time import time

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix=";", intents=intents)

class LevelSystem:
    def __init__(self, data_file="levels_data.json"):
        self.data_file = data_file
        self.data = self.load_data()
        self.lock = asyncio.Lock()
        
    def reload_data(self):
        self.data = self.load_data()
        
    def check_and_update_level(self, user_id):
        current_xp, next_level_xp = self.get_progress(user_id)
        current_level = self.get_level(user_id)
    
        # Recalculate level if necessary
        while current_xp >= next_level_xp:
            current_xp -= next_level_xp
            self.data[user_id]['level'] += 1
            next_level_xp = self.calculate_next_level_xp(self.data[user_id]['level'])
    
        # Update progress after recalculation
        self.data[user_id]['xp'] = current_xp

        # Save data to ensure changes persist
        self.save_data()

        
    def load_data(self):
        """Load user data from the JSON file."""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                return json.load(f)
        else:
            return {}

    def save_data(self):
        """Save user data to the JSON file."""
        with open(self.data_file, "w") as f:
            json.dump(self.data, f, indent=4)

    def get_user_data(self, user_id):
        """Get the data for a specific user, initializing it if necessary."""
        if user_id not in self.data:
            self.data[user_id] = {"xp": 0, "level": 1}  # Initialize new user with level 1 and xp 0
            self.save_data()
        return self.data[user_id]
    
    async def add_xp(self, user_id, xp):
        async with self.lock:
            user_data = self.get_user_data(user_id)
            user_data["xp"] += xp

        leveled_up = False
        while user_data["xp"] >= self.xp_to_next_level(user_data["level"]):
            user_data["xp"] -= self.xp_to_next_level(user_data["level"])
            user_data["level"] += 1
            leveled_up = True

        self.save_data()
        return leveled_up  # Return True if the user leveled up

    def xp_to_next_level(self, level):
        """Calculate the XP required for the next level."""
        return int(50 * (1.5 ** (level - 1)))

    def get_progress(self, user_id):
        """Get user's XP progress toward the next level."""
        user_data = self.get_user_data(user_id)
        current_xp = user_data["xp"]
        next_level_xp = self.xp_to_next_level(user_data["level"])
        return current_xp, next_level_xp

    def get_level(self, user_id):
        """Get the user's current level."""
        return self.get_user_data(user_id)["level"]
