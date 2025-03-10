import aiohttp
import sqlite3
import random

# 📖 Get Dictionary Meaning
async def get_dictionary_meaning(word):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}") as response:
            data = await response.json()
            if "title" in data:
                return "❌ Word not found!"
            return data[0]["meanings"][0]["definitions"][0]["definition"]

# 🌦️ Get Weather Info
async def get_weather(city):
    API_KEY = "47d9087cc25e483ab2345800250603"
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

            # Error handling: Check if 'error' key exists
            if "error" in data:
                return "❌ City not found! Please enter a valid city."

            # Extract weather details
            location = data['location']['name']
            country = data['location']['country']
            temp_c = data['current']['temp_c']
            condition = data['current']['condition']['text']
            humidity = data['current']['humidity']
            wind_kph = data['current']['wind_kph']
            
            # Weather sets
            weather_conditions = {
                "sunny": ["Sunny", "Clear"],
                "cloudy": ["Partly Cloudy", "Cloudy", "Overcast"],
                "rainy": [
                    "Patchy rain possible", "Light rain shower", "Light rain", "Moderate rain at times", 
                    "Moderate rain", "Heavy rain at times", "Heavy rain", "Torrential rain shower"
                ],
                "thunder": ["Patchy light rain with thunder", "Moderate or heavy rain with thunder", "Thundery outbreaks possible"],
                "snowy": [
                    "Patchy snow possible", "Light snow", "Moderate snow", "Heavy snow", 
                    "Ice pellets", "Patchy light snow", "Patchy moderate snow", "Moderate or heavy snow showers"
                ],
                "windy": ["Mist", "Fog", "Freezing fog", "Blowing snow"],
                "sleet": [
                    "Patchy sleet possible", "Light sleet", "Moderate or heavy sleet", 
                    "Patchy freezing drizzle possible", "Freezing drizzle","Heavy freezing drizzle"
                ],
                "severe": ["Blizzard", "Hurricane", "Tornado"]
            }
            
            # Emoji set
            condition_emojis = {
                "severe": "<a:severe:1347252248182259726>",
                "thunder": "<a:thunder_storm:1347251166181982218>",
                "sunny": "<:sunny:1347254994402934906>",
                "rainy": "<a:rainy_c:1347250679671947460>",
                "cloudy": ":cloud:",
                "sleet": "<:sleet:1347252004040347801>",
                "windy": "<:windy:1347251645146333216>",
                "snowy": "<:snowy:1347251254648242310>"
            }
            
            condition_emoji = ""
            for weather_condition in weather_conditions:
                for i in weather_condition:
                    if condition == i:
                        condition_emoji = condition_emojis[weather_condition]
                        break
                    
            if not condition_emoji:
                condition_emoji = "<:default:1347255357205909565>"
            # Format response for Discord bot
            return (
                f"<:Location:1347247863746265128> | **Weather in {location}, {country}:**\n"
                f"🌡️ | **Temperature:** {temp_c}°C\n"
                f"{condition_emoji} | **Condition:** {condition}\n"
                f"<:humidity:1347248304538259539> | **Humidity:** {humidity}%\n"
                f"<:windw:1347247844385361963> | **Wind Speed:** {wind_kph} kph"
            )

# 🤣 Get Random Meme
async def get_random_meme():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://meme-api.com/gimme") as response:
            data = await response.json()
            return data["url"]
