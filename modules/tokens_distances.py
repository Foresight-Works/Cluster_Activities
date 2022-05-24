import sys
sys.path = sys.path[1:] + sys.path[:1]
from modules.libraries import *
from modules.config import *

def string_similarity_ratio(token_pair):
    token1, token2 = token_pair
    score = Levenshtein.ratio(token1, token2)
    return (token_pair, score)

def run_string_similarity_ratio(tokens, num_executors):
    # Exclude entities from tokens (<name>, <number>)
    tokens = [t for t in tokens if not re.findall('<.*>', t)]
    tokens_pairs = tuple(combinations(tokens, 2))
    tokens_scores = {}
    executor = ProcessPoolExecutor(num_executors)
    num_pairs = len(tokens_pairs)
    chunksize = int(num_pairs/(20*num_executors))
    if num_executors > 1:
        for token_pair, score in executor.map(string_similarity_ratio, tokens_pairs, chunksize=chunksize):
            tokens_scores[token_pair] = score
            del token_pair, score
        executor.shutdown()
    else:
        for token_pair, score in map(string_similarity_ratio, tokens_pairs):
            tokens_scores[token_pair] = score
    return tokens_scores

def scoresToMatrix(token_pairs_scores, fillna_value):
    token_pairs = list(token_pairs_scores.keys())
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
        token1, token2 = token_pair
        matrix.at[token1, token2] = score
    matrix = matrix.fillna(fillna_value)
    matrix = matrix.sort_index().sort_index(axis=1)
    return (matrix)

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


def build_embeddings_distance_matrix(tokens, tokens_model):
    # Exclude entities from tokens (<name>, <number>)
    tokens = [t for t in tokens if not re.findall('<.*>', t)]

    # Embedding vectors
    tokens_embeddings = api.load("{m}".format(m=tokens_model))
    vocab_embeddings, not_in_vocabulary = filter_embeddings(tokens, tokens_embeddings)

    # Embedding vectors distances: names_pairs_distances
    embeddings_vectors = np.stack(list(vocab_embeddings.values()))
    embedding_tokens = list(vocab_embeddings.keys())
    names_pairs_indices = list(combinations(embedding_tokens, 2))
    embeddings_distances = pdist(embeddings_vectors, metric='euclidean')
    embeddings_distances = dict(zip(names_pairs_indices, embeddings_distances))
    distance_matrix = scoresToMatrix(embeddings_distances, 0)
    mn, mx = distance_matrix.min(), distance_matrix.max()
    mn, mx = min(mn), max(mx)
    scaled_matrix = (distance_matrix - mn) / (mx - mn)
    scaled_matrix = scaled_matrix.replace(0, 1)
    scaled_matrix = scaled_matrix.sort_index().sort_index(axis=1)
    return scaled_matrix

def build_distance_matrices(tokens):
    print('{n} tokens, sample:'.format(n=len(tokens)), tokens[:10])
    edit_distances = run_string_similarity_ratio(tokens, num_executors)
    edit_distances = scoresToMatrix(edit_distances, 1)
    embeddings_distance_matrix = build_embeddings_distance_matrix(tokens, tokens_model)
    distance_matrices = [edit_distances, embeddings_distance_matrix]
    return distance_matrices