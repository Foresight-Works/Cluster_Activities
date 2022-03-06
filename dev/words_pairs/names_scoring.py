from setup import *

def filter_embeddings(vocab_tokens, embeddings):
    '''
    Filter embeddings dictionary for the vectors of a given vocabulary
    :param vocab_tokens(list): The tokens of an input vocabulary
    :param embeddings (dictionary): Embedding vectors obtained from a language model, keyed by tokens
    '''
    vocab_embeddings, not_in_vocabulary = {}, []
    for token in vocab_tokens:
        try:
            vocab_embeddings[token] = embeddings[token]
        except KeyError as e:
            if 'not in vocabulary' in str(e):
                not_in_vocabulary.append(token)
    return vocab_embeddings, not_in_vocabulary

def lcs_similarity(token_pair):
    token1, token2 = token_pair
    score = SequenceMatcher(None, token1, token2).ratio()
    return (token_pair, score)

def lcs_scores(tokens_pairs, num_executors):
    tokens_scores = {}
    executor = ProcessPoolExecutor(num_executors)
    chunksize = int(len(tokens_pairs)/(10*num_executors))
    print('chunksize=', chunksize)
    if num_executors > 1:
        for token_pair, score in executor.map(lcs_similarity, tokens_pairs, chunksize=chunksize):
            tokens_scores[token_pair] = score
        executor.shutdown()
    else:
        for token_pair, score in map(lcs_similarity, tokens_pairs):
            tokens_scores[token_pair] = score
    return tokens_scores

def scoresToMatrix(token_pairs_scores):
    token_pairs = list(token_pairs_scores.keys())
    #print('token_pairs sample:', token_pairs[:2])
    tokens = []
    for tokens_pair in token_pairs: tokens += list(tokens_pair)
    unique_tokens = list(set(tokens))
    matrix = pd.DataFrame(index=unique_tokens, columns=unique_tokens)
    for token_pair, score in token_pairs_scores.items():
        #print(token_pair, score)
        token1, token2 = token_pair
        matrix.at[token1, token2] = score
    matrix = matrix.fillna(0)
    return (matrix)

# Read reference dictionaries
names_tokens, tokens_pairs_scores, response = {}, {}, {}
if 'names_tokens.npy' in os.listdir(results_dir):
    names_tokens = np.load(os.path.join(results_dir, 'names_tokens.npy'), allow_pickle=True)[()]
if 'tokens_pairs_scores.npy' in os.listdir(results_dir):
    names_tokens = np.load(os.path.join(results_dir, 'tokens_pairs_scores.npy'), allow_pickle=True)[()]
if 'response.npy' in os.listdir(results_dir):
    names_tokens = np.load(os.path.join(results_dir, 'response.npy'), allow_pickle=True)[()]

## Source: evaluate script ##
def countClusterTokens(cluster):
    cluster_names = response[cluster]
    tokens = []
    for name in cluster_names: tokens += names_tokens[name]
    return (len(tokens))

def scoreNamesPair(names_pair):
    name1, name2 = names_pair
    tokens1, tokens2 = names_tokens[name1], names_tokens[name2]
    names_token_pairs = list(itertools.product(tokens1, tokens2))
    names_pair_score = 0
    for tokens_pair in names_token_pairs:
        names_pair_score += tokens_pairs_scores[tokens_pair]
        # print(tokens_pair, names_pair_score)
    return names_pair_score

def scoreCluster(cluster, cluster_name_pairs):
    cluster_score = 0
    for names_pair in cluster_name_pairs:
        name1, name2 = names_pair
        tokens1, tokens2 = names_tokens[name1], names_tokens[name2]
        names_token_pairs = list(itertools.product(tokens1, tokens2))
        names_pair_score = 0
        for tokens_pair in names_token_pairs:
            names_pair_score += tokens_pairs_scores[tokens_pair]

        cluster_score += scoreNamesPair(names_pair)
    cluster_score = cluster_score/countClusterTokens(cluster)
    return cluster, round(cluster_score, 2)

def scoreClusters(clusters, clusters_names_pairs, num_executors):
    executor = ProcessPoolExecutor(num_executors)
    clusters_scores = {}
    for cluster, cluster_score in executor.map(scoreCluster, clusters, clusters_names_pairs):
        #print('cluster and score:', cluster, cluster_score)
        clusters_scores[cluster] = cluster_score
    executor.shutdown()
    #write_duration('clusters scoring', start=start1)

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
        names = response[cluster]
        for n in names: print(n)
    print(40*'*')
    print('cluster scored as nan')
    for cluster in nan_scored: print(cluster)
    # Mean score per cluster
    return round(sum(list(clusters_scores.values()))/len(clusters_scores), 2)
