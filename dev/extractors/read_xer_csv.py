import pandas as pd
pd.set_option('display.max_columns', None)
import os
files_dir = '/data/823A As-built Programme'
files = os.listdir(files_dir)
print('files:', files)
dfs = {}
for file in files:
    print('**** {} ****'.format(file))
    df = pd.read_csv(os.path.join(files_dir, file))
    if 'Unnamed: 0' in df.columns: del df['Unnamed: 0']
    print(df.info())
    print(df.head())
    dfs[file] = df

for name1, df1 in dfs.items():
    for name2, df2 in dfs.items():
        if name1 != name2:
            if df1.equals(df2):
                print('Data frames: {} = {}'.format(name1, name2))
            if len(df1.columns) == len(df2.columns):
                diff = list(set(df1.columns) - set(df2.columns))
                if not diff:
                    print('Columns: {} = {}'.format(name1, name2))
                    print(df1.columns)
