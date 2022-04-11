import requests
from requests.auth import HTTPBasicAuth
url = 'http://172.31.34.107:15672/api/queues/%2F/'
login = 'rnd'
password = 'Rnd@2143'
response = requests.get(url, auth=HTTPBasicAuth(login, password))
res_json = response.json()
q_names = []
for q in res_json: q_names.append(q['name'])
print('queue names:', q_names)