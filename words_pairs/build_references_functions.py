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

