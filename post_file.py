# to add file metadata: https://stackoverflow.com/questions/22567306/how-to-upload-file-with-python-requests
from setup import *
import requests

if config.get('service', 'local'):
    url = config.get('service', 'local_url')
else:
    url = config.get('service', 'dev_url')
n_clusters_percs = config_vals('model', 'n_clusters_perc')
print('n_clusters_percs:', n_clusters_percs)
zipped_files = os.listdir(data_dir)
print('zipped files:', zipped_files)

experiment_id = 1
for zip_file in zipped_files:
    for n_clusters_perc in n_clusters_percs:
        run_start = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        data_path = os.path.join(data_dir, zip_file)
        data = {'n_clusters_perc': n_clusters_perc, 'run_start': run_start, 'experiment_id': experiment_id}
        print('params:', data)
        print('Data path:', data_path)
        files = {'file': open(data_path, 'rb')}
        r = requests.post(url, files=files, data=data)
        print(r.text)