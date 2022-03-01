from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
from difflib import SequenceMatcher
import pandas as pd

distance_matrices = []
tokens_path = '/results/CLP_CCGT/tokens.txt'
tokens = open(tokens_path).read().split('\n')
print('{n} tokens'.format(n=len(tokens)))
tokens = [t for t in tokens if t]
tokens = tokens[:10]

# LCS tokens distances: lcs_distances
print('LCS distance')
tokens_pairs = tuple(combinations(tokens, 2))
print('{n} token pairs'.format(n=len(tokens_pairs)))
print('token pairs sample:', tokens_pairs[:5])

def lcs_similarity(token_pair):
    token1, token2 = token_pair
    #print('token1, token2:', token1, token2)
    score = SequenceMatcher(None, token1, token2).ratio()
    #print('score:', score)
    return (token_pair, score)

def lcs_scores(tokens_pairs, num_executors):
    c = 0
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
            c += 1
            #if c<10:
            print('--------')
            print('token_pair:', token_pair)
            print('tokens_scores:', tokens_scores)
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

num_executors = 1
lcs_distances = lcs_scores(tokens_pairs, num_executors)
distance_matrix = scoresToMatrix(lcs_distances)
distance_matrix.to_excel('lcs_distance_matrix.xlsx')