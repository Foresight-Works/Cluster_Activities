import json
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

def cluster_duration_std(cluster_df):
    if len(cluster_df) > 0:
        cluster_df['PlannedEnd'] = pd.to_datetime(cluster_df['PlannedEnd'], format="%d/%m/%Y")
        cluster_df['PlannedStart'] = pd.to_datetime(cluster_df['PlannedStart'], format="%d/%m/%Y")
        PlannedDuration = (cluster_df['PlannedEnd'] - cluster_df['PlannedStart']).dt.days.astype(int)
        score = round(np.std(np.array(PlannedDuration)))
        #print('wcss score=', score)
    return score

def calculate_weightedSOS(vectors):
    cluster_distances = squareform(pdist(vectors, 'sqeuclidean'))
    Dr = np.sum(np.triu(cluster_distances))
    weighted_Dr = Dr/(2*len(vectors))
    return weighted_Dr

def run_evaluation (clusters, projects, ids_embeddings = np.empty(1), metrics = ['duration_std', 'wcss']):
    clusters_scores = []
    for cluster_key, ids in clusters.items():
        #print(cluster_key, ids)
        cluster_score = [cluster_key]
        if 'duration_std' in metrics:
            cluster_df = projects[projects['ID'].isin(ids)]
            #print(len(cluster_df))
            cluster_score.append(cluster_duration_std(cluster_df))
        if 'wcss' in metrics:
            names_embeddings = {k:v for k,v in ids_embeddings.items() if k in ids}
            names_embeddings = np.stack(list(names_embeddings.values()))
            cluster_score.append(calculate_weightedSOS(names_embeddings))
        clusters_scores.append(cluster_score)
    return pd.DataFrame(clusters_scores, columns=['key'] + metrics)


# Data
projects = pd.read_excel('data/projects.xlsx')
print(projects.head())

with open('data/ccgt_response.json', 'r') as j:
     clusters = dict(json.loads(j.read()))
print('clusters')
print(clusters)
ids_embeddings = np.load('./data/ids_embeddings.npy', allow_pickle=True)[()]

metrics = ['duration_std', 'wcss']
clusters_scores_df = run_evaluation(clusters, projects, ids_embeddings=ids_embeddings, metrics=metrics)
print('clusters_scores')
print(clusters_scores_df)

clusters_scores = np.array(clusters_scores_df[metrics])
# print('clusters_scores array')
# print(clusters_scores)

scaler = MinMaxScaler()
scaled_scores = scaler.fit_transform(clusters_scores)
# print('scaled_scores array')
# print(scaled_scores)

scaled_scores = pd.DataFrame(scaled_scores, columns=metrics)
scaled_scores['key'] = list(clusters_scores_df['key'])
scaled_scores = scaled_scores[['key']+metrics]
print('scaled_scores df')
print(scaled_scores)

# Plot
x, y = scaled_scores[metrics[1]], scaled_scores[metrics[0]]
plt.scatter(x, y, marker='.', s=20)
plt.xlabel(metrics[1])
plt.ylabel(metrics[0])
plt.savefig('std_wcss.png')
plt.show()


