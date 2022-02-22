import pandas as pd
import os
for f in os.listdir():
    print(f)
    df = pd.read_csv(f)
    print(df.columns)