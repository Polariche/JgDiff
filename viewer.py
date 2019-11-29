import json
import path
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import bigdata


def matchRoles_v1(matchId):
    #useless lololol

    with open(path.matches+str(matchId)+".json", encoding='UTF8') as file:
        
        j = json.load(file)
        players = j["participants"]

        duration = j["gameDuration"]
        minute = int(duration/60)

        #pid, champ
        a = np.zeros((2,5,2), dtype=int)

        for player in players:
            pid = player["participantId"]
            lane = player["timeline"]["lane"]
            role = player["timeline"]["role"]
            team = int(player["teamId"]/100-1)
            spell1 = player["spell1Id"]
            spell2 = player["spell2Id"]

            champ = player["championId"]
            totalCs = player["stats"]["totalMinionsKilled"]+player["stats"]["neutralMinionsKilled"]
            csPerMin = totalCs / minute

            row = [pid, champ]

            if lane == "TOP":
                a[team][0] = row

            elif (spell1 == 11 or spell2 == 11) and lane == "JUNGLE":
                a[team][1] = row

            elif lane == "MIDDLE":
                a[team][2] = row

            elif (role == "DUO_CARRY" or csPerMin >= 3) and lane == "BOTTOM" :
                a[team][3] = row

            elif (role == "DUO_SUPPORT" or csPerMin < 3) and (lane == "BOTTOM" or lane == "JUNGLE"):
                a[team][4] = row

        for i in range(2):
            check = sum(a[i][:,0]) - 20*i
            if check >= 10 and check < 15:
                for j in range(5):
                    if a[i][j, 0] == 0:
                        pid = 15 - check + 5*i
                        a[i][j] = [pid, players[pid-1]["championId"]]
                        

        return a


def matchRoles_v2(matchId):
    a = np.zeros((2,10), dtype=int)

    with open(path.timelines+str(matchId)+".json", encoding='UTF8') as file:
        frame = json.load(file)["frames"][0]
        ids = [x["participantId"] for x in frame["participantFrames"].values()]
        a[0] = ids

    with open(path.matches+str(matchId)+".json", encoding='UTF8') as file:
        p = json.load(file)["participants"]
        a[1] = [p[x-1]["championId"] for x in a[0]]

    return a



def timeline(matchId, p):
    f = [[] for i in range(len(p))]

    with open(path.timelines+str(matchId)+".json", encoding='UTF8') as file:
        frames = json.load(file)["frames"]

        for frame in frames[:-1]:
            timestamp = frame["timestamp"]

            for i in range(len(p)):
                info = frame["participantFrames"][str(p[i])]
                x,y = info["position"].values()
                level = info["level"]
                totalGold = info["totalGold"]
                cs = info["minionsKilled"]
                jgcs = info["jungleMinionsKilled"]

                thing = [timestamp,x,y,level,totalGold,cs,jgcs]
                f[i].append(thing)

        return np.array(f)


def kills(matchId):
    with open(path.timelines+str(matchId)+".json", encoding='UTF8') as file:
        frames = json.load(file)["frames"]
        f = [[] for i in range(len(frames))]

        for i in range(len(frames)):
            events = frames[i]["events"]

            picks = ["level", "totalGold"]
            growthDiff = []
            if i<1:
                growthDiff = [1,500]*10
            else:
                # information BEFORE the kill happened
                growthDiff = [x[picks[t]] for x in frames[i-1]["participantFrames"].values() for t in range(2) ]

            for event in events:
                if event["type"] == "CHAMPION_KILL":

                    timestamp = event["timestamp"]
                    x,y = event["position"].values()
                    k = event["killerId"]
                    d = event["victimId"]
                    a = np.nan
                    if len(event["assistingParticipantIds"]) > 0:
                        a = int(''.join(map(lambda x: str(x%10), sorted(event["assistingParticipantIds"], reverse=True))))

                    f[i].append([timestamp, x, y, k, d, a]+growthDiff)
            f[i] = np.array(f[i]).reshape(-1,26)

        return f


page = 0
def matchViewer(matchId):
    #roles = matchRoles(matchId)
    #print(roles)
    roleText = ["Top", "Jgl", "Mid", "Bot", "Sup"]

    vs = []
    vs = np.array(timeline(matchId, list(range(1,11))))
    kill = kills(matchId)

    print(vs)

    def setMap(gca):
        gca.set_xlim([0,15000])
        gca.set_ylim([0,15000])
        img = plt.imread("statics/minimap.png")
        gca.imshow(img,extent=[-200, 15000, -200, 15000])

    def plotPage(page, gca):
        print("page: ", page)
        setMap(gca)

        gca.scatter(vs[:5,page,1], vs[:5,page,2], color='b', picker=True)
        gca.scatter(vs[5:,page,1], vs[5:,page,2], color='r', picker=True)
        for i in range(10):
            plt.text(vs[i,page,1]+10, vs[i,page,2], roleText[i%5], color='#DDDDDD')

        for i in range(len(kill[page])):
            col = 'b' if kill[page][i, 4] <= 5 else 'r'

            gca.scatter(kill[page][i, 1], kill[page][i, 2], color=col, marker='x', s=200)
        
    def onscroll(event):
        global page

        if event.button == 'down':
            page = min(len(vs[0])-1, page+1)
        elif event.button == 'up':
            page = max(0, page-1)

        event.canvas.figure.clear()
        gca = event.canvas.figure.gca()
        plotPage(page, gca)
        event.canvas.draw()

    def onpick3(event):
        ind = event.ind
        team = int(event.artist.get_facecolors()[0,0])

        for i in range(len(ind)):
            pid = ind[i]+team*5
            print(team, roleText[ind[i]], vs[pid, page][3:])

    fig = plt.figure()
    fig.canvas.mpl_connect('scroll_event', onscroll)
    fig.canvas.mpl_connect('pick_event', onpick3)

    plotPage(0, plt.gca())


    plt.show()

if __name__ == "__main__":
    matchRoles(3273221800)
