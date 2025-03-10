import discord

# Define the target bot and specific message
TARGET_BOT_ID = 519850436899897346  # Replace with the ID of the target bot
TARGET_EMBED_TITLE = "Take Action"    # Replace with the message you want to identify
TARGET_EMBED_DESCRIPTION = "Take Action"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

def ping(bot):

    @bot.event
    async def on_message(message):
        # Ignore messages from the bot itself
        if message.author == bot.user:
            return

        # Check if the message is from the target bot
        if message.author.id == TARGET_BOT_ID:
            print(f"Message from target bot: {message.content}")

            if message.embeds:
                for embed in message.embeds:
                    # Access embed attributes like title and description
                    if (embed.title == TARGET_EMBED_TITLE or 
                        embed.description == TARGET_EMBED_DESCRIPTION):
                        print("Raid detected!")
                        await message.channel.send("<@891319231436685342>")
                        return