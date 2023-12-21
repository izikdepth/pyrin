import discord
from discord.ext import commands, tasks
import requests
import json
from requests.exceptions import RequestException,ConnectTimeout
import telegram
import os
from dotenv import load_dotenv


load_dotenv()


bot = telegram.Bot(token=os.getenv("TELEGRAM_BOT"))

telegram_chat_id = -1001534672988 #telegram chat id


intents = discord.Intents(guilds=True)
client = discord.Client(intents=intents)
intents.members = True



#verified role id, you can get this by right clicking the role on discord and copy

def get_price():
   url = "https://api.livecoinwatch.com/coins/single"
   payload = json.dumps({
       "currency": "USD",
       "code": "PYI",
       "meta": True
   })

   headers = {
       'content-type': 'application/json',
       'x-api-key': '045cd7e4-a5a4-4a12-9473-cb4ec60ce97a'
   }

   try:
       response = requests.request("POST", url, headers=headers, data=payload, timeout=30)
       response.raise_for_status() # Raises stored HTTPError, if one occurred.
       data = json.loads(response.text)
       price = data['rate']
       return price
   except KeyError:
       return None
   except RequestException as e:
       print(f"An error occurred while making the API request: {e}")
       return None
   except ConnectTimeout as e:
       print(f"Connection to the API timed out: {e}")
       return None
   except requests.exceptions.HTTPError as e:
       if e.response.status_code == 502:
           print("Server Error: Bad Gateway")
       return None


# fetch marketcap    
def get_mc():
    url = "https://api.livecoinwatch.com/coins/single"
    payload = json.dumps({
        "currency": "USD",
        "code": "PYI",
        "meta": True
    })

    headers = {
        'content-type': 'application/json',
        'x-api-key': '045cd7e4-a5a4-4a12-9473-cb4ec60ce97a'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=30)
        response.raise_for_status()  # Raises stored HTTPError, if one occurred.
        data = json.loads(response.text)
        mc= data['cap'] #mc stands for market cap
        return mc
    except KeyError:
       return None
    except RequestException as e:
       print(f"An error occurred while making the API request: {e}")
       return None
    except ConnectTimeout as e:
       print(f"Connection to the API timed out: {e}")
       return None
    except requests.exceptions.HTTPError as e:
       if e.response.status_code == 502:
           print("Server Error: Bad Gateway")
       return None
    
def format_marketcap(marketcap):
    million = 1000000
    billion = 1000000000

    if marketcap < million:
        return f"${marketcap / 1000:.1f}K"
    elif marketcap < billion:
        return f"${marketcap / million:.1f}M"
    else:
        return f"${marketcap / billion:.1f}B"
    
    
#mc stands for marketcap fyi    

class Stats(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.bot.ready = False
        self.channel_id =   #price feed channel
        self.channel_mc =  #marketcap channel
        self.member_countChannel =  #members count channel
        self.channel_telegram =   #telegram member count channel
        
        self.update_memberCount.start()
        self.update_pyrin_price.start() 
        self.update_market_cap.start()
        self.update_telegram.start()
        
        
         
    
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.ready = True
            print(f'Bot is ready. Channel ID: {self.channel_id}')
            
    @tasks.loop(seconds=30)  # Update every minute
    async def update_pyrin_price(self):
        pyrin_price = get_price() 
        
        if not self.bot.ready or self.channel_id is None:  # Don't do anything if the bot isn't ready or the channel hasn't been set
            return

        channel = self.bot.get_channel(int(self.channel_id))  # Make sure to convert the channel ID to an integer

        if channel is None:
            print(f'Could not find channel with ID {self.channel_id}')
            return
        
        if pyrin_price is not None:
            formatted_price = "{:.3f}".format(pyrin_price)
            # Update the channel's name with the price
            await channel.edit(name=f"PYI: ${formatted_price}")
            
            # Set the bot's status
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Pyrin Price: ${pyrin_price}"))
        else:
            print("Could not fetch Pyrin price")
        
    @tasks.loop(seconds=30)
    async def update_market_cap(self):
        try:
            market_cap = get_mc()
            
            if not self.bot.ready or self.channel_mc is None:  # Don't do anything if the bot isn't ready or the channel hasn't been set
                return

            channel = self.bot.get_channel(int(self.channel_mc))  # Make sure to convert the channel ID to an integer

            if channel is None:
                print(f'Could not find channel with ID {self.channel_mc}')
                return
            
            formatted_marketcap = format_marketcap(market_cap)
            
            #edit channel name with marketcap
            await channel.edit(name=f"MCap: {formatted_marketcap}")
            
            
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching the market cap: {str(e)}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
     
    """verified members count function checks the number of verified members in the server and displays it over the channel"""
           
    @tasks.loop(seconds=30) # Update every 30 seconds
    async def update_memberCount(self):
        if not self.bot.ready or self.member_countChannel is None:
            return

        channel = self.bot.get_channel(int(self.member_countChannel))

        if channel is None:
            print(f'Could not find channel with ID {self.member_countChannel}')
            return

        guild = self.bot.guilds[0] # Get the first guild the bot is in
        total_member_count = guild.member_count # Get the total number of members in the guild

        await channel.edit(name=f"Members: {total_member_count}")
        
    
    @tasks.loop(seconds=30) # Update every 30 seconds
    async def update_telegram(self):
        if not self.bot.ready or self.channel_telegram is None:
            return

        channel = self.bot.get_channel(int(self.channel_telegram))

        if channel is None:
            print(f'Could not find channel with ID {self.channel_telegram}')
            return

        # Fetch the member count of the Telegram group
        telegram_bot = telegram.Bot(token=os.getenv("TELEGRAM_BOT"))
        chat_id = telegram_chat_id
        telegram_member_count = await telegram_bot.get_chat_member_count(chat_id) # await the coroutine

        await channel.edit(name=f"Telegram: {telegram_member_count}")


    
def setup(bot):
    bot.add_cog(Stats(bot))