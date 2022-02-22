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
    print('dt_format:', dt, dt_format)
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
        #print('planned_start_sample, start_dt_format:', planned_start_sample, start_dt_format)
        #print('planned_end_sample, end_dt_format:', planned_end_sample, end_dt_format)
        cluster_df['PlannedStart'] = pd.to_datetime(cluster_df['PlannedStart'], format=start_dt_format)
        cluster_df['PlannedEnd'] = pd.to_datetime(cluster_df['PlannedEnd'], format=end_dt_format)
        PlannedDuration = (cluster_df['PlannedEnd'] - cluster_df['PlannedStart']).dt.days.astype(int)
        score = round(np.std(np.array(PlannedDuration)))
        return score

def calculate_weightedSOS(vectors):
    cluster_distances = squareform(pdist(vectors, 'sqeuclidean'))
    Dr = np.sum(np.triu(cluster_distances))
    weighted_Dr = Dr/(2*len(vectors))
    return weighted_Dr

def calculate_wcss


def evaluate_clusters(clusters_dict, projects_df, metrics, scaled=True, ids_embeddings=np.empty(1)):
    clusters_scores = []
    for cluster_key, ids in clusters_dict.items():
        clusters_count = len(ids)
        #print(cluster_key, ids)
        cluster_score = [cluster_key, clusters_count]
        if 'cluster_duration_std' in metrics:
            cluster_df = projects_df[projects_df['ID'].isin(ids)]
            #print(len(cluster_df))
            cluster_score.append(cluster_duration_std(cluster_df))
        if 'cluster_ss' in metrics:
            names_embeddings = {k:v for k, v in ids_embeddings.items() if k in ids}
            names_embeddings = np.stack(list(names_embeddings.values()))
            cluster_score.append(calculate_weightedSOS(names_embeddings))
        clusters_scores.append(cluster_score)
    scores = pd.DataFrame(clusters_scores, columns=['key', 'count'] + metrics)
    print('scores')
    print(scores)
    print('Scaling scores')
    if scaled:
        clusters_scores = np.array(scores[metrics])
        scaler = MinMaxScaler()
        scaled_scores = scaler.fit_transform(clusters_scores)
        scaled_scores = pd.DataFrame(scaled_scores, columns=metrics)
        scaled_scores['key'] = list(scores['key'])
        scaled_scores = scaled_scores[['key'] + metrics]
        print('Scaled scores')
        print(scaled_scores)
        return scaled_scores
    else:
        return scores

