import pandas as pd

data_files = ['CCGT D1.csv', 'CCGT D2.csv', 'DUKE S2X1CC_2013_10_27.csv', 'DUKE WAYNE COUNTY_2012-01-29.csv']
task_names = []
for file in data_files:
    project_df = pd.read_csv('./response/raw_data/{f}'.format(f=file))
    project_names = list(project_df['Activity Name'][project_df['Activity type'] == 'TT_Task'].unique())
    task_names += project_names
tasks_names = list(set(task_names))

with open('./results/cluster_key.txt', 'w', encoding="utf-8") as f:
    for name in task_names:
        name = name.lower()
        f.write('{n}\n'.format(n=name))

