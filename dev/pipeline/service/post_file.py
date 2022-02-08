# to add file metadata: https://stackoverflow.com/questions/22567306/how-to-upload-file-with-python-requests
import requests
#from setup import *
url = 'http://127.0.0.01:6001/analysis'
raw_data_path = '/data/misc/project1.graphml'
print('raw_data_path:', raw_data_path)
files = {'file': open(raw_data_path, 'rb')}
r = requests.post(url, files=files)