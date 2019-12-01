import pandas as pd
import torch
#pd.concat([pd.read_csv(f"supplement/objects{i}.csv").iloc[:,1:] for i in range(1,20)]).reset_index(drop = True).to_csv("supplement/objects.csv")