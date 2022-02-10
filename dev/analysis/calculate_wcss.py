import re
import os
import time
from concurrent.futures import ProcessPoolExecutor
from matplotlib import pyplot as plt
import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None, 'display.max_colwidth', 100)
import numpy as np
from scipy.spatial.distance import pdist, squareform
from sentence_transformers import SentenceTransformer, util
transformer_model = SentenceTransformer('all-MiniLM-L6-v2')

data_dir = 'C:\\Users\\RonyArmon\\Projects_Code\\Cluster_Activities\\results'
results_dir = os.path.join(data_dir, 'clusters')
Agg_Clust_path = os.path.join(results_dir, 'AgglomerativeClustering_affinityEuclidean')
clusters_files = os.listdir(Agg_Clust_path)
clusters_files = [f for f in clusters_files if (('.xlsx' in f) & ('~$' not in f))]


def calculate_wcss(clusters_file):
    print('file:', clusters_file)
    name = clusters_file.replace('.xlsx', '')
    file_df = pd.read_excel(os.path.join(Agg_Clust_path, clusters_file))
    clusters = list(file_df['cluster'].unique())
    wcss = 0 #wcss
    for cluster in clusters:
        #print('cluster:', cluster)
        cluster_names = list(file_df['name'][file_df['cluster']==cluster])
        names_embeddings = transformer_model.encode(cluster_names, convert_to_tensor=True)
        names_embeddings = np.array(names_embeddings)
        cluster_distances = squareform(pdist(names_embeddings, 'sqeuclidean'))
        Dr = np.sum(np.triu(cluster_distances))
        #print('cluster_Dr:', Dr)
        weighted_Dr = Dr/(2*len(cluster_names))
        #print('weighted_Dr=', weighted_Dr)
        wcss += weighted_Dr
        #print('pooled=', wcss)
    print('name, wcss:', name, wcss)
    return (name, wcss)

#clusters_files = clusters_files[:4]
def controller():
    start = time.time()
    wcsos = {}
    executor = ProcessPoolExecutor(6)
    for result in executor.map(calculate_wcss, clusters_files):
        name, wcss = result
        print('controller: name, wcss:', name, wcss)
        wcsos[name] = wcss
    executor.shutdown()
    print('wcsos', wcsos)
    results = []
    for k, v in wcsos.items():
        cluster_num = int(re.findall('(\d{1,})', k)[0])
        results.append([cluster_num, v])
    wcss = round(pd.DataFrame(results, columns=['num_clusters', 'score']).sort_values(by=['num_clusters'])).astype(int)
    print(wcss)
    wcss.to_excel('wcss.xlsx', index=False)
    nums_clusters, scores = list(wcss['num_clusters']), list(wcss['score'])
    plt.plot(nums_clusters, scores)
    plt.xlabel('Number of clusters')
    plt.ylabel('WCSS')
    plt.show()
    #fig1 = plt.gcf()
    plt.savefig('wcss.png')

    end = time.time()
    duration_secs = round(end - start, 2)
    duration_mins = round(duration_secs / 60, 2)
    print('run duration: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))

if __name__=="__main__":
    controller ()