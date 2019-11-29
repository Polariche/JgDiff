import viewer
import path
import os
import numpy as np
import pandas as pd
import json

rows = []
with open("statics/champion.json", encoding='UTF8') as c:
	t = json.load(c)["data"]

	for x in t.values():
		row = [x["key"], x["name"]]
		rows.append(row)

pd.DataFrame(rows, columns=["id", "name"], ).to_csv("matchroles/champions.csv",index=False)

