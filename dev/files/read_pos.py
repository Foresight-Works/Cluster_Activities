import pandas as pd
import os
results_dir = 'C:\\Users\\RonyArmon\\Projects_Code\\Cluster_Activities\\results'
df = pd.read_pickle(os.path.join(results_dir, 'pos.pkl'))
print(df.columns)
print(df[['token_id', 'name_id']].head(10))