import os
import time
import psycopg2
import pandas.io.sql as sqlio
from sqlalchemy import create_engine
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None, 'display.max_colwidth', 100)
import numpy as np
from sentence_transformers import SentenceTransformer, util
from modules.clustering import *

gen_start = time.time()

durations = []
conn = psycopg2.connect("user=postgres password='1234'")
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
cur = conn.cursor()
db_name = 'ccgt'
engine = create_engine('postgresql+psycopg2://postgres:1234@localhost/{db}'.format(db=db_name))  #:5432
projects = sqlio.read_sql_query('SELECT * FROM projects', engine)
ids = list(projects['Activity ID'])
names = list(projects['Activity Name'])
print('{} names'.format(len(names)))

names = list(projects['Activity Name'].unique())
print('{} names'.format(len(names)))
start = time.time()
transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
end = time.time()
duration_secs = round(end - start, 2)
duration_mins = round(duration_secs / 60, 2)
print('load model duration: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))
durations.append(['load_model', duration_secs])

start = time.time()
names_embeddings = transformer_model.encode(names, convert_to_tensor=True)
X = np.array(names_embeddings)
end = time.time()
duration_secs = round(end - start, 2)
duration_mins = round(duration_secs / 60, 2)
print('encoding duration: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))
durations.append(['data_encoding', duration_secs])

def run_get_clusters(n_clusters):
    model_name = 'AgglomerativeClustering'
    affinity = 'euclidean'
    hyper_params_conf = {'n_clusters': n_clusters, 'affinity': affinity}
    print('model params:', hyper_params_conf)
    file_name = results_file_name(model_name, hyper_params_conf)+'.xlsx'
    print('file_name:', file_name)
    clustering, clusters_df = get_clusters(X, names, model_name, hyper_params_conf)
    return file_name, clusters_df

n_clusters = [300, 600, 900, 1200, 1500, 1800]

def controller():
    start = time.time()
    executor = ProcessPoolExecutor(6)
    for file_name, clusters_df in executor.map(run_get_clusters, n_clusters):
        print('n_clusters:', n_clusters)
        print(clusters_df.head())
        clusters_df.to_excel(file_name, index=False)

    end = time.time()
    duration_secs = round(end - start, 2)
    duration_mins = round(duration_secs / 60, 2)
    print('clustering duration: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))
    durations.append(['clustering', duration_secs])

    durations_df = pd.DataFrame(durations, columns=['action', 'durations(secs)'])
    if len(n_clusters) == 1: file_name = 'single_cluster_durations_300.xlsx'
    else: file_name = '{n}_clusters_duration.xlsx'.format(n=len(n_clusters))
    durations_df.to_excel(os.path.join(file_name), index=False)

    gen_end = time.time()
    duration_secs = round(gen_end - gen_start, 2)
    duration_mins = round(duration_secs / 60, 2)
    print('all process duration: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))
    durations.append(['load_model', duration_secs])


if __name__=="__main__":
    controller ()
