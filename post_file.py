# to add file metadata: https://stackoverflow.com/questions/22567306/how-to-upload-file-with-python-requests
from setup import *
import requests
print('Service running locally?', local_service)
if local_service:
    url = 'http://127.0.0.01:6002/cluster_analysis/api/v0.1/clustering'
else:
    url = 'http://172.31.36.11/cluster_analysis/api/v0.1/clustering'
print('url:', url)
print('Raw data path:', data_path)
files = {'file': open(data_path, 'rb')}
r = requests.post(url, files=files)
print(r.text)