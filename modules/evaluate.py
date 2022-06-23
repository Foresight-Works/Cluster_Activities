from datetime import datetime
import pandas as pd
import numpy as np
from modules.libraries import *
from modules.config import *

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
    if calculate == 'planned':
        headers = ['PlannedStart', 'PlannedEnd']
    else:
        headers = ['ActualStart', 'ActualEnd']
    print('Calculating {c} duration'.format(c=calculate))
    print('{n} tasks'.format(n=len(project_df)))
    project_df = project_df[['ID'] + headers].replace('', np.nan).dropna().astype(str)
    print('{n} tasks have {c} start/end data'.format(n=len(project_df), c=calculate))
    for header in headers:
        header_sample = project_df[header].values[0]
        dt_format = infer_dt_format(header_sample)
        project_df[header] = [datetime.strptime(date_string, dt_format) for date_string in list(project_df[header])]

    project_df['Duration'] = (project_df[headers[1]] - project_df[headers[0]]).dt.days.astype(int)
    print('{n} tasks in results'.format(n=len(project_df)))
    return dict(zip(list(project_df['ID']), list(project_df['Duration'])))


def activities_duration_product_research(project_df, calculate):
    '''
    Activity duration calculated for the product research format
    '''
    if calculate == 'planned':
        headers = ['PlannedStart', 'PlannedEnd']
    else: headers = ['ActualStart', 'ActualEnd']
    print('{c} duration: {n} tasks'.format(c=calculate, n=len(project_df)))
    project_df = project_df[['ID'] + headers].replace('', np.nan).dropna().astype(str)
    # Infer date time data types and convert the dates data to the format identified
    for header in headers:
        header_sample = project_df[header].values[0]
        dt_format = infer_dt_format(header_sample)
        project_df[header] = [datetime.strptime(date_string, dt_format) for date_string in list(project_df[header])]
    project_df['Duration'] = (project_df[headers[1]] - project_df[headers[0]]).dt.days.astype(int)
    project_df = project_df[['ID', 'Duration']]
    project_df = project_df.rename(columns=\
                    {'Duration':'{p}Duration'.format(p=calculate.capitalize())})
    return project_df


def clusters_duration_std(clusters_dict, id_planned_duration):

    '''
    Calculate the standard deviation of tasks processes in each cluster
    :param clusters_dict (dict): Cluster activities ids (lists) keyed by cluster id
    :param id_planned_duration: The planned duration for projects' activities indexed by activity ID
    '''
    scores = []
    for cluster_key, cluster_ids in clusters_dict.items():
        duration_values = [id_planned_duration[id] for id in cluster_ids]
        duration_std = np.std(np.array(duration_values))
        scores.append([cluster_key, duration_std])
    scores = pd.DataFrame(scores, columns=['key', 'duration_std'])
    return scores


def ch_index_sklearn(clusters_dict, ids_embeddings=np.empty(1)):
    '''
    Calculate within and between sum of squares per cluster and for all clusters
    '''
    names_embeddings = np.stack(list(ids_embeddings.values()))
    data_centroid = np.mean(names_embeddings, axis=0)
    n_samples = names_embeddings.shape[0]
    n_clusters = len(clusters_dict)

    BSS, WSS = 0.0, 0.0
    scores = []
    for cluster_key, cluster_ids in clusters_dict.items():
        # Vectors for cluster key
        names_embeddings = {id: embedding for id, embedding in ids_embeddings.items() if id in cluster_ids}
        cluster_k = np.stack(list(names_embeddings.values()))
        cluster_centroid = np.mean(cluster_k, axis=0)
        cluster_size = len(cluster_k)
        BSSk = cluster_size * np.sum((cluster_centroid - data_centroid) ** 2)
        WSSk = np.sum((cluster_k - cluster_centroid) ** 2)
        BSSk, WSSk = round(BSSk, 2), round(WSSk, 2)
        scores.append([cluster_key, cluster_size, BSSk, WSSk])
        BSS += BSSk
        WSS += WSSk
    scores = pd.DataFrame(scores, columns=['key', 'size', 'BSSk', 'WSSk'])
    if WSS == 0.0:
        ch_index = 1.0
    else:
        ch_index = BSS * (n_samples - n_clusters) / (WSS * (n_clusters - 1.0))

    BSS, WSS, ch_index = round(BSS, 2), round(WSS, 2), round(ch_index, 2)
    return BSS, WSS, ch_index, scores

def scale_df(df):
    cols = df.columns
    df_vals = np.array(df)
    scaler = MinMaxScaler()
    scaled_scores = scaler.fit_transform(df_vals)
    return pd.DataFrame(scaled_scores, columns=cols)

def vote(scaled_scores, scores_cols, metrics_optimize):
    md_cols = scaled_scores.drop(scores_cols, axis=1)
    scaled_scores = pd.concat([md_cols, scaled_scores], axis=1)
    for metric, optimize in metrics_optimize.items():
        optimize_for, optimize_weight = optimize
        if optimize_for == 'min':
            scaled_scores[metric] = [(1-x) for x in scaled_scores[metric]]
        scaled_scores[metric] = optimize_weight * scaled_scores[metric]
    scaled_scores['sum'] = scaled_scores[scores_cols].sum(axis=1)
    run_id = int(scaled_scores[['sum']].idxmax())
    return run_id
