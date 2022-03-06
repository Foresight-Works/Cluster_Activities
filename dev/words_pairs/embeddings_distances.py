import cProfile
pr = cProfile.Profile()
import numpy as np
import gensim.downloader as api
from itertools import combinations
from scipy.spatial.distance import pdist
import time
start = time.time()
def filter_embeddings(vocab_tokens, embeddings):
    '''
    Filter embeddings dictionary for the vectors of a given vocabulary
    :param vocab_tokens(list): The tokens of an input vocabulary
    :param embeddings (dictionary): Embedding vectors obtained from a language model, keyed by tokens
    '''
    vocab_embeddings, not_in_vocabulary = {}, []
    for token in vocab_tokens:
        try:
            vocab_embeddings[token] = embeddings[token]#.reshape(1, -1)
        except KeyError as e:
            if 'not in vocabulary' in str(e):
                not_in_vocabulary.append(token)
    return vocab_embeddings, not_in_vocabulary

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

language_model_name = 'glove-twitter-25'
tokens = open('results/tokens.txt').read().split('\n')
tokens = list(set(tokens))
print('{n} tokens'.format(n=len(tokens)))
pr.enable()
print('load embeddings')
tokens_embeddings = api.load("{m}".format(m=language_model_name))
vocab_embeddings, not_in_vocabulary = filter_embeddings(tokens, tokens_embeddings)
print('vocab embmedding sample:', list(vocab_embeddings.items())[:2])

# Name pairs indices
tokens = list(vocab_embeddings.keys())
names_pairs_indices = list(combinations(tokens, 2))
print('names_pairs_indices sample')
print(names_pairs_indices[:10])

embeddings_vectors = np.stack(list(vocab_embeddings.values()))
num_vectors = len(embeddings_vectors)
print('Calculate embedding distances for {nv} vectors using pdist'.format(nv=num_vectors))
print(embeddings_vectors.shape)
start1 = time.time()
embeddings_distances = pdist(embeddings_vectors)
write_duration('distances calculations', start=start1)
print('Condensed results')
print(embeddings_distances)

result = dict(zip(names_pairs_indices, embeddings_distances))
for names, distance in result.items(): print(names, distance)

pr.disable()
#pr.print_stats(sort='time')
