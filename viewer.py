import json
import path
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas


def matchRoles(matchId):
    #This needs some multiclass SVM for proper role identification

    with open(path.matches+str(matchId)+".json") as file:
        
        j = json.load(file)
        players = j["participants"]

        duration = j["gameDuration"]
        minute = int(duration/60)

        #pid, champ
        a = np.empty((2,5,2), dtype=int)

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

        return a


def timeline(matchId, p):
    f = [[] for i in range(len(p))]

    with open(path.timelines+str(matchId)+".json") as file:
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
    with open(path.timelines+str(matchId)+".json") as file:
        frames = json.load(file)["frames"]
        f = [[] for i in range(len(frames))]

        for i in range(len(frames)):
            events = frames[i]["events"]

            for event in events:
                if event["type"] == "CHAMPION_KILL":

                    timestamp = event["timestamp"]
                    x,y = event["position"].values()
                    k = event["killerId"]
                    d = event["victimId"]
                    #a = ''
                    #if len(event["assistingParticipantIds"]) > 0:
                    #    a = ','.join(map(str, event["assistingParticipantIds"]))

                    f[i].append([timestamp, x, y, k, d,]) #a])
            f[i] = np.array(f[i]).reshape(-1,5)

        return f


page = 0
def matchViewer(matchId):
    roles = matchRoles(matchId)

    roleText = ["Top", "Jungle", "Mid", "Bot", "Support"]

    vs = []
    vs = np.array(timeline(matchId, list(range(1,11))))
    kill = kills(matchId)

    def plotPage(page, gca):
        gca.set_xlim([0,14800])
        gca.set_ylim([0,14800])
        img = plt.imread("assets/minimap.png")
        gca.imshow(img,extent=[-200, 14800, -200, 14800])

        gca.scatter(vs[:5,page,1], vs[:5,page,2], color='b')
        gca.scatter(vs[5:,page,1], vs[5:,page,2], color='r')

        for i in range(len(kill[page])):
            col = 'b' if kill[page][i, 4] <= 5 else 'r'

            gca.scatter(kill[page][i, 1], kill[page][i, 2], color=col, marker='X', s=200)
        for i in range(10):
            plt.text(vs[i,page,1]+10, vs[i,page,2], roleText[i%5], color='#DDDDDD')

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

    fig = plt.figure()
    fig.canvas.mpl_connect('scroll_event', onscroll)

    plotPage(0, plt.gca())


    plt.show()


print(matchViewer(3664646598))