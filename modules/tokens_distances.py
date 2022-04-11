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
    with open(os.path.join(results_dir, 'not_in_embedding_vocabulary.txt'), 'w') as f:
        for t in not_in_vocabulary: f.write('{t}\n'.format(t=t))
    #print('vocab_embeddings sample', list(vocab_embeddings.items())[:3])

    # Embedding vectors distances: names_pairs_distances
    embeddings_vectors = np.stack(list(vocab_embeddings.values()))
    num_vectors = len(embeddings_vectors)
    embedding_tokens = list(vocab_embeddings.keys())
    names_pairs_indices = list(combinations(embedding_tokens, 2))
    #print('names_pairs_indices sample')
    #print(names_pairs_indices[:10])
    embeddings_distances = pdist(embeddings_vectors, metric='euclidean')
    embeddings_distances = dict(zip(names_pairs_indices, embeddings_distances))
    #print('{n} embeddings_distances values'.format(n=len(embeddings_distances)))
    #print('embeddings_distances sample:', list(embeddings_distances.items())[:2])
    embeddings_vectors = np.stack(list(vocab_embeddings.values()))
    num_vectors = len(embeddings_vectors)
    embedding_tokens = list(vocab_embeddings.keys())
    names_pairs_indices = list(combinations(embedding_tokens, 2))
    #print('names_pairs_indices sample')
    #print(names_pairs_indices[:10])
    embeddings_distances = pdist(embeddings_vectors, metric='euclidean')
    embeddings_distances = dict(zip(names_pairs_indices, embeddings_distances))
    distance_matrix = scoresToMatrix(embeddings_distances, 0)
    scaler = MinMaxScaler()
    #print('distance_matrix')
    #print(distance_matrix)
    mn, mx = distance_matrix.min(), distance_matrix.max()
    #print('mn, mx:', mn, mx)
    mn, mx = min(mn), max(mx)
    #print('mn, mx:', mn, mx)
    scaled_matrix = (distance_matrix - mn) / (mx - mn)
    scaled_matrix = scaled_matrix.replace(0, 1)
    #print('scaled_matrix')
    #print(scaled_matrix)
    scaled_matrix = scaled_matrix.sort_index().sort_index(axis=1)
    return scaled_matrix

if __name__ == '__main__':
    tokens = open(tokens_path).read().split('\n')
    tokens = list(set(tokens))
    tokens = [t for t in tokens if t]
    print('{n} tokens, sample:'.format(n=len(tokens)), tokens[:10])
    edit_distances = run_string_similarity_ratio(tokens, num_executors)
    edit_distances = scoresToMatrix(edit_distances, 1)
    embeddings_distance_matrix = build_embeddings_distance_matrix(tokens, tokens_model)
    distance_matrices = [edit_distances, embeddings_distance_matrix]
    for index, matrix in enumerate(distance_matrices):
        matrix_file = 'matrix_{i}.pkl'.format(i=index)
        print('matrix_file:', matrix_file)
        matrix.to_pickle(matrix_file)
        s3_client.upload_file(matrix_file, ds_bucket, os.path.join(matrices_dir, matrix_file))
        os.remove(matrix_file)


