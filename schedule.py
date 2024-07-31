from discord.ext import commands
from config import intents, TOKEN, COMMAND_PREFIX
from commandscog import CommandsCog
from pollcog import PollCog
import asyncio

class Bot(commands.Bot):
    def __init__(self):
        self._in_status = []
        self.last_in_sent_status = []
        self._out_status = []
        self.last_out_sent_status = []
        self.status_update_event = asyncio.Event()
        super().__init__(command_prefix=COMMAND_PREFIX, intents=intents)

    async def setup_hook(self):
        await self.add_cog(PollCog(self))
        await self.add_cog(CommandsCog(self))
        self.bg_task = self.loop.create_task(self.status_update_task())

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_poll_vote_add(self, user, ans):
        name = ans.text
        if name in self._out_status:
            self._out_status.remove(name)
        if name not in self._in_status:
            self._in_status.append(name)
        self.status_update_event.set()
        print(f"user:{user} added ans:{name}")

    async def on_poll_vote_remove(self, user, ans):
        name = ans.text
        if name in self._in_status:
            self._in_status.remove(name)
        if name not in self._out_status:
            self._out_status.append(name)
        self.status_update_event.set()
        print(f"user:{user} removed ans:{name}")

    async def status_update_task(self):
        while not self.is_closed():
            await self.status_update_event.wait()
            await asyncio.sleep(1)  # Wait for 1 second
            
            channel = self.get_channel(1261688488500269076)  # Replace with your channel ID
            
            if self._in_status != self.last_in_sent_status or \
                self._out_status != self.last_out_sent_status:
                in_msg = f"In({len(self._in_status)}): {','.join(self._in_status)}"
                out_msg = f"Out({len(self._out_status)}): {','.join(self._out_status)}"
                final_msg = in_msg + "\n" + out_msg
                await channel.send(final_msg)
                self.last_in_sent_status = self._in_status.copy()
                self.last_out_sent_status = self._out_status.copy()            
            self.status_update_event.clear()

class ManageFood:
    def __init__(self) -> None:
        pass

def main():
    bot = Bot()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()