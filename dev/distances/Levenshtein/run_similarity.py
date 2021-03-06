from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
import pandas as pd
import Levenshtein

def string_similarity_ratio(token_pair):
    token1, token2 = token_pair
    score = Levenshtein.ratio(token1, token2)
    return (token_pair, score)

def run_string_similarity_ratio(tokens_pairs, num_executors):
    c = 0
    tokens_scores = {}
    executor = ProcessPoolExecutor(num_executors)
    chunksize = int(len(tokens_pairs)/(10*num_executors))
    print('chunksize=', chunksize)
    if num_executors > 1:
        for token_pair, score in executor.map(string_similarity_ratio, tokens_pairs, chunksize=chunksize):
            tokens_scores[token_pair] = score
        executor.shutdown()
    else:
        for token_pair, score in map(string_similarity_ratio, tokens_pairs):
            tokens_scores[token_pair] = score
            print('--------')
            print('token_pair:', token_pair)
            print('tokens_scores:', tokens_scores)

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

num_executors = 1
distance_matrices = []
tokens_path = 'tokens.txt'
tokens = open(tokens_path).read().split('\n')
print('{n} tokens'.format(n=len(tokens)))
tokens = [t for t in tokens if t]
tokens = tokens[:10]

# LCS tokens distances: lcs_distances
tokens_pairs = tuple(combinations(tokens, 2))
print('{n} token pairs'.format(n=len(tokens_pairs)))
print('token pairs sample:', tokens_pairs)

pairs_distances = run_string_similarity_ratio(tokens_pairs, num_executors)
distance_matrix = scoresToMatrix(pairs_distances, 1)
distance_matrix.to_excel('pairs_distances.xlsx')