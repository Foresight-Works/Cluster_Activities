import numpy as np
import pandas as pd
from itertools import combinations
from scipy.spatial.distance import pdist
import gensim.downloader as api
from sklearn.preprocessing import MinMaxScaler

def filter_embeddings(vocab_tokens, embeddings):
    '''
    Filter embeddings dictionary for the vectors of a given vocabulary
    :param vocab_tokens(list): The tokens of an input vocabulary
    :param embeddings (dictionary): Embedding vectors obtained from a language model, keyed by tokens
    '''
    c = 0
    vocab_embeddings, not_in_vocabulary = {}, []
    for token in vocab_tokens:
        if c < 11:
            try:
                vocab_embeddings[token] = embeddings[token]
                c += 1
            except KeyError as e:
                if 'not in vocabulary' in str(e):
                    not_in_vocabulary.append(token)
    return vocab_embeddings, not_in_vocabulary

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

tokens = open('tokens.txt').read().split('\n')
print('{n} tokens'.format(n=len(tokens)))
tokens = [t for t in tokens if t]
print('load embeddings')
tokens_embeddings = api.load("glove-twitter-25")
vocab_embeddings, not_in_vocabulary = filter_embeddings(tokens, tokens_embeddings)
print('vocab_embeddings sample', list(vocab_embeddings.items())[:3])
embeddings_vectors = np.stack(list(vocab_embeddings.values()))
num_vectors = len(embeddings_vectors)
embedding_tokens = list(vocab_embeddings.keys())
names_pairs_indices = list(combinations(embedding_tokens, 2))
print('names_pairs_indices sample')
print(names_pairs_indices[:10])
embeddings_distances = pdist(embeddings_vectors, metric='euclidean')
embeddings_distances = dict(zip(names_pairs_indices, embeddings_distances))
distance_matrix = scoresToMatrix(embeddings_distances, 0)
scaler = MinMaxScaler()
print('distance_matrix')
print(distance_matrix)
distance_matrix.to_excel('distance_matrix.xlsx')
mn, mx = distance_matrix.min(), distance_matrix.max()
print('mn, mx:', mn, mx)
mn, mx = min(mn), max(mx)
print('mn, mx:', mn, mx)
scaled_matrix = (distance_matrix - mn) / (mx - mn)
scaled_matrix = scaled_matrix.replace(0, 1)
print('scaled_matrix')
print(scaled_matrix)
scaled_matrix.to_excel('scaled_distance_matrix.xlsx')