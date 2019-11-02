from query import SummonerQuery, MatchQuery
import xml.etree.ElementTree as ET
import json
import utils
import path

def handleFailure(query, success=None, failure=None, **kwargs):
    if query.response.status_code == 200:
        success(query, kwargs)
    else:
        print("Query Unsuccessful: " + query.response.status_code.__str__() + " " + query.link)
        failure(query)

def clone(query, **kwargs):
    x = query.__class__(query.queue)
    x.args = query.args
    x.link = query.link
    x.callback = query.callback
    x.callback_kwargs = query.callback_kwargs

    x.sendToQueue()

def save(query, **kwargs):
    data = query.response.json()

    with open(kwargs['path'] + query.name() + ".json", "w+") as f:
        json.dump(data, f, indent = 4)


def printResponse(query, **kwargs):
    print(query.response)
    print(query.response.text)



def loop(query, start=0, recursion=0, **kwargs):
    funcs = []

    def accountToMatchlist(query, **kwargs):
        #printResponse(query)

        q = query.queue
        account = query.response.json()
        #print(account)
        accountId = account['accountId']

        MatchQuery(q).setCallback(funcs[1], **kwargs).byAccountId(accountId, queue = 420, endIndex = 20)

    def matchlistToMatches(query, **kwargs):
        q = query.queue
        #print(query.link)
        matchlist = query.response.json()['matches']

        save(query, path=path.matchlists)

        for m in matchlist:
            MatchQuery(q).setCallback(save, path=path.timelines).timelineByMatchId(m['gameId'])
            MatchQuery(q).setCallback(funcs[2], **kwargs).byMatchId(m['gameId'])

    def matchesToAccounts(query, **kwargs):
        q = query.queue

        save(query, path=path.matches)

        participantIdentities = query.response.json()["participantIdentities"]
        
        for p in participantIdentities:
            accountId = p["player"]["accountId"]

            SummonerQuery(q).setCallback(funcs[0], **kwargs).byAccountId(accountId)


    funcs = [accountToMatchlist, matchlistToMatches, matchesToAccounts]

    funcs[start](query)