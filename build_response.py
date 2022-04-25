from modules.libraries import *
from modules.config import *
from modules.utils import *
from modules.tokenizers import *

print('Building response')
experiment_id, best_run_id, file_names_str = sys.argv[1], sys.argv[2], sys.argv[3]
print('experiment_id:', experiment_id)
print('best_run_id:', best_run_id)
print('file_names_str in build response:', file_names_str)
experiment_dir_name = 'experiment_{id}'.format(id=experiment_id)
experiment_dir = os.path.join(results_dir, experiment_dir_name)
run_dir = os.path.join(experiment_dir, 'runs', best_run_id)
references_dir = os.path.join(run_dir, 'references')
print('reference dictionaries directory:', references_dir)

distance_matrices = []
matrices = os.listdir(matrices_dir)
for matrix in matrices:
    path = os.path.join(matrices_dir, matrix)
    print('path:', path)
    distance_matrices.append(pd.read_pickle(path))

def text_to_key(cluster_names, cutoff=0.4):
    cluster_key = ''
    names_tokens = {}
    for name in cluster_names:
        tokens = tokenize(name, unique=True, exclude_stopwords=False, \
                           exclude_numbers=True, exclude_digit_tokens=True)
        names_tokens[name] = tokens
    #print('names_tokens:', names_tokens)
    cluster_names_pairs = tuple(combinations(cluster_names, 2))
    pairs_matches = []
    source_tokens = [] # Store for all tokens in cluster names
    for name_pair in cluster_names_pairs:
        name1, name2 = name_pair
        tokens1, tokens2 = names_tokens[name1], names_tokens[name2]
        source_tokens = source_tokens + tokens1 + tokens2
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

    # Score each match by it's length in relation to the cluster_key lengths
    names = []
    for name_pair in cluster_names_pairs: names += name_pair
    names_lengths_median = np.median(np.array([len(name) for name in names]))
    for pair_matches in pairs_matches:
        if names_lengths_median>0:
            near_median_factor = len(pair_matches)/names_lengths_median
            match_scores[pair_matches] = near_median_factor * match_scores[pair_matches]
        else: match_scores[pair_matches] = 0
    # Identify the best scoring match
    max_score = max(list(match_scores.values()))
    for pair_matches, match_score in match_scores.items():
        if match_score == max_score:
            cluster_key = pair_matches

    cluster_key = ' '.join(list(set(cluster_key)))
    return cluster_key

def parts_to_texts(cluster_id):
    '''
    Split a group of using a splitter symbol (e.g. hyphen) to produce lists of the phrase parts
    Splitter: ' - '
    '''
    # Store names parts by their location relative to a hyphen break in each name
    names_parts = defaultdict(list)
    cluster_names = clustering_result[cluster_id]
    for name in cluster_names:
        delimiters = ' - |/|\(|\)|\[|\]' # To keep parenthesis use ' - |/|,(\(.+?\))'
        name_split = [i.rstrip().lstrip() for i in re.split(delimiters, name) if i]

        # Number of parts produced by a hyphen break
        num_parts = len(name_split)
        parts_indices = np.arange(num_parts)
        for index in parts_indices:
            names_parts[index].append(name_split[index])
    names_parts = dict(names_parts)
    key_parts = ['']

    names_parts_tokens = []
    uppercased_tokens_dicts = []
    for index, names_part in names_parts.items():
        if len(names_part) > 1:
            names_part_tokens = tokenize_texts(names_part, unique=True, exclude_stopwords=False, \
                                           exclude_numbers=True, exclude_digit_tokens=True, lowercased=False)
            print('names_part_tokens:', names_part_tokens)
            uppercased_tokens_dict = build_uppercased_tokens_dict(names_part_tokens)
            print('uppercased_tokens_dict:', uppercased_tokens_dict)
            uppercased_tokens_dicts.append(uppercased_tokens_dict)


            # Get key by the name part
            parts_key = text_to_key(names_part, cutoff=0.8)
            if parts_key:
                part_key_tokens = tokenize(parts_key, unique=True, exclude_stopwords=False, \
                                           exclude_numbers=True, exclude_digit_tokens=True)
                # Re-order the key words by their typical order in the name parts
                tokens_typical_locations = get_tokens_locations(names_part)
                key_tokens_locations = {k: v for k, v in tokens_typical_locations.items() if k in part_key_tokens}
                sorted_key_tokens_locations = {k: v for k, v in sorted(key_tokens_locations.items(), key=lambda item: item[1])}
                parts_key = ' '.join(list(sorted_key_tokens_locations.keys()))
                parts_key = string.capwords(parts_key)
                key_parts.append(parts_key)
    key_parts = [i for i in key_parts if i]
    if not key_parts:
        if normalize(cluster_names[0]):
            key_parts = [normalize(cluster_names[0])]
    entity_labels = ['<number><name>', '<name><number>', '<name>', '<number>']
    key_parts1 = []
    for key_part in key_parts:
        key_part = key_part.replace('> <', '><')
        # Clear entity or number tags if they open a name part
        for label in entity_labels:
            label_pattern = '^\s*{p}*\s*{l}+'.format(l=label, p=punctuation_marks)
            if re.findall(label_pattern, key_part):
                key_part = re.sub(label_pattern, '', key_part)
                key_part = key_part.lstrip().rstrip()
        key_parts1.append(key_part)
    key_parts1 = [p for p in key_parts1 if p]
    key = ' - '.join(key_parts1)
    key = key.replace('&amp', '')
    key = re.sub('/|,|;', '-', key)
    key = re.sub('^[\s|{p}|-]*'.format(p=punctuation_marks), '', key)
    key = key.lstrip('-').replace('{{', '').replace('}}', '')

    # Normalize uppercased entities
    uppercased_tokens_dicts = reduce(lambda aggr, new: aggr.update(new) or aggr, uppercased_tokens_dicts, {})
    if uppercased_tokens_dicts:
        key_tokens = key.split(' ')
        key_tokens = replace_uppercased(key_tokens, uppercased_tokens_dicts)
        key = ' '.join(key_tokens)

    if not key.rstrip().lstrip(): key = cluster_names[0]
    return cluster_id, key

# Todo: re-test performance with 1 vs 4 executors
num_executors = 1
def key_clusters(clustering_result, num_executors):
    executor = ProcessPoolExecutor(num_executors)
    cluster_ids = list(clustering_result.keys())
    named_clusters, named_clusters_ids = {}, {}
    for cluster_id, cluster_key in executor.map(parts_to_texts, cluster_ids):
        activities_ids = clusters_namesIDs[cluster_id]
        named_clusters[cluster_key] = list(zip(activities_ids, clustering_result[cluster_id]))
        named_clusters[cluster_key] = [tuple(i) for i in named_clusters[cluster_key]]
        named_clusters_ids[cluster_key] = activities_ids
    executor.shutdown()
    # Todo integration: replace clusters by the identifier(s) defined for the response
    named_clusters = {'clusters': named_clusters}
    return named_clusters, named_clusters_ids

# Experiment result (to build as response)
clustering_result = {}
if 'clustering_result.npy' in os.listdir(references_dir):
    clustering_result = np.load(os.path.join(references_dir, 'clustering_result.npy'), allow_pickle=True)[()]
    print('clustering_result example:', list(clustering_result.items())[:1])
print(100*'-')
if 'clusters_namesIDs.npy' in os.listdir(run_dir):
    clusters_namesIDs = np.load(os.path.join(run_dir, 'clusters_namesIDs.npy'), allow_pickle=True)[()]
    print('clusters_namesIDs example:', list(clusters_namesIDs.items())[:1])

named_clusters, named_clusters_ids = key_clusters(clustering_result, num_executors)
np.save(os.path.join(results_dir, 'named_clusters.npy'), named_clusters)
np.save(os.path.join(results_dir, 'named_clusters_ids.npy'), named_clusters_ids)
print(100*'-')
cluster_names = sorted(list(named_clusters['clusters'].keys()))
cluster_names = '\n'.join(cluster_names)