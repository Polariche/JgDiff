import bigdata
import path
import os
import numpy as np
import pandas as pd

roleText = ["Top", "Jgl", "Mid", "Bot", "Sup"]

t = os.listdir(path.matches)
matches = [int(x[:-5]) for x in t]

t = []

for match in matches:
    roles = bigdata.matchRoles(match)

    t.append(np.concatenate([[match], roles.reshape(-1)]))

roles = ["Top", "Jungle", "Mid", "Bot", "Support"]
pd.DataFrame(np.array(t), columns=["matchId"]+[x+"_0_id " for x in roleText]+[x+"_1_id" for x in roleText]+[x+"_0_ch" for x in roleText]+[x+"_1_ch" for x in roleText]).to_csv(path.supplement+"/matchrole.csv")

