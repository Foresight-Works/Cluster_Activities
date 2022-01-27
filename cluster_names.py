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
start = time.time()
from modules.clustering import *

data_dir = 'C:\\Users\\RonyArmon\\Projects_Code\\Cluster_Activities\\results'
results_dir = os.path.join(data_dir, 'clusters')

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

transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
end = time.time()
duration_secs = round(end - start, 2)
duration_mins = round(duration_secs / 60, 2)
print('prep duration: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))

start = time.time()
names_embeddings = transformer_model.encode(names, convert_to_tensor=True)
X = np.array(names_embeddings)
end = time.time()
duration_secs = round(end - start, 2)
duration_mins = round(duration_secs / 60, 2)
print('encoding duration: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))

start = time.time()
model_name = 'AgglomerativeClustering'
n_clusters = 1000
affinity = 'euclidean'
hyper_params_conf = {'n_clusters': n_clusters, 'affinity': affinity}
print('model params:', hyper_params_conf)
file_name = results_file_name(model_name, hyper_params_conf)
print('file_name:', file_name)
clustering, clusters_df = get_clusters(X, names, model_name, hyper_params_conf)
clusters_df.to_excel(os.path.join(results_dir, '{fn}.xlsx'.format(fn=file_name)), index=False)

end = time.time()
duration_secs = round(end - start, 2)
duration_mins = round(duration_secs / 60, 2)
print('clustering duration: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))