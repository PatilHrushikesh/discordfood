from datetime import timedelta
from discord import Poll

class Polls:
    DEFAULT_DURATION = timedelta(hours=2)

    def __init__(self, question: str, options: list[str], duration: timedelta = None, multiple: bool = True):
        self.question = question
        self.options = options
        self.duration = duration or self.DEFAULT_DURATION
        self.multiple = multiple
        self.poll = self._create_poll()

    def _create_poll(self) -> Poll:
        poll = Poll(self.question, duration=self.duration, multiple=self.multiple)
        for option in self.options:
            poll.add_answer(text=option)
        return poll

    def get_poll(self) -> Poll:
        return self.poll

    async def end_poll(self) -> None:
        print("Ending poll")
        await self.poll.end()

    async def get_results(self) -> dict:
        pass
        # print("Getting results")
        # results = {}
        # print(f"Poll finished:{self.poll.is_finalised()}")
        # for poll_answer in self.poll.answers:
        #     print(f"Ans:{poll_answer} Coutn:{poll_answer.vote_count}")
            # async for voter in poll_answer.voters():
            #     print(f'{voter} has voted for {poll_answer}!')
            # votes = answer.votes
            # voters = [vote.user for vote in votes]
            # results[answer.text] = {
            #     'count': len(votes),
            #     'voters': voters
            # }
        # return results

    def get_total_votes(self) -> int:
        return self.poll.total_votes

    def is_finished(self) -> bool:
        return self.poll.is_finalized()