from query import SummonerQuery, MatchQuery
import xml.etree.ElementTree as ET
import json

def handleFailure(query, success=None, failure=None, **kwargs):
    if query.response.status_code == 200:
        success(query)
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


def matchlistToMatches(query, **kwargs):
    q = query.queue
    matchlist = query.response.json()['matches']

    for m in matchlist[:1]:
        MatchQuery(q).setCallback(save, path="matches/").byMatchId(m['gameId'])
        MatchQuery(q).setCallback(save, path="timelines/").timelineByMatchId(m['gameId'])

def accountToMatchlist(query, **kwargs):
    printResponse(query)

    q = query.queue
    account = query.response.json()
    accountId = account['accountId']

    MatchQuery(q).setCallback(matchlistToMatches).byAccountId(accountId)

