# to add file metadata: https://stackoverflow.com/questions/22567306/how-to-upload-file-with-python-requests
import os
import requests
from setup import *
url = 'http://127.0.0.01:6001/analysis'
print('data_files_paths')
print(data_files_paths)
files = []
file_key_num = 0

for data_file_name in data_files_names:
    #file_key_num += 1
    #file_key = 'key_{n}'.format(n=file_key_num)
    path = os.path.join(raw_data_dir, data_file_name)
    files.append(('file', (data_file_name, open(path, 'rb'))))
print('++ files ++')
for f in files: print(f)
r = requests.post(url, files=files)
print(r.text)