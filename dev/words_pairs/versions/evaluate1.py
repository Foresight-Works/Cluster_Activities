from setup import *
import itertools
num_executors = 8
start = time.time()
def print_duration(process, start_time=start):
    '''
    Print process processes. Place the function following the last line for the process measured
    :param process(str): The name of the process measured
    :param start_time (time.time(): The start time for the process
    '''
    duration_secs = round(time.time() - start1, 2)
    duration_mins = round(duration_secs / 60, 2)
    print('{p} took {ds} seconds, {dm} minutes'
          .format(p=process, ds=duration_secs, dm=duration_mins))

# Paths
results_dir = '../results'
matrices_dir = os.path.join(results_dir, 'distance_matrices')

# Data
f = open('../response/CCGT_878Clusters_validation_response.json', )
data = json.load(f)
clusters, cluster_names = list(data.keys()), list(data.values())
names = []
for n in cluster_names: names += n
names = list(set(names))
print('{n} unique cluster_key'.format(n=len(names)))
names_tokens = {}

# Reference dictionary: Distance matrices (distance_matrices)
matrices_files = os.listdir(matrices_dir)
print('matrices_files:', matrices_files)
distance_matrices = {}
for file in matrices_files:
    print('matrix file:', file)
    path = os.path.join(matrices_dir, file)
    df = pd.read_pickle(path)
    distance_matrices[file.split('.')[0]] = df
print('distance_matrices loaded')

# Reference dictionary: Tokens per Name (names_tokens)
for name in names:
    tokens = tokenize(name, unique=True, exclude_stopwords=True, \
                       exclude_numbers=True, exclude_digit_tokens=True)
    names_tokens[name] = tokens
print('{n} cluster_key tokens:'.format(n=len(names_tokens)))
print('examples:', list(names_tokens.items())[:2])

# Reference list: Names pairs (names_pairs)
# Reference dictionary: Names pairs per cluster
names_pairs, clusters_names_pairs = (), {}
for cluster, cluster_names in data.items():
    cluster_name_pairs = tuple(combinations(cluster_names, 2))
    names_pairs += cluster_name_pairs
    clusters_names_pairs[cluster] = cluster_name_pairs
print('{n} cluster_key pairs'.format(n=len(names_pairs)))
print('example:', names_pairs[:2])
print('{n} clusters_names_pairs'.format(n=len(clusters_names_pairs)))
print('example:', list(clusters_names_pairs.items())[:2])


# Reference list: Tokens pairs (token_pairs)
token_pairs = []
for name_pair in names_pairs:
    names_pairs_tokens1, names_pairs_tokens2 = names_tokens[name_pair[0]], names_tokens[name_pair[1]]
    token_pairs += list(itertools.product(names_pairs_tokens1, names_pairs_tokens2))
print('{n} token pairs'.format(n=len(token_pairs)))
print('example:', token_pairs[:2])

# Reference dictionaries: Tokens pairs - Similarity per Distance Matrix (token_pairs)

matrices_scores = {}
for file, matrix in distance_matrices.items():
    start1 = time.time()
    token_pairs_scores = {}
    for token_pair in token_pairs:
        token_pairs_scores[token_pair] = matrix.at[token_pair[0], token_pair[1]]
    matrices_scores[file.split('.')[0]] = token_pairs_scores
    print('{n} token pairs scores'.format(n=len(token_pairs_scores)))
    print('examples:', list(token_pairs_scores.items())[:2])
print_duration('scoring cluster_key pairs by matrices', start_time=start)

# Build a list(tuple) of token pairs (tuples)

def filterMatrixByTokens (names_pair, distance_matrix):
    '''
    Filter input distance matrix indexed by tokens to keep the columns and rows for the
    tokens in the input cluster_key
    '''
    name1, name2 = names_pair
    tokens1, tokens2 = names_tokens[name1], names_tokens[name2]
    tokens12 = tokens1 + tokens2
    unique_tokens12 = list(set(tokens12))
    return distance_matrix[unique_tokens12][distance_matrix.index.isin(unique_tokens12)]

def build_clusters_matrices(cluster, names):
    '''
    Identify the pair or cluster_key between each name in the cluster, and for each name pair, extract the
    distance matrices for the tokens of the cluster_key in this pair

    '''
    names_pairs = list(combinations(names, 2))
    names_pairs_matrices = {}
    for names_pair in names_pairs:
        pairs_matrices = []
        for distance_matrix in distance_matrices:
            tokens_matrix = filterMatrixByTokens(names_pair, distance_matrix)
            pairs_matrices.append(tokens_matrix)
        #print(pairs_matrices)
        names_pairs_matrices[names_pair] = tuple(pairs_matrices)
    return cluster, names_pairs_matrices

def scoreTokensPair(tokens, distance_matrix):
    '''
    Score a pair of tokens for similarity
    :param tokens_pair(tuple): The pair of tokens to score
    :param distance_matrix(df): The distance matrix to use in scoring
    '''
    return distance_matrix.at[tokens[0], tokens[1]]

# def scoreNamesPair(name_pair):
#     '''
#     Score a pair of cluster_key for similarity
#     '''
#     name1, name2 = name_pair
#     tokens1, tokens2 = names_tokens[name1], names_tokens[name2]
#     for token1 in tokens1:
#         token1_scores = []
#         for token2 in tokens2:
#             pair_score = 0
#             for name_pair_matrix in name_pair_matrices:
#                 pair_score += scoreTokensPair((token1, token2), name_pair_matrix)
#
#                     matrix.at[token1, token2]
#             token1_scores.append(pair_score)
#         token1_scores = [s for s in token1_scores if str(s) != 'nan']
#         if token1_scores:
#             token1_score = max(token1_scores)
#         else:
#             token1_score = 0
#         similarity_score += token1_score
#
#
# def words_pairs(cluster, names_pairs_matrices):
#     for name_pair_matrices in names_pairs_matrices:
#         name_pair, matrices = name_pair_matrices
#         similarity_score = 0
#         tokens = [] #change name
#
#
#         unique_tokens = list(set(tokens))
#         tokens_count = len(tokens)
#         if tokens_count > 0:
#             similarity_score = similarity_score/tokens_count
#             similarity_score = round(similarity_score, 2)
#         else: similarity_score = 0
#         return similarity_score
#
# def score_clusters(response, num_executors):
#     clusters_matrices = {}
#     executor = ProcessPoolExecutor(num_executors)
#     for cluster, names_pairs_matrices in executor.map(build_clusters_matrices, clusters, cluster_names):
#         print(cluster)
#         clusters_matrices[cluster] = names_pairs_matrices
#
#
#
#     executor.shutdown()
#     print(clusters_matrices)
#
# score_clusters(response, num_executors)
#

print_duration('complete scoring run')
