import os

from modules.utils import *
from modules.clustering import *
from modules.cluster_names import *

transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
gen_start = time.time()
durations = []
checked = []

# todo: update upload or pipeline to allow more then one project in the data path
projects = parse_graphml_file(data_path)
ids = list(projects[ids_col])
names = list(projects[names_col])
print('{} names'.format(len(names)))
tokens = tokenize(names, is_list=True, exclude_stopwords=True, \
                  exclude_numbers=True, exclude_digit_tokens=True)
print('{} unique tokens'.format(len(names)))
with open(os.path.join(results_dir, tokens_file), 'w') as f:
    for token in tokens: f.write('{t}\n'.format(t=token))
tokens_similarity = run_similarity(tokens, 6)
tokens_similarity.to_pickle(os.path.join(results_dir, 'tokens_similarity.pkl'))
print('distance similarity calculated')

names_embeddings = transformer_model.encode(names, convert_to_tensor=True)
X = np.array(names_embeddings)
print(X.shape)
model_params['n_clusters'] = int(len(names)*n_clusters_perc/100)
model_conf = model_conf_instance(model_name, model_params)
clustering = model_conf.fit(X)
clusters_labels = list(clustering.labels_)

# Write results to excel (for monitoring, remove in integration)
file_name = results_file_name(model_name, model_params) + '.xlsx'
projects['cluster'] = clusters_labels
print(projects.info())
print(projects[[ids_col, names_col, 'cluster']].head())
projects.to_excel('results.xlsx', index=False)

# Cluster names
clusters = list(projects['cluster'].unique())
# for cluster in clusters:
#     #print('cluster', cluster)
#     cluster_names = list(projects[names_col][projects['cluster'] == cluster])
#     cluster_key = find_matches(cluster_names, tokens_similarity)
#     #print(30*'='+'\n{ck}\n--------'.format(ck=cluster_key))
#     #for n in cluster_names: print(n)

response, validation_response = build_clusters_response(projects, clusters, tokens_similarity)
with open(os.path.join(results_dir, "{p}_validation_response.json".format(p=project_name)), "w") as outfile:
    outfile.write(response)
with open(os.path.join(results_dir, "{p}_response.json".format(p=project_name)), "w") as outfile:
    outfile.write(validation_response)

