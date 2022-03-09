# to add file metadata: https://stackoverflow.com/questions/22567306/how-to-upload-file-with-python-requests
from setup import *
import requests
print('Service running locally?', local_service)
if local_service == 'True':
    url = 'http://127.0.0.01:6002/cluster_analysis/api/v0.1/clustering'
else:
    url = 'http://172.31.36.11/cluster_analysis/api/v0.1/clustering'
print('url:', url)
print('Raw data path:', data_path)
files = {'file': open(data_path, 'rb')}
experiment_ids = pd.read_sql_query("SELECT experiment_id from experiments", conn).astype(int)
if len(experiment_ids) == 0: experiment_id = 1
else: experiment_id = int(max(experiment_ids.values)[0]) + 1
print('experiment_id:', experiment_id)
r = requests.post(url, files=files, data={'experiment_id': 1})
print(r.text)