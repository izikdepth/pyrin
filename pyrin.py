import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

# intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # Enable the message content intent

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print("Bot is ready!")

async def load_cogs():
    Cogs_list = [
        "stats"
    ]

    for Cog in Cogs_list:
        await bot.load_extension(f'Cogs.{Cog}')  # Use await to load extensions

# Run the bot and load cogs asynchronously
async def main():
    async with bot:
        await load_cogs()
        Token = os.getenv("PYRIN_BOT")
        await bot.start(Token)

# Use asyncio.run to start the main function
if __name__ == "__main__":
    asyncio.run(main())