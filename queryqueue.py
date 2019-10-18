import asyncio
from query import Query

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


    def append(self, x):
        self.queue.append(x)

    def start(self):
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.resetMinute())
        self.loop.create_task(self.resetSecond())
        self.loop.create_task(self.execute())
        self.loop.run_forever()

    async def execute(self):
        while True:
            if self.minuteCalls < minuteLimit and self.secondCalls < secondLimit and len(self.queue) > 0:
                self.minuteCalls += 1
                self.secondCalls += 1

                query = self.queue.pop(0)
                print(query)
                query.executeQuery()
            await asyncio.sleep(0.1)


    async def resetMinute(self):
        while True:
            self.minuteCalls = 0
            print("Minute")
            await asyncio.sleep(120)
    

    async def resetSecond(self):
        while True:
            self.secondCalls = 0
            await asyncio.sleep(1)
