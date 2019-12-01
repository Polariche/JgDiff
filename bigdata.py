import path
import os
import numpy as np
import pandas as pd
import json

def diagTransform(data):
	# new x : ／, new y: ＼
	# data is in format [[x1, y1], [x2, y2], ...]

	return np.matmul(np.array([[1, 1], [-1, 1]])/15000, data.T-7500).T

def jgAction(json, match):
	frames = json["frames"][:-1]
	events = [frame["events"] for frame in frames]

def playerFrame(json, match):
	frames = json["frames"][:-1]
	pFrames = [list(frame["participantFrames"].values()) for frame in frames]
	table = np.empty([len(frames)*10, 3+9])

	table[:,0] = match
	table[:,1] = np.array([[i]*10 for i in range(len(frames))]).reshape(-1)
	table[:,2] = list(range(1,11))*len(frames)

	table[:,3:] = np.array([[[p["participantId"], p["position"]["x"], p["position"]["y"], p["currentGold"], p["totalGold"], p["level"], p["xp"], p["minionsKilled"], p["jungleMinionsKilled"]] for p in v] for v in pFrames]).reshape(len(frames)*10, -1)

	return table

def objects(json, match):
    frames = json["frames"]
    f = []

    for i in range(len(frames)):
        events = frames[i]["events"]

        for event in events:
            if event["type"] == "BUILDING_KILL":
                timestamp = event["timestamp"]
                x,y = event["position"].values()
                k = event["killerId"]
                d = event["type"]
                a = np.nan
                s1 = event["laneType"]
                s2 = event["towerType"]

                if len(event["assistingParticipantIds"]) > 0:
                    a = int(''.join(map(lambda x: str(x%10), sorted(event["assistingParticipantIds"], reverse=True))))

                f.append([match, timestamp, x, y, k, d, a, s1, s2])

            if event["type"] == "ELITE_MONSTER_KILL":
                timestamp = event["timestamp"]
                x,y = event["position"].values()
                k = event["killerId"]
                d = event["type"]
                a = np.nan
                s1 = event["monsterType"]
                s2 = np.nan if "monsterSubType" not in event.keys() else event["monsterSubType"]

                f.append([match, timestamp, x, y, k, d, a, s1, s2])
    return np.array(f).reshape(-1,9)


def kills(json, match):
    frames = json["frames"]
    f = []

    for i in range(len(frames)):
        events = frames[i]["events"]

        for event in events:
            if event["type"] == "CHAMPION_KILL":
                timestamp = event["timestamp"]
                x,y = event["position"].values()
                k = event["killerId"]
                d = event["victimId"]
                a = np.nan
                if len(event["assistingParticipantIds"]) > 0:
                    a = int(''.join(map(lambda x: str(x%10), sorted(event["assistingParticipantIds"], reverse=True))))

                f.append([match, timestamp, x, y, k, d, a])


    return np.array(f).reshape(-1,7)

def matchRoles(match):
    #This needs some multiclass SVM for proper role identification
    a = np.zeros((2,10), dtype=int)

    with open(path.timelines+str(match)+".json", encoding='UTF8') as file:
        pf = pd.DataFrame(playerFrame(json.load(file), match), columns=['matchId', 'frame', 'participantKey'] + ['participantId', 'position_x', 'position_y', 'currentGold', 'totalGold', 'level', 'xp', 'cs', 'jgcs'])
        pf['totalcs'] = pf['cs']+pf['jgcs']

        transformed = diagTransform(pf[['position_x', 'position_y']].values)
        pf['x'] = transformed[:,0]
        pf['y'] = transformed[:,1]

        # sup : lowest CS by the end of the game
        # jg : highest JG cs

        assigned = np.array([False]*11)

        sups = sorted(pf[pf['frame'] == max(pf['frame'])].sort_values(['totalcs'])['participantId'].iloc[:2].astype(int).values)
        jgs = sorted(pf[pf['frame'] == max(pf['frame'])].sort_values(['jgcs'], ascending=False)['participantId'].iloc[:2].astype(int).values)

        for s in sups:
            assigned[s] = True
        for j in jgs:
            assigned[j] = True

        # determine liners by their early-game position

        liners = pf[~assigned[pf['participantId'].astype(int).values]]
        liners = liners[(liners['frame'] >= 2) & (liners['frame'] < 7)].groupby('participantId').mean().sort_values('y')
        liners = liners.index.astype(int).values

        bots = sorted(liners[:2])
        mids = sorted(liners[2:4])
        tops = sorted(liners[4:])

        a[0] = [tops[0], jgs[0], mids[0], bots[0], sups[0], tops[1], jgs[1], mids[1], bots[1], sups[1]]

    with open(path.matches+str(match)+".json", encoding='UTF8') as file:
        p = json.load(file)["participants"]
        a[1] = [p[x-1]["championId"] for x in a[0]]

    return a

def createTables(matchlist):
	playerFrameTable = np.empty([0, 9])
	for match in matchlist:
		
		with open(path.timelines+str(match)+".json", encoding='UTF8') as file:
			j= json.load(file)

			playerFrameTable = np.concatenate([playerFrameTable, objects(j, match)], axis=0)

	return playerFrameTable

if __name__ == "__main__":

	t = os.listdir(path.matches)
	for a in range(1,20):
		matches = [int(x[:-5]) for x in t][(a-1)*1000:a*1000]
		print(a)
		pd.DataFrame(createTables(matches), columns=['matchId', 'timestamp', 'x', 'y', 'killer', 'event', 'assist', 'type', 'subtype']).to_csv(f"supplement/objects{a}.csv")
	#pd.DataFrame(createTables(matches), columns=['matchId', 'frame', 'participantKey'] + ['participantId', 'position_x', 'position_y', 'currentGold', 'totalGold', 'level', 'xp']).to_csv(f"supplement/playerFrameTable{a}.csv")
#print(createTables([3278904898, 3956480499]).astype(np.int64))


