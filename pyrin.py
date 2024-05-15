import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix="/")

#intents
intents = discord.Intents.default()
intents.members = True

@bot.event
async def on_ready():
    print("Bot is ready!")

Cogs_list = [
    "stats", 
]

for Cog in Cogs_list:
    bot.load_extension(f'Cogs.{Cog}')

Token = os.getenv("PYRIN_BOT")
bot.run(Token)