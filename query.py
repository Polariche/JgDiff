import requests
from api_key import API_KEY
import asyncio
import utils

class Query:
    def __init__(self, queue):
        self.response = None
        self.callback = None
        self.fileName = None
        self.method = ""
        self.queue = queue

    def clearArgs(self):
        self.args = {}

    def setCallback(self, callback, **kwargs):
        self.callback = callback
        self.callback_kwargs = kwargs

        return self

    def sendToQueue(self):
        self.queue.append(self)

        return self

    def executeQuery(self, timeout=3):
        try:
            self.response = requests.get(url=self.link, timeout=timeout)
        except requests.exceptions.RequestException as e:
            print(e)
            return 408

        if self.response.status_code == 200:
            if self.callback != None:
                self.callback(self, **self.callback_kwargs)
        else:
            print("Query Unsuccessful: " + self.response.status_code.__str__() + "\n\t" +  self.link)
            

        return self.response.status_code

    def isComplete(self):
        return self.response != None

    def __repr__(self):
        if self.response != None:
            return self.response.__repr__()
        else:
            return self.__class__.__name__ + "." + self.method + " " + self.args.__repr__() + " " + "Callback: " + self.callback.__name__

    def name(self):
        if self.name == None:
            return self.__class__.__name__ +  "_".join([''] + [x[0].__str__()+"_"+x[1].__str__() for x in list(self.args.items())]) 
        else:
            return self.fileName


class SummonerQuery(Query):
    def __init__(self, queue):
        super().__init__(queue)
        self.base_link = "https://kr.api.riotgames.com/lol/summoner/v4/summoners"

    def byName(self, summonerName, **kwargs):
        self.args = kwargs
        args_text = utils.url_args(kwargs)
        self.args['summonerName'] = summonerName
        self.link = f"{self.base_link}/by-name/{summonerName}?{args_text}api_key={API_KEY}"
        self.method = "byName"

        return self.sendToQueue()

    def byAccountId(self, encryptedAccountId, **kwargs):
        self.args = kwargs
        args_text = utils.url_args(kwargs)
        self.args['encryptedAccountId'] = encryptedAccountId
        self.link = f"{self.base_link}/by-account/{encryptedAccountId}?{args_text}api_key={API_KEY}"
        self.method = "byAccountId"

        return self.sendToQueue()

    def byPUUID(self, encryptedPUUID, **kwargs):
        self.args = kwargs
        args_text = utils.url_args(kwargs)
        self.args['encryptedPUUID'] = encryptedPUUID
        self.link = f"{self.base_link}/by-puuid/{encryptedPUUID}?{args_text}api_key={API_KEY}"
        self.method = "byPUUID"

        return self.sendToQueue()
    

class MatchQuery(Query):
    def __init__(self, queue):
        super().__init__(queue)
        self.base_link = "https://kr.api.riotgames.com/lol/match/v4"

    def byMatchId(self, matchId, **kwargs):
        self.args = kwargs
        args_text = utils.url_args(kwargs)
        self.args['matchId'] = matchId
        self.link = f"{self.base_link}/matches/{matchId}?{args_text}api_key={API_KEY}"
        self.fileName = str(matchId)
        self.method = "byMatchId"

        return self.sendToQueue()

    def byAccountId(self, encryptedAccountId, **kwargs):
        self.args = kwargs
        args_text = utils.url_args(kwargs)
        self.args['encryptedAccountId'] = encryptedAccountId
        self.link = f"{self.base_link}/matchlists/by-account/{encryptedAccountId}?{args_text}api_key={API_KEY}"
        self.fileName = str(encryptedAccountId)
        self.method = "byAccountId"

        return self.sendToQueue()

    def timelineByMatchId(self, matchId, **kwargs):
        self.args = kwargs
        args_text = utils.url_args(kwargs)
        self.args['matchId'] = matchId
        self.link = f"{self.base_link}/timelines/by-match/{matchId}{args_text}?{args_text}api_key={API_KEY}"
        self.fileName = str(matchId)
        self.method = "timelineByMatchId"

        return self.sendToQueue()

