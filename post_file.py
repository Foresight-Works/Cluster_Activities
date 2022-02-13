# to add file metadata: https://stackoverflow.com/questions/22567306/how-to-upload-file-with-python-requests
from setup import *
import requests
url = 'http://127.0.0.01:6002/cluster_analysis/api/v0.1/clustering'
# Remote (routing by Nginx)
# url = 'http://172.31.36.11/cluster_analysis/api/v0.1/clustering'

print('Raw data path:', raw_data_file)
files = {'file': open(raw_data_file, 'rb')}
r = requests.post(url, files=files)
print(r.text)