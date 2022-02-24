# to add file metadata: https://stackoverflow.com/questions/22567306/how-to-upload-file-with-python-requests
from setup import *
import requests

if config.get('service', 'local'):
    url = config.get('service', 'local_url')
else:
    url = config.get('service', 'dev_url')

print('n_clusters_percs:', n_clusters_percs)
zip_file = config.get('data', 'file')
print('zip file:', zip_file)

experiment_id = 1
data_path = os.path.join(data_dir, zip_file)
data = {'experiment_id': experiment_id}
print('params:', data)
print('Data path:', data_path)
file = {'file': open(data_path, 'rb')}
r = requests.post(url, files=file, data=data)
print(r.text)