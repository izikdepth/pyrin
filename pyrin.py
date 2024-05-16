import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

bot = commands.Bot(command_prefix="/")

# intents
intents = discord.Intents.default()
intents.members = True

@bot.event
async def on_ready():
    print("Bot is ready!")

async def load_extensions():
    Cogs_list = ["stats"]  
    for cog_name in Cogs_list:
        try:
            bot.load_extension(f'Cogs.{cog_name}')
            print(f"Loaded extension: Cogs.{cog_name}")
        except ImportError as e:
            print(f"Failed to load extension: Cogs.{cog_name}. Error: Module not found {e}.")
        except AttributeError as e:
            print(f"Failed to load extension: Cogs.{cog_name}. Error: Attribute error {e}.")



async def main():
    await load_extensions()
    Token = os.getenv("PYRIN_BOT")
    await bot.start(Token)

if __name__ == "__main__":
    asyncio.run(main())
