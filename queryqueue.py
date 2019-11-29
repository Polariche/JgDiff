import asyncio
import os
from query import Query
import utils
import path

minuteLimit=100     # 100 per 2 minute
secondLimit=20      # 20 per 1 sec

class QueryQueue:
    def __init__(self):
        self.queue = []
        self.working = False

    def __getitem__(self, i):
        return self.queue[i]

    def __len__(self):
        return len(self.queue)


    def append(self, x, retry=False):
        self.queue.append(x)

    def pop(self):
        return self.queue.pop(0)

    def empty(self):
        return len(self.queue) == 0

    def start(self):
        self.working = True
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.resetMinute())
        self.loop.create_task(self.resetSecond())
        self.loop.create_task(self.execute())
        self.loop.run_forever()

    async def execute(self):
        while True:

            if self.minuteCalls >= minuteLimit or self.secondCalls >= secondLimit:
                if self.working:
                    print(f"Reached the limit - Minute: {self.minuteCalls}, Second: {self.secondCalls}")
                    self.working = False
                await asyncio.sleep(1)

            elif self.empty():
                if self.working:
                    print(f"Queue is Empty")
                    self.working = False
                    
            else:
                self.working = True
                self.minuteCalls += 1
                self.secondCalls += 1

                query = self.pop()
                print(query)
                code = query.executeQuery()

                if code == 429 or code == 408:
                    self.minuteCalls = minuteLimit
                    self.append(query, retry=True)


    async def resetMinute(self):
        while True:
            self.minuteCalls = 0
            print("Minute Reset")
            await asyncio.sleep(120)
    

    async def resetSecond(self):
        while True:
            self.secondCalls = 0
            await asyncio.sleep(1)


class MatchFirstQueue(QueryQueue):
    def __init__(self):
        super().__init__()
        self.matchQueue = []
        self.matchListQueue = []

        self.searchedMatchLists = [filename[:-5] for filename in os.listdir(path.matchlists)]
        self.searchedMatches = [filename[:-5] for filename in os.listdir(path.matches)]

    def append(self, x, retry=False):
        matchId = utils.get(x.args, "matchId")

        if matchId == None:
            if x.__class__.__name__ == "MatchQuery":
                if x.fileName not in self.searchedMatchLists or retry:
                    self.matchListQueue.append(x)
                    self.searchedMatchLists.append(x.fileName)
            else:
                self.queue.append(x)
        else:
            if not matchId in self.searchedMatches or retry:
                self.matchQueue.append(x)

                if x.method == "byMatchId":
                    self.searchedMatches.append(matchId)

    def pop(self):
        if (len(self.matchQueue) > 0):
            return self.matchQueue.pop(0)
        elif (len(self.matchListQueue) > 0):
            return self.matchListQueue.pop(0)
        else:
            return self.queue.pop(0)

    def empty(self):
        return len(self.matchQueue) + len(self.queue) + len(self.matchListQueue)== 0

