from setup import *

transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
gen_start = time.time()
durations = []

checked = []

def run_similarity(tokens, num_executors):
    results_df = pd.DataFrame(columns=tokens, index=tokens)
    tokens_scores = []
    executor = ProcessPoolExecutor(num_executors)
    for result in executor.map(calc_similarity, tokens):
        tokens_scores += result
    executor.shutdown()

    for result in tokens_scores:
        token1, token2, similarity = result
        similarity = round(similarity, 2)
        results_df.at[token1, token2] = similarity

    end = time.time()
    duration_secs = round(end - start, 2)
    duration_mins = round(duration_secs / 60, 2)
    print('similarity calculation took {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))

    return results_df

projects = parse_graphml_file(data_path)
ids = list(projects[ids_col])
names = list(projects[names_col])
print('{} names'.format(len(names)))
tokens = tokenize(names, is_list=True, exclude_stopwords=True, \
                  exclude_numbers=True, exclude_digit_tokens=True)
print('{} unique tokens'.format(len(names)))

def calc_similarity(token1, tokens=tokens):
    '''
    Calculate token similarity for input token compared to all tokens
    from a list of tokens and cluster tokens that are more similar than the
    specified threshold.
    '''
    token_scores = []
    if token1 not in checked:
        checked.append(token1)
        for token2 in tokens:
            score = similar(token1, token2)
            token_scores.append((token1, token2, score))
    return token_scores

tokens_similarity = run_similarity(tokens, 6)
tokens_similarity.to_pickle(os.path.join(results_dir, 'words_pairs.pkl'))
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
for cluster in clusters:
    print('cluster', cluster)
    cluster_names = list(projects[names_col][projects['cluster'] == cluster])
    cluster_key = find_matches(cluster_names, tokens_similarity)
    print(30*'='+'\n{ck}\n--------'.format(ck=cluster_key))
    for n in cluster_names: print(n)

response, validation_response = build_clusters_response(clusters)
with open("validation_response.json", "w") as outfile:
    outfile.write(response)
with open("response.json", "w") as outfile:
    outfile.write(validation_response)

