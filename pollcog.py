import asyncio
from config import IST
import constants
import datetime

from discord.ext import commands, tasks

from polls import Polls


class MealTimes:
    LUNCH = datetime.time(hour=11, minute=22, second=00, tzinfo=IST)
    DINNER = datetime.time(hour=11, minute=19, second=30, tzinfo=IST)
    
class PollCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lunch_task.start()
        self.dinner_task.start()

    def cog_unload(self):
        self.lunch_task.cancel()
        self.dinner_task.cancel()

    async def get_channel(self, channel_id):
        for _ in range(3):  # Try 3 times
            channel = self.bot.get_channel(channel_id)
            if channel:
                return channel
            await asyncio.sleep(3)
        return None
    
    async def send_message(self, channel_id, user_msg:str):
        channel = await self.get_channel(channel_id)
        return await channel.send(user_msg)

    async def create_and_send_poll(self, question):
        # this will not work 
        channel = await self.get_channel(constants.CHANNELS['lunch-dinner'])
        if channel:
            members = constants.MEMBERS.keys()
            custom_poll = Polls(question, members)
            poll = custom_poll.get_poll()
            await channel.send(poll=poll)
        else:
            print("Failed to get channel after multiple attempts")

    @tasks.loop(time=MealTimes.LUNCH)
    async def lunch_task(self):
        # await self.create_and_send_poll(constants.LUNCH_QUESTION)
        msg = await self.send_message("==Voting started for lunch==")

    @tasks.loop(time=MealTimes.DINNER)
    async def dinner_task(self):
        # await self.create_and_send_poll(constants.DINNER_QUESTION)
        msg = await self.send_message("==Voting started for dinner==")

    @lunch_task.before_loop
    @dinner_task.before_loop
    async def before_tasks(self):
        await self.bot.wait_until_ready()