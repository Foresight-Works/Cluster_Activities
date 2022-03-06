from setup import *
distance_matrices = []
matrices = os.listdir(matrices_dir)
for matrix in matrices:
    path = os.path.join(matrices_dir, matrix)
    distance_matrices.append(pd.read_pickle(path))

# Read reference dictionaries
clustering_result, names_tokens, tokens_pairs_scores, clusters_names_pairs = {}, {}, {}, {}
if 'clustering_result.npy' in os.listdir(results_dir):
    clustering_result = np.load(os.path.join(results_dir, 'clustering_result.npy'), allow_pickle=True)[()]
    #print('clustering_result example:', list(names_tokens.items())[:1])
best_score_run_id = str(list(clustering_result.keys())[0])
clustering_result = list(clustering_result.values())[0]
# Read experiment id
experiment_ids = pd.read_sql_query("SELECT experiment_id from experiments", conn).astype(int)
experiment_id = int(max(experiment_ids.values)[0])
print('experiment_id:', experiment_id)
experiment_dir_name = 'experiment_{id}'.format(id=experiment_id)
experiment_dir = os.path.join(results_dir, experiment_dir_name)
print('experiment_dir:', experiment_dir)
run_dir = os.path.join(experiment_dir, 'runs', best_score_run_id)
references_dir = os.path.join(run_dir, 'references')

if 'names_tokens.npy' in os.listdir(references_dir):
    names_tokens = np.load(os.path.join(references_dir, 'names_tokens.npy'), allow_pickle=True)[()]
if 'tokens_pairs_scores.npy' in os.listdir(references_dir):
    tokens_pairs_scores = np.load(os.path.join(references_dir, 'tokens_pairs_scores.npy'), allow_pickle=True)[()]
if 'clusters_names_pairs.npy' in os.listdir(references_dir):
    clusters_names_pairs = np.load(os.path.join(references_dir, 'clusters_names_pairs.npy'), allow_pickle=True)[()]
if 'clusters_namesIDs.npy' in os.listdir(run_dir):
    clusters_namesIDs = np.load(os.path.join(run_dir, 'clusters_namesIDs.npy'), allow_pickle=True)[()]

def tokens_count(tokens):
    counts = dict()
    for token in tokens:
        if token in counts:
            counts[token] += 1
        else:
            counts[token] = 1
    return counts

def get_cluster_key(cluster_id, cutoff=0.8):
    cluster_names_pairs = clusters_names_pairs[cluster_id]
    pairs_matches = []
    for name_pair in cluster_names_pairs:
        name1, name2 = name_pair
        tokens1, tokens2 = names_tokens[name1], names_tokens[name2]
        tokens1 = [t.lower() for t in tokens1]
        tokens2 = [t.lower() for t in tokens2]
        if name1 == name2:
            pair_matches = tokens1
        else:
            len1, len2 = len(tokens1), len(tokens2)
            if len1 <= len2:
                short_name_tokens, long_name_tokens = tokens1, tokens2
            else: short_name_tokens, long_name_tokens = tokens2, tokens1
            pair_matches = []
            for short_name_token in short_name_tokens:
                short_name_token = [short_name_token]
                names_token_pairs = list(itertools.product(short_name_token, long_name_tokens))
                token_pairs_scores = {}
                for tokens_pair in names_token_pairs:
                    # Use distance matrices to score token pairs
                    token1, token2 = tokens_pair
                    token_pairs_score = 0
                    for index, matrix in enumerate(distance_matrices):
                        if all(x in matrix.columns for x in tokens_pair):
                            matrix_score = matrix.at[token1, token2]
                        else: matrix_score = 0
                        token_pairs_score += matrix_score
                    token_pairs_score = round(token_pairs_score, 2)
                    token_pairs_scores[tokens_pair] = token_pairs_score

                # Identify the best match in the long name to the short name token
                max_score = max(list(token_pairs_scores.values()))
                if max_score >= cutoff:
                    for tokens_pair, pair_score in token_pairs_scores.items():
                        if pair_score == max_score: matched_token = tokens_pair[1]
                    #print('matched token with best score:', matched_token)
                    pair_matches.append(matched_token)

        pairs_matches.append(tuple(pair_matches))
    matches_tokens = []
    for pair_matches in pairs_matches: matches_tokens += list(pair_matches)
    matches_tokens_counts = tokens_count(matches_tokens)

    # Score each match by the frequency of its tokens
    match_scores = {}
    for pair_matches in pairs_matches:
        match_score = 0
        for token in pair_matches:
            match_score += matches_tokens_counts[token]
        match_scores[pair_matches] = match_score

    # Score each match by it's length in relation to the names lengths
    names = []
    for name_pair in cluster_names_pairs: names += name_pair
    names_lengths_median = np.median(np.array([len(name) for name in names]))
    for pair_matches in pairs_matches:
        near_median_factor = len(pair_matches)/names_lengths_median
        match_scores[pair_matches] = near_median_factor * match_scores[pair_matches]

    # Identify the best scoring match
    max_score = max(list(match_scores.values()))
    for pair_matches, match_score in match_scores.items():
        if match_score == max_score:
            cluster_key = pair_matches

    cluster_key = ' '.join(list(set(cluster_key)))
    return cluster_id, cluster_key

def key_clusters(clustering_result, num_executors):
    executor = ProcessPoolExecutor(num_executors)
    cluster_ids = list(clustering_result.keys())
    named_clusters, named_clusters_ids = {}, {}
    for cluster_id, cluster_key in executor.map(get_cluster_key, cluster_ids):
        named_clusters[cluster_key] = clustering_result[cluster_id]
        activities_ids = clusters_namesIDs[cluster_id]
        named_clusters_ids[cluster_key] = activities_ids
    executor.shutdown()
    named_clusters = {best_score_run_id: named_clusters}
    return named_clusters, named_clusters_ids

num_executors = int(config.get('run', 'num_executors'))
named_clusters, named_clusters_ids = key_clusters(clustering_result, num_executors)
np.save(os.path.join(results_dir, 'named_clusters.npy'), named_clusters)
np.save(os.path.join(results_dir, 'named_clusters_ids.npy'), named_clusters_ids)
