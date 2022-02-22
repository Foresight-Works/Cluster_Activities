import pandas as pd
from datetime import date
import os
files = os.listdir('./program_excels')
PlannedDuration_stats = pd.DataFrame()
for index, file in enumerate(files):
    print('===== {f} ====='.format(f=file))
    project = pd.read_excel(os.path.join('./program_excels', file))
    if len(project)>0:
        project['PlannedEnd'] = pd.to_datetime(project['PlannedEnd'], format="%d/%m/%Y")
        project['PlannedStart'] = pd.to_datetime(project['PlannedStart'], format="%d/%m/%Y")
        #project['PlannedDuration'] = date(project['PlannedEnd']) - date(project['PlannedStart'])
        project['PlannedDuration'] = (project['PlannedEnd'] - project['PlannedStart']).dt.days.astype(int)
        print(project['PlannedDuration'].head())
        durations_stats = round(project['PlannedDuration'].describe().astype(int))
        PlannedDuration_stats['file_{n}'.format(n=index)] = list(durations_stats.values)
        # durations_stats = pd.DataFrame(durations_stats).T
        # print(durations_stats.columns)
        print(durations_stats)
    else:
        print('zero lines in', file)

PlannedDuration_stats.index = list(durations_stats.index)
PlannedDuration_stats.to_excel('PlannedDuration_stats.xlsx')
print(PlannedDuration_stats)
