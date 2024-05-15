import discord
from discord.ext import commands, tasks
import requests
import json
from requests.exceptions import RequestException, ConnectTimeout
from dotenv import load_dotenv
import os


load_dotenv()

intents = discord.Intents(guilds=True)
client = discord.Client(intents=intents)
intents.members = True



#verified role id, you can get this by right clicking the role on discord and copy

def get_price():
    """
    Retrieves the current price of PYI cryptocurrency from LiveCoinWatch API.

    Returns:
        float: The current price of PYI in USD.
        None: If an error occurs during the request or processing the response.
    """
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
        price = data['rate']
        return price
    except ConnectTimeout as e:
        print(f"Connection to the API timed out: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 502:
            print("Server Error: Bad Gateway")
        else:
            print(f"An HTTP error occurred: {e}")
        return None
    except KeyError:
        return None
    except RequestException as e:
        print(f"An error occurred while making the API request: {e}")
        return None

# fetch marketcap    
def get_mc():
    """
    Retrieves the market capitalization (MC) of PYI cryptocurrency from LiveCoinWatch API.

    Returns:
        int: The market capitalization of PYI in USD.
        None: If an error occurs during the request or processing the response.
    """
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
        mc = data['cap']  # mc stands for market cap
        return mc
    except ConnectTimeout as e:
        print(f"Connection to the API timed out: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 502:
            print("Server Error: Bad Gateway")
        else:
            print(f"An HTTP error occurred: {e}")
        return None
    except KeyError:
        return None
    except RequestException as e:
        print(f"An error occurred while making the API request: {e}")
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
    
def format_circulating_supply(circulating_supply):
    """
    Formats the circulating supply with 'k' for thousands, 'm' for millions, and 'b' for billions.

    Args:
        circulating_supply (int): The circulating supply of the cryptocurrency.

    Returns:
        str: Formatted string representing the circulating supply.
    """
    if circulating_supply >= 1000000000:
        return f"{circulating_supply / 1000000000:.1f}b"
    elif circulating_supply >= 1000000:
        return f"{circulating_supply / 1000000:.1f}m"
    else:
        return f"{circulating_supply / 1000:.1f}k"


def get_circulating_supply():
    """
    Retrieves the circulating supply of PYI cryptocurrency from LiveCoinWatch API.

    Returns:
        int: The circulating supply of PYI.
        None: If an error occurs during the request or processing the response.
    """
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
        response.raise_for_status() 
        data = json.loads(response.text)
        cs = data['circulatingSupply']  
        return cs
    except ConnectTimeout as e:
        print(f"Connection to the API timed out: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 502:
            print("Server Error: Bad Gateway")
        else:
            print(f"An HTTP error occurred: {e}")
        return None
    except KeyError:
        return None
    except RequestException as e:
        print(f"An error occurred while making the API request: {e}")
        return None
    
#mc stands for marketcap fyi    

class Stats(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.bot.ready = False
        self.channel_price = os.getenv("channel_price")
        self.channel_mc = os.getenv("channel_mc")
        self.channel_cirsupply = os.getenv("circulating_supply")
        self.update_pyrin_price.start()
        self.update_market_cap.start()
        self.update_cirsupply.start()
    
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.ready = True
            print(f'Bot is ready. Channel ID: {self.channel_price}')
            print(f'Bot is ready. Channel ID: {self.channel_mc}')
            print(f'Bot is ready. Channel ID: {self.channel_cirsupply}')
            
    @tasks.loop(seconds=30)
    async def update_pyrin_price(self):
        pyrin_price = get_price()

        if not self.bot.ready or self.channel_price is None:
            return

        channel = self.bot.get_channel(int(self.channel_price))

        if channel is None:
            print(f'Could not find channel with ID {self.channel_price}')
            return

        if pyrin_price is not None:
            formatted_price = "{:.3f}".format(pyrin_price)
            await channel.edit(name=f"PYI: ${formatted_price}")
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Pyrin Price: ${pyrin_price}"))

    @tasks.loop(seconds=30)
    async def update_market_cap(self):
        try:
            market_cap = get_mc()

            if not self.bot.ready or self.channel_mc is None:
                return

            channel = self.bot.get_channel(int(self.channel_mc))

            if channel is None:
                print(f'Could not find channel with ID {self.channel_mc}')
                return

            formatted_marketcap = format_marketcap(market_cap)

            await channel.edit(name=f"MCap: {formatted_marketcap}")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching the market cap: {str(e)}")
        except ValueError as e:
            print(f"A formatting error occurred: {str(e)}")
            
    @tasks.loop(seconds=30)
    async def update_cirsupply(self):
        try:
            cs = get_circulating_supply()

            if not self.bot.ready or self.channel_cirsupply is None:
                return

            channel = self.bot.get_channel(int(self.channel_cirsupply))

            if channel is None:
                print(f'Could not find channel with ID {self.channel_cirsupply}')
                return

            if cs is not None:
                formatted_cs = format_circulating_supply(cs)
                await channel.edit(name=f"Cir.Supply: {formatted_cs}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching the circulating supply: {str(e)}")
        except ValueError as e:
            print(f"A formatting error occurred: {str(e)}")


def setup(bot):
    bot.add_cog(Stats(bot))