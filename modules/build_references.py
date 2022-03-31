from setup import *
from modules.tokenizers import *
from modules.utils import *

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

def string_similarity_ratio(token_pair):
    token1, token2 = token_pair
    score = Levenshtein.ratio(token1, token2)
    return (token_pair, score)

def run_string_similarity_ratio(tokens_pairs, num_executors):
    tokens_scores = {}
    executor = ProcessPoolExecutor(num_executors)
    chunksize = int(len(tokens_pairs)/(10*num_executors))
    if num_executors > 1:
        for token_pair, score in executor.map(string_similarity_ratio, tokens_pairs, chunksize=chunksize):
            tokens_scores[token_pair] = score
        executor.shutdown()
    else:
        for token_pair, score in map(string_similarity_ratio, tokens_pairs):
            tokens_scores[token_pair] = score
    return tokens_scores

def scoresToMatrix(token_pairs_scores, fillna_value):
    token_pairs = list(token_pairs_scores.keys())
    #print('token_pairs sample:', token_pairs[:2])
    tokens = []
    for tokens_pair in token_pairs: tokens += list(tokens_pair)
    unique_tokens = list(set(tokens))
    matrix = pd.DataFrame(index=unique_tokens, columns=unique_tokens)
    reversed_pairs_scores = {}
    for token_pair, score in token_pairs_scores.items():
        reversed_pair = (token_pair[1], token_pair[0])
        reversed_pairs_scores[reversed_pair] = score
    token_pairs_scores = {**token_pairs_scores, **reversed_pairs_scores}
    for token_pair, score in token_pairs_scores.items():
        #print(token_pair, score)
        token1, token2 = token_pair
        matrix.at[token1, token2] = score
    matrix = matrix.fillna(fillna_value)
    return (matrix)

def reference_dictionaries(clustering_result, references_dir, distance_matrices):
    start = time.time()
    print('building reference dictionaries')
    np.save(os.path.join(references_dir, 'clustering_result.npy'), clustering_result)
    clusters, clusters_names = list(clustering_result.keys()), list(clustering_result.values())
    unique_clusters = list(set(clusters))
    print('{n1} clusters | {n2} unique clusters'.format(n1=len(clusters), n2=len(unique_clusters)))
    names = []
    for cluster_names in clusters_names: names += cluster_names
    names = list(set(names))
    print('{n} unique cluster_key'.format(n=len(names)))
    names_tokens = {}

    # Reference dictionary: Tokens per Name (names_tokens)
    for name in names:
        tokens = tokenize(name, unique=True, exclude_stopwords=True, \
                           exclude_numbers=True, exclude_digit_tokens=True)
        names_tokens[name] = tokens
    np.save(os.path.join(references_dir, 'names_tokens.npy'), names_tokens)
    print('{n} cluster_key tokens values in dictionary'.format(n=len(names_tokens)))
    print('examples:', list(names_tokens.items())[:2])

    # Reference list: Names pairs (names_pairs)
    # Reference dictionary: Names pairs per cluster(clusters_names_pairs)
    names_pairs, clusters_names_pairs = (), {}
    for cluster, clusters_names in clustering_result.items():
        clusters_name_pairs = tuple(combinations(clusters_names, 2))
        if clusters_name_pairs:
            names_pairs += clusters_name_pairs
            clusters_names_pairs[cluster] = clusters_name_pairs
    np.save(os.path.join(references_dir, 'clusters_names_pairs.npy'), clusters_names_pairs)
    print('{n} cluster_key pairs'.format(n=len(names_pairs)))
    print('example:', names_pairs[:2])
    print('{n} clusters_names_pairs'.format(n=len(clusters_names_pairs)))
    #print('example:', list(clusters_names_pairs.items())[:2])

    # Reference list: Tokens pairs (tokens_pairs)
    tokens_pairs = []
    for name_pair in names_pairs:
        name_pairs_tokens1, name_pairs_tokens2 = names_tokens[name_pair[0]], names_tokens[name_pair[1]]
        tokens_pairs += list(itertools.product(name_pairs_tokens1, name_pairs_tokens2))
    print('{n} token pairs'.format(n=len(tokens_pairs)))
    print('examples:', tokens_pairs[:2])

    # Reference dictionaries: Tokens pairs - Similarity scores (tokens_pairs_scores)
    start1 = time.time()
    tokens_pairs_scores = {}
    for token_pair in tokens_pairs:
        for matrix in distance_matrices:
            scores = []
            if all(t in matrix.columns for t in token_pair):
                score = matrix.at[token_pair[0], token_pair[1]]
            else: score = 0
            scores.append(score)
        tokens_pairs_scores[token_pair] = sum(scores)
    print('{n} token pairs scores'.format(n=len(tokens_pairs_scores)))
    print('examples:', list(tokens_pairs_scores.items())[:2])
    np.save(os.path.join(references_dir, 'tokens_pairs_scores.npy'), tokens_pairs_scores)
    write_duration('scoring cluster_key pairs by matrices', start=start1)
    write_duration('References preparation', start=start)