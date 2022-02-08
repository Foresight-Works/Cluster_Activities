import os

from modules.utils import *
from modules.clustering import *
from modules.cluster_names import *

transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
durations = []

# todo: update upload or pipeline to allow more then one project in the data path
projects = parse_graphml_file(data_path)
ids = list(projects[ids_col])
names = list(projects[names_col])
print('{} names'.format(len(names)))
tokens = tokenize(names, is_list=True, exclude_stopwords=True, \
                  exclude_numbers=True, exclude_digit_tokens=True)
with open(os.path.join(results_dir, tokens_file), 'w') as f:
    for token in tokens: f.write('{t}\n'.format(t=token))
tokens_similarity = run_similarity(tokens, 6)
tokens_similarity.to_pickle(os.path.join(results_dir, 'tokens_similarity.pkl'))

names_embeddings = transformer_model.encode(names, convert_to_tensor=True)
X = np.array(names_embeddings)
model_params['n_clusters'] = int(len(names)*n_clusters_perc/100)
model_conf = model_conf_instance(model_name, model_params)
clustering = model_conf.fit(X)
clusters_labels = list(clustering.labels_)

# Response
clusters = list(projects['cluster'].unique())
response, validation_response = build_clusters_response(projects, clusters, tokens_similarity)
with open(os.path.join(results_dir, "{p}_validation_response.json".format(p=project_name)), "w") as outfile:
    outfile.write(response)
with open(os.path.join(results_dir, "{p}_response.json".format(p=project_name)), "w") as outfile:
    outfile.write(validation_response)

