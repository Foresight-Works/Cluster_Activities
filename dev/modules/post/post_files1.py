# to add file metadata: https://stackoverflow.com/questions/22567306/how-to-upload-file-with-python-requests
import os
import requests
from setup import *

user = 'rnd'
password = 'Rnd@2143'
url = 'http://127.0.0.01:6001/cluster_analysis/api/v0.1/clustering'
# Remote
#url = 'http://172.31.36.11:5000/analysis'

print('data_files_paths')
print(data_files_paths)
files = []
file_key_num = 0

for data_file_name in data_files_names:
    path = os.path.join(raw_data_dir, data_file_name)
    files.append(('file', (data_file_name, open(path, 'rb'))))
print('++ files ++')
for f in files: print(f)
r = requests.post(url, files=files)
#r = requests.post(url, files=files, auth=(user, password))
print(r.text)