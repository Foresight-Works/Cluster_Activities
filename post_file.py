# to add file metadata: https://stackoverflow.com/questions/22567306/how-to-upload-file-with-python-requests
from setup import *
import requests
if config.get('service', 'local'):
    url = config.get('service', 'local_url')
else:
    url = config.get('service', 'dev_url')

print('Data path:', data_path)
files = {'file': open(data_path, 'rb')}
r = requests.post(url, files=files)
print(r.text)