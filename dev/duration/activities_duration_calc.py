import numpy as np
import pandas as pd
from datetime import datetime

def infer_dt_format(dt):
    '''
    Infer the format of dt string to use as parameter in pd.to_datetime
    '''
    dt_format = "%a %b %d %H:%M:%S %Z %Y"
    seps = ['/', '-']
    if any(sep in dt for sep in seps):
        for sep in seps:
            parts = dt.split(sep)
            if len(parts[0]) == 4: #2023-04-19
                dt_format = "%Y{}%m{}%d".format(sep, sep)
            else:
                dt_format = "%d{}%m{}%Y".format(sep, sep)
            break
    return dt_format

def activities_duration(project_df, calculate):
    '''
    Calculate the planned and actual duration for program activities
    :param project_df (DataFrame): Planned/Actual Start/End times for each activity
    :param calculate(str; planned, actual): The type of duration to calculate
    '''
    print(len(project_df))
    if calculate == 'planned':
        headers = ['PlannedStart', 'PlannedEnd']
    else: headers = ['ActualStart', 'ActualEnd']
    project_df = project_df[['ID'] + headers].dropna().astype(str)
    print(len(project_df))
    for header in headers:
        header_sample = project_df[header].values[0]
        dt_format = infer_dt_format(header_sample)
        print('header: {h} | sample: {s} | dt_format: {d}'.format(h=header, s=header_sample, d=dt_format))
        project_df[header] = [datetime.strptime(date_string, dt_format) for date_string in list(project_df[header])]
        print(project_df[header].head())
    project_df['Duration'] = (project_df[headers[1]] - project_df[headers[0]]).dt.days.astype(int)
    return dict(zip(list(project_df['ID']), list(project_df['Duration'])))

projects_df = pd.read_excel('projects.xlsx')
id_actual_duration = activities_duration(projects_df, 'actual')
for k, v in id_actual_duration.items():
    print(k, v)