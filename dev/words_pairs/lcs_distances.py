from concurrent.futures import ProcessPoolExecutor
import cProfile
import numpy as np
from difflib import SequenceMatcher
from itertools import combinations
import time
pr = cProfile.Profile()
start = time.time()
num_executors = 12
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

tokens = open('results/tokens.txt').read().split('\n')
tokens = list(set(tokens))
tokens = [t for t in tokens if t]
print('{n} tokens'.format(n=len(tokens)))

pr.enable()
tokens_pairs = list(combinations(tokens, 2))
print('names_pairs_indices sample')
print(tokens_pairs[:10])
print('Calculate lcs distances for {n} tokens pairs'.format(n=len(tokens_pairs)))
# tokens_pairs = tokens_pairs[:100000]
# print('Calculate lcs distances for {n} tokens pairs'.format(n=len(tokens_pairs)))
start1 = time.time()
names_pairs_lcs_distances = lcs_scores(tokens_pairs, num_executors)
write_duration('distances calculations', start=start1)
#for cluster_key, distance in names_pairs_lcs_distances.items(): print(cluster_key, distance)
write_duration('distances calculations', start=start1)

pr.disable()
#pr.print_stats(sort='time')
