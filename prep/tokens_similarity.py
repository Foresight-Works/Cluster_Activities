import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from concurrent.futures import ProcessPoolExecutor
import re
import os
import time

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

results_dir = 'C:\\Users\\RonyArmon\\Projects_Code\\Cluster_Activities\\results'
pos_df = pd.read_pickle(os.path.join(results_dir, 'pos.pkl'))
#print('{} rows'.format(len(pos_df)))
#print(pos_df.head())
tokens = list(set(pos_df['token']))
#tokens = tokens[:10]
print('{} tokens'.format(len(tokens)))

start = time.time()
checked = []
def calc_similarity (token1):
    '''
    Calculate token similarity for input token compared to all tokens
    from a list of tokens and cluster tokens that are more similar than the
    specified threshold.
    '''
    token_scores = []
    if token1 not in checked:
        checked.append(token1)
        for token2 in tokens:
            score = similar(token1, token2)
            token_scores.append((token1, token2, score))
    return token_scores

# results_df = pd.DataFrame(columns=tokens, index=tokens)
# for token in tokens:
#     token_scores = calc_similarity(token)
#     for result in token_scores:
#         token1, token2, similarity = result
#         similarity = round(similarity,2)
#         results_df.at[token1, token2] = similarity
# print('\nresults:')
# print(results_df)

def controller():
    results_df = pd.DataFrame(columns=tokens, index=tokens)
    tokens_scores = []
    executor = ProcessPoolExecutor(6)
    for result in executor.map(calc_similarity, tokens):
        # print(result)
        tokens_scores += result
    executor.shutdown()

    for result in tokens_scores:
        token1, token2, similarity = result
        similarity = round(similarity, 2)
        results_df.at[token1, token2] = similarity

    end = time.time()
    duration_secs = round(end - start, 2)
    duration_mins = round(duration_secs / 60, 2)
    print('run duration: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))
    print('\nresults:')
    print(results_df)
    print(results_df.columns)
    results_df.to_pickle(os.path.join(results_dir, 'tokens_similarity.pkl'))

if __name__=="__main__":
    controller ()
