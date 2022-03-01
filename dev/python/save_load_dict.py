import numpy as np
clustering_result = {1: {'a':1, 'b': 2, 'c':3}}
np.save('clustering_result.npy', clustering_result)
clustering_result = np.load('clustering_result.npy', allow_pickle=True)[()]
print('clustering_result pre naming')
print(clustering_result)
run_id = list(clustering_result.keys())[0]
clustering_result = list(clustering_result.values())[0]
print('run id:', run_id, type(run_id))
print('clustering_results only')
print(clustering_result)
