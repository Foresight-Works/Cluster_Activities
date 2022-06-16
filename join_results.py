import pandas as pd
import os
results_dir = '/home/rony/Projects_Code/Cluster_Activities/validation'
files = [f for f in os.listdir(results_dir) if '.xlsx' in f]
df_cols = pd.read_excel(os.path.join(results_dir, files[0])).columns
print(df_cols)
dfs = pd.DataFrame(columns=df_cols)
for file in files:
	source_file = file.replace('.xlsx', '').replace('file_', '')
	df = pd.read_excel(os.path.join(results_dir, file))
	df['File'] = source_file
	print(df.head())
	dfs = pd.concat([dfs, df])
dfs = dfs.astype(str)
dfs['ClusterID_File'] = dfs['File']+'_'+dfs['Cluster_ID']
print(dfs.head())
print(dfs.info())
dfs.to_excel('validation_results.xlsx', index=False)
