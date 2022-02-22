import json
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

def infer_dt_format(dt):
    '''
    Infer the format of dt string to use as parameter in pd.to_datetime
    '''
    seps = ['/', '-']
    for sep in seps:
        if sep in dt:
            parts = dt.split(sep)
            if len(parts[0]) == 4: #2023-04-19
                dt_format = "%Y{}%m{}%d".format(sep, sep)
            else:
                dt_format = "%d{}%m{}%Y".format(sep, sep)
            break
    return dt_format

def cluster_duration_std(cluster_df):
    '''
    Calculate the standard deviation for the planned duration values of cluster names
    :param cluster_df: A data frame containing the cluster task names along with their planned start and end dates
    '''
    cluster_df.replace("", float("NaN"), inplace=True)
    cluster_df.dropna(subset=['PlannedStart', 'PlannedEnd'], inplace=True)
    if len(cluster_df) > 0:
        planned_start_sample = cluster_df['PlannedStart'].values[0]
        planned_end_sample = cluster_df['PlannedEnd'].values[0]
        start_dt_format, end_dt_format = infer_dt_format(planned_start_sample), infer_dt_format(planned_end_sample)
        cluster_df['PlannedStart'] = pd.to_datetime(cluster_df['PlannedStart'], format=start_dt_format)
        cluster_df['PlannedEnd'] = pd.to_datetime(cluster_df['PlannedEnd'], format=end_dt_format)
        PlannedDuration = (cluster_df['PlannedEnd'] - cluster_df['PlannedStart']).dt.days.astype(int)
        ch_index = round(np.std(np.array(PlannedDuration)))
        return ch_index


def calinski_harabasz_ch_index_sklearn(clusters_dict, ids_embeddings=np.empty(1)):
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


def clusters_duration_std(clusters_dict, projects_df):

    '''
    Calculate the standard deviation of tasks duration in each cluster
    :param clusters_dict (dict): Cluster activities ids (lists) keyed by cluster id
    :param projects_df: The input data with cluster ids, used to capture activity durations
    '''
    scores = []
    for cluster_key, cluster_ids in clusters_dict.items():
        cluster_df = projects_df[projects_df['ID'].isin(cluster_ids)]
        duration_std = cluster_duration_std(cluster_df)
        scores.append([cluster_key, duration_std])
    scores = pd.DataFrame(scores, columns=['key', 'duration_std'])
    return scores
