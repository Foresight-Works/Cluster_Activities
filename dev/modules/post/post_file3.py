# to add file metadata: https://stackoverflow.com/questions/22567306/how-to-upload-file-with-python-requests
import requests
decision = input('post locally(y)?')
if decision == 'y':
    url = 'http://127.0.0.01:6002/cluster_analysis/api/v0.1/clustering'
else:
    #Remote (routing by Nginx)
    url = 'http://172.31.36.11/cluster_analysis/api/v0.1/clustering'

print('Raw response path:', data_path)
files = {'file': open(data_path, 'rb')}
r = requests.post(url, files=files)
print(r.text)