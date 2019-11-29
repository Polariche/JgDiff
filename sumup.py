import viewer
import path
import os
import numpy as np
import pandas as pd


def getMatches():
    t = os.listdir(path.matches)
    matches = [int(x[:-5]) for x in t if int(x[:-5])%5!=0]

    return matches

    
def rolePd():
    matches = getMatches()

    t = []

    for match in matches:
        if match%5 == 0:
            continue
        roles = viewer.matchRoles(match)

        t.append(np.concatenate([[match], roles.reshape(-1)]))

    roles = ["Top", "Jungle", "Mid", "Bot", "Support"]
    pd.DataFrame(np.array(t), columns=["matchId"]+[roles[int(i/2%5)]+"_"+int(i/10).__str__()+"_"+("id" if i%2==0 else "championId") for i in range(20)]).to_csv(path.supplement+"/matchrole.csv")


def killsPd():
    matches = getMatches()

    f = lambda x: pd.DataFrame(np.concatenate(np.array(viewer.kills(m))).astype(int), columns=["timestamp", "x", "y", "kill", "death", "assist"]+["level", "gold"]*10).to_csv("supplement/kills/"+str(x)+".csv")
    
    for m in matches[:1]:
        f(m)

killsPd()