from modules.libraries import *
from modules.config import *
from modules.utils import *
from modules.tokenizers import *
from clustering import *
from modules.tokenizers import normalize_texts

distance_matrices = []
# Todo when integrated to pipeline use matrices_dir from config
matrices = os.listdir(matrices_dir)
for matrix in matrices:
    path = os.path.join(matrices_dir, matrix)
    distance_matrices.append(pd.read_pickle(path))

def text_to_key(tasks_part, cutoff=0.4):
    cluster_key = ''
    names_tokens = {}
    for name in tasks_part:
        tokens = tokenize(name, unique=True, exclude_stopwords=False, \
                           exclude_numbers=True, exclude_digit_tokens=True)
        names_tokens[name] = tokens
    tasks_part_pairs = tuple(combinations(tasks_part, 2))
    pairs_matches = []
    source_tokens = [] # Store for all tokens in cluster names
    for name_pair in tasks_part_pairs:
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
    for name_pair in tasks_part_pairs: names += name_pair
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

def parts_to_texts(id_cluster_tasks):
    '''
    Split a group of using a splitter symbol (e.g. hyphen) to produce lists of the phrase parts
    Splitter: ' - '
    '''
    # Store tasks names parts by their location relative to a hyphen break in each name
    tasks_parts = defaultdict(list)
    cluster_id, cluster_tasks1 = id_cluster_tasks
    task_var_type = type(cluster_tasks1[0])

    # When called from grouped clusters the data is a list of strings (task names), without the task ids
    if task_var_type == str: cluster_tasks = [p for p in cluster_tasks1]
    else: cluster_tasks = [p[0] for p in cluster_tasks1]
    for task in cluster_tasks:
        delimiters = ' - |/|\(|\)|\[|\]' # To keep parenthesis use ' - |/|,(\(.+?\))'
        task_split = [i.rstrip().lstrip() for i in re.split(delimiters, task) if i]
        # Number of parts produced by a hyphen break
        num_parts = len(task_split)
        parts_indices = np.arange(num_parts)
        for index in parts_indices:
            tasks_parts[index].append(task_split[index])
    tasks_parts = dict(tasks_parts)
    key_parts = ['']
    uppercased_tokens_dicts = []
    for index, tasks_part in tasks_parts.items():
        if len(tasks_part) > 1:
            tasks_part_tokens = tokenize_texts(tasks_part, unique=True, exclude_stopwords=False, \
                                           exclude_numbers=True, exclude_digit_tokens=True, lowercased=False)
            uppercased_tokens_dict = build_uppercased_tokens_dict(tasks_part_tokens)
            uppercased_tokens_dicts.append(uppercased_tokens_dict)

            # Get key by the task part
            parts_key = text_to_key(tasks_part, cutoff=0.8)
            if parts_key:
                part_key_tokens = tokenize(parts_key, unique=True, exclude_stopwords=False, \
                                           exclude_numbers=True, exclude_digit_tokens=True)
                # Re-order the key words by their typical order in the task parts
                tokens_typical_locations = get_tokens_locations(tasks_part)
                key_tokens_locations = {k: v for k, v in tokens_typical_locations.items() if k in part_key_tokens}
                sorted_key_tokens_locations = {k: v for k, v in sorted(key_tokens_locations.items(), key=lambda item: item[1])}
                parts_key = ' '.join(list(sorted_key_tokens_locations.keys()))
                parts_key = string.capwords(parts_key)
                key_parts.append(parts_key)
    key_parts = [i for i in key_parts if i]
    if not key_parts:
        if normalize(cluster_tasks[0]):
            key_parts = [normalize(cluster_tasks[0])]
    entity_labels = ['<number><name>', '<name><number>', '<task>', '<number>']
    key_parts1 = []
    for key_part in key_parts:
        key_part = key_part.replace('> <', '><')
        # Clear entity or number tags if they open a task name part
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
    if not key.rstrip().lstrip(): key = cluster_tasks[0]
    return cluster_id, key


def key_clusters(clusters, num_executors, to_group=True):
    '''
    Derive keys for clusters using the names of the tasks grouped in each cluster
    :param clusters (dict): Lists of task names/ids tuples, keyed by the cluster numeric key.
    For example:
    clusters ['1'] = [('Technical presentations and questions delivery to customer', 'CUS0080'),
    ('Customer Presentations', 'CUS0090')]
    '''
    executor = ProcessPoolExecutor(num_executors)
    cluster_ids = list(clusters.keys())

    # Prepare names with ids for parallelized execution of the naming operation
    ids_norm_names = []
    for cluster_id in cluster_ids:
        names = [n[0] for n in clusters[cluster_id]]
        norm_names = list(set(normalize_texts(names)))
        ids_norm_names.append((cluster_id, norm_names))

    # Cluster names by cluster keys
    named_clusters = {}
    for cluster_id, cluster_key in executor.map(parts_to_texts, ids_norm_names):
        cluster_id_key = str((cluster_id, cluster_key))
        cluster_tasks_ids = clusters[cluster_id]
        named_clusters[cluster_id_key] = cluster_tasks_ids
        executor.shutdown()
    print('{n} clusters prior to grouping'.format(n=len(named_clusters)))
    # Group clusters
    if to_group:
        grouped_clusters = {}
        cluster_keys = get_clusters_keys(named_clusters)
        merged_clusters_keys = group_clusters(cluster_keys)
        print('{n} cluster groups'.format(n=len(merged_clusters_keys)))
        keys_merged = []
        for keys in merged_clusters_keys: keys_merged += list(keys)
        print('{n} clusters merged:'.format(n=len(keys_merged)))
        ## Determine grouped cluster names
        # Collect merged clusters tasks
        merged_cluster_id_clusters_keys = []
        cluster_id_tasks = {}
        for cluster_id, merged_clusters in enumerate(merged_clusters_keys):
            cluster_tasks = names_for_keys(named_clusters, merged_clusters)
            cluster_id_tasks[cluster_id] = cluster_tasks
            norm_names = list(set(normalize_texts(cluster_tasks)))
            merged_cluster_id_clusters_keys.append((cluster_id, norm_names))
        # Rename the merged clusters using their tasks
        executor = ProcessPoolExecutor(num_executors)
        for cluster_id, merged_clsuters_key \
               in executor.map(parts_to_texts, merged_cluster_id_clusters_keys):
            grouped_clusters[(cluster_id, merged_clsuters_key)] = cluster_id_tasks[cluster_id]
        executor.shutdown()

    # Exclude grouped clusters from named clusters
    named_clusters = {k: v for k, v in named_clusters.items() if k not in keys_merged}
    print('{n} clusters that were not grouped'.format(n=len(named_clusters)))
    print('{n} clusters that were grouped'.format(n=len(grouped_clusters)))
    clusters = {**named_clusters, **grouped_clusters}
    print('{n} grouped and not grouped clusters'.format(n=len(clusters)))
    return clusters