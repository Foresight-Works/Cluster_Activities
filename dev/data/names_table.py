import os
import pandas as pd
results_dir = 'C:\\Users\\RonyArmon\\Projects_Code\\Cluster_Activities\\results'
names = open(os.path.join(results_dir, 'names.txt')).read().split('\n')
names = [n for n in names if n]
vals = []
for index, name in enumerate(names):
    index += 1
    val = [index, name]
    if val:
        vals.append(val)
    print(index, name)
#print(vals)
vals = [v for v in vals if v]
names_df = pd.DataFrame(vals, columns=['name_id', 'name'])
names_df.to_excel(os.path.join(results_dir, 'name_df.xlsx'), index=False)