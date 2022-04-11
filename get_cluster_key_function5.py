import os
import sys
modules_dir = os.path.join(os.getcwd(), 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
from libraries import *
from config import *
from parsers import *
from utils import *
from modules.tokenizers import *
from aws.s3 import *

db_name = 'CAdb'
conn_params = {'host': 'localhost', 'user':'rony', 'password':'exp8546$fs', 'database': db_name}
conn = mysql.connect(**conn_params)
cur = conn.cursor()
cur.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

def results_from_table(experiment_id, ids=False, result_key='clusters'):
    result_df = pd.read_sql_query("SELECT * FROM results \
    WHERE experiment_id={eid}".format(eid=experiment_id), conn)
    result = result_df['result'].values[0]
    result = ast.literal_eval(result)
    if result_key == 'clusters':
        result_key = [c for c in result.keys() if 'duration' not in c][0]
    result = result[result_key]
    clusters = {}
    for k, v in result.items():
        # if len(k.split(' ')) > 1:
        if not ids:
            v = [i[1] for i in v]
        clusters[k] = v
    return clusters

experiment_id = 232
clustering_result = results_from_table(experiment_id)

############### build response functions ##############
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
                        all_in = all(x in matrix.columns for x in tokens_pair)
                        if all_in:
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

# todo: names to cluster_id
def parts_to_texts(cluster_names):
#def parts_to_texts(cluster_id):
    '''
    Split a group of using a splitter symbol (e.g. hyphen) to produce lists of the phrase parts
    Splitter: ' - '
    '''
    # Store names parts by their location relative to a hyphen break in each name
    names_parts = defaultdict(list)
    # todo: names to cluster_id
    #cluster_names = clustering_result[cluster_id]
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
    for index, names_part in names_parts.items():
        if len(names_part) > 1:
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
    key = key.lstrip('-')
    if not key.rstrip().lstrip(): key = cluster_names[0]
    # todo: return cluster_id, key
    return key
#######################################################
distance_matrices = []
paths = get_s3_paths(ds_bucket_obj, matrices_dir)
for path in paths:
    file = load_pickle_file(path, s3, ds_bucket, matrices_dir)
    distance_matrices.append(file)

tokens_not_in_matrices = []
#cluster_ids = list(clustering_result.keys())
#########################################################################################
single_word_key = []
for key, names in clustering_result.items():
    if ((key == 'Condenser') & (len(key.split(' ')) == 1) & (len(names[0].split(' ')) > 1)):
    #if ((len(key.split(' ')) == 1) & (len(names[0].split(' ')) > 1)):
        single_word_key.append(key)
        print(60*'+')
        print('key:', key)
        print((4+len(key))*'=')
        for name in names: print(name)
        key = parts_to_texts(names)
        print((4+len(key))*'-')
        print('new key:', key)
print('{n1} of a total of {n2} clusters have a single word key:\n'\
      .format(n1=len(single_word_key), n2=len(clustering_result)), single_word_key)
tokens_not_in_matrices = list(set(tokens_not_in_matrices))
print('Tokens not in matrices:', tokens_not_in_matrices)
