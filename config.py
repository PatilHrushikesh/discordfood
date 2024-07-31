from discord import Intents
import os
import datetime
from discord import Intents
from dotenv import load_dotenv

load_dotenv()

# Constants
TOKEN = os.getenv('DISCORD_TOKEN')
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

intents = Intents.default()
intents.messages = True
intents.members = True
intents.guilds = True
intents.polls = True

COMMAND_PREFIX = '$'