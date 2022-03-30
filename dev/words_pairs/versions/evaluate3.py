from setup import *
import itertools
num_executors = 8
start = time.time()
def write_duration(process, start=start):
    '''
    Print process processes. Place the function following the last line for the process measured
    :param process(str): The name of the process measured
    :param start_time (time.time(): The start time for the process
    '''
    duration_secs = round(time.time() - start, 2)
    duration_mins = round(duration_secs / 60, 2)
    print('{p} took {ds} seconds, {dm} minutes'
          .format(p=process, ds=duration_secs, dm=duration_mins))

# Paths
results_dir = './results'
matrices_dir = os.path.join(results_dir, 'distance_matrices')

# Data
f = open('response/CCGT_878Clusters_validation_response.json', )
data = json.load(f)
clusters, cluster_names = list(data.keys()), list(data.values())
unique_clusters = list(set(clusters))
print('{n1} clusters | {n2} unique clusters'.format(n1=len(clusters), n2=len(unique_clusters)))
names = []
for n in cluster_names: names += n
names = list(set(names))
print('{n} unique cluster_key'.format(n=len(names)))
names_tokens = {}

# Reference dictionary: Tokens per Name (names_tokens)
for name in names:
    tokens = tokenize(name, unique=True, exclude_stopwords=True, \
                       exclude_numbers=True, exclude_digit_tokens=True)
    names_tokens[name] = tokens
print('{n} cluster_key tokens:'.format(n=len(names_tokens)))
print('examples:', list(names_tokens.items())[:2])

# Reference list: Names pairs (names_pairs)
# Reference dictionary: Names pairs per cluster(clusters_names_pairs)
names_pairs, clusters_names_pairs = (), {}
for cluster, cluster_names in data.items():
    clusters_name_pairs = tuple(combinations(cluster_names, 2))
    names_pairs += clusters_name_pairs
    clusters_names_pairs[cluster] = clusters_name_pairs
print('{n} cluster_key pairs'.format(n=len(names_pairs)))
print('example:', names_pairs[:2])
print('{n} clusters_names_pairs'.format(n=len(clusters_names_pairs)))
print('example:', list(clusters_names_pairs.items())[:2])

# Reference list: Tokens pairs (token_pairs)
token_pairs = []
for name_pair in names_pairs:
    name_pairs_tokens1, name_pairs_tokens2 = names_tokens[name_pair[0]], names_tokens[name_pair[1]]
    token_pairs += list(itertools.product(name_pairs_tokens1, name_pairs_tokens2))
print('{n} token pairs'.format(n=len(token_pairs)))
print('example:', token_pairs[0])


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

# Reference dictionaries: Tokens pairs - Similarity scores (distances)
start1 = time.time()
token_pairs_scores = {}
for token_pair in token_pairs:
    for file, matrix in distance_matrices.items():
        scores = []
        scores.append(matrix.at[token_pair[0], token_pair[1]])
    token_pairs_scores[token_pair] = sum(scores)
print('{n} token pairs scores'.format(n=len(token_pairs_scores)))
print('examples:', list(token_pairs_scores.items())[:2])
write_duration('scoring cluster_key pairs by matrices', start=start1)
write_duration('References preparation', start=start)

def countClusterTokens(cluster):
    cluster_names = data[cluster]
    tokens = []
    for name in cluster_names: tokens += names_tokens[name]
    return (len(tokens))

def scoreNamesPair(names_pair):
    name1, name2 = names_pair
    tokens1, tokens2 = names_tokens[name1], names_tokens[name2]
    names_token_pairs = list(itertools.product(tokens1, tokens2))
    names_pair_score = 0
    #print('names_token_pairs:', names_token_pairs)
    for tokens_pair in names_token_pairs:
        names_pair_score += token_pairs_scores[tokens_pair]
        #print(tokens_pair, names_pair_score)
    return names_pair_score

def scoreCluster(cluster):
    cluster_score = 0
    cluster_name_pairs = clusters_names_pairs[cluster]
    #print('cluster_name_pairs')
    #print(cluster_name_pairs)
    for names_pair in cluster_name_pairs:
        #print(names_pair)
        cluster_score += scoreNamesPair(names_pair)
    cluster_score = cluster_score/countClusterTokens(cluster)
    return cluster, round(cluster_score, 2)

def scoreClusters(clusters, num_executors):
    executor = ProcessPoolExecutor(num_executors)
    clusters_scores = {}
    for cluster, cluster_score in executor.map(scoreCluster, clusters):
        #print('cluster and score:', cluster, cluster_score)
        clusters_scores[cluster] = cluster_score
    executor.shutdown()
    write_duration('clusters scoring', start=start1)

    # Print results
    nan_scored = []
    for cluster in clusters:
        score = clusters_scores[cluster]
        if str(score) == 'nan':
            nan_scored.append(cluster)
        print(30 * '=')
        print('cluster:', cluster)
        print('score=', score)
        print(10 * '-')
        names = data[cluster]
        for n in names: print(n)
    print(40*'*')
    print('cluster scored as nan')
    for cluster in nan_scored: print(cluster)
    # Mean score per cluster
    return round(sum(list(clusters_scores.values()))/len(clusters_scores), 2)


start1 = time.time()
print('scoring {n} clusters'.format(n=len(clusters)))

eval_score = scoreClusters(clusters, num_executors)
print('eval_score:', eval_score)
write_duration('process')