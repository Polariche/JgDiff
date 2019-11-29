import pandas as pd

#pd.concat([pd.read_csv(f"supplement/playerFrameTable{i}.csv").iloc[:,1:] for i in range(1,20)]).reset_index(drop = True).to_csv("supplement/playerFrameTable.csv")