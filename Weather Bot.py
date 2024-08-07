import discord
import requests
import asyncio
from datetime import datetime
from discord.ext import commands

TOKEN = 'YOUR TOKEN HERE'
WEATHER_API_KEY = 'OPEN WEATHER API KEY HERE'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

# Define a dictionary to map weather descriptions to emojis
weather_emojis = {
    'clear sky': '☀️',
    'few clouds': '⛅',
    'scattered clouds': '☁️',
    'broken clouds': '☁️',
    'shower rain': '🌧️',
    'rain': '🌧️',
    'thunderstorm': '⛈️',
    'snow': '❄️',
    'mist': '🌫️'
}

# Map wind directions to cardinal directions
wind_directions = {
    'N': 0,
    'NNE': 22.5,
    'NE': 45,
    'ENE': 67.5,
    'E': 90,
    'ESE': 112.5,
    'SE': 135,
    'SSE': 157.5,
    'S': 180,
    'SSW': 202.5,
    'SW': 225,
    'WSW': 247.5,
    'W': 270,
    'WNW': 292.5,
    'NW': 315,
    'NNW': 337.5
}

# ...

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="with the weather"))
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def weather(ctx, *, location: str):
    location_parts = location.split(',')
    if len(location_parts) != 2:
        await ctx.send("Please provide both the city and the country (e.g., `.weather Paris, FR`)")
        return

    city_name, country_code = [part.strip().capitalize() for part in location_parts]
    response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city_name},{country_code}&appid={WEATHER_API_KEY}')
    data = response.json()

    if response.status_code == 200:
        # Retrieve weather information
        weather_description = data['weather'][0]['description'].capitalize()
        temperature_kelvin = data['main']['temp']
        temperature_celsius = temperature_kelvin - 273.15
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        wind_degrees = data['wind']['deg']

        # Convert wind degrees to cardinal direction
        wind_direction = "Unknown"
        for direction, angle in wind_directions.items():
            if (angle - 22.5) <= wind_degrees < (angle + 22.5):
                wind_direction = direction
                break

        # ...

        # Create an embedded message for the current weather
        embed = discord.Embed(title=f"Current Weather in {city_name}, {country_code}", description=f"Here's the current weather for {city_name}, {country_code}:", color=0x3498db)
        embed.add_field(name="Description", value=f"{weather_emojis.get(weather_description.lower(), '❓')} {weather_description}", inline=False)
        embed.add_field(name="Temperature", value=f"🌡️ {temperature_celsius:.1f}°C", inline=False)
        embed.add_field(name="Humidity", value=f"{humidity}% Relative Humidity", inline=False)
        embed.add_field(name="Wind", value=f"💨 {wind_speed} m/s from {wind_direction}", inline=False)
        embed.add_field(name="Interactive Map", value=f"[OpenStreetMap](https://www.openstreetmap.org/?mlat={data['coord']['lat']}&mlon={data['coord']['lon']}#map=13/{data['coord']['lat']}/{data['coord']['lon']})", inline=False)

        embed.set_footer(text=f"Requested by {ctx.author.display_name} at {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")

        await ctx.send(embed=embed)
    else:
        await ctx.send("Sorry, I couldn't fetch the weather information for that location.")

bot.run(TOKEN)
