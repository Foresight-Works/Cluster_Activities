from concurrent.futures import ProcessPoolExecutor
import gensim.downloader as api
import pandas as pd
import os
import time
import nltk
from sklearn.metrics.pairwise import cosine_similarity
# model_name = 'word2vec-google-news-300'
model_name = 'glove-twitter-25'


# Tokens
results_dir = 'C:\\Users\\RonyArmon\\Projects_Code\\Cluster_Activities\\results'
unique_names = open(os.path.join(results_dir, 'names.txt')).read().split('\n')
print('{n} unique names tokenized'.format(n=len(unique_names)))
tokens = []
for name in unique_names:
    name_tokens = nltk.word_tokenize(name)
    tokens += name_tokens
tokens = list(set(tokens))
print('{} tokens'.format(len(tokens)))

# Embedding model
model_glove_twitter = api.load("{m}".format(m=model_name))
print('embedding model loaded')

# Get embedding vectors for the vocabulary tokens
tokens_embeddings, not_in_vocabulary = {}, []
for token in tokens:
    try:
        tokens_embeddings[token] = model_glove_twitter[token].reshape(1, -1)
    except KeyError as e:
        if 'not in vocabulary' in str(e):
            not_in_vocabulary.append(token)
print('{} tokens in twitter vocabulary'.format(len(tokens)))
results_dir = os.path.join(results_dir, 'similarity')
with open(os.path.join(results_dir, 'not_in_{m}.txt'.format(m=model_name)), 'w') as f:
    for i in not_in_vocabulary:
        f.write('{i}\n'.format(i=i))


# Calculate cosine similarity between vocabulary tokens
tokens = [t for t in tokens if t not in not_in_vocabulary]
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
        embed1 = tokens_embeddings[token1]
        checked.append(token1)
        for token2 in tokens:
            embed2 = tokens_embeddings[token2]
            score = float(cosine_similarity(embed1, embed2))
            token_scores.append((token1, token2, score))
    return token_scores

results_df = pd.DataFrame(columns=tokens, index=tokens)
for token in tokens:
    token_scores = calc_similarity(token)
    for result in token_scores:
        token1, token2, similarity = result
        similarity = round(similarity, 2)
        #print(token1, token2, similarity)
        results_df.at[token1, token2] = similarity

end = time.time()
duration_secs = round(end - start, 2)
duration_mins = round(duration_secs / 60, 2)
print('run duration: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))


print('\nresults:')
print(results_df)
results_df.to_pickle(os.path.join(results_dir, '{m}.pkl'.format(m=model_name)))


# def controller():
#     results_df = pd.DataFrame(columns=tokens, index=tokens)
#     tokens_scores = []
#     executor = ProcessPoolExecutor(6)
#     for result in executor.map(calc_similarity, tokens):
#         # print(result)
#         tokens_scores += result
#     executor.shutdown()
#
#     for result in tokens_scores:
#         token1, token2, similarity = result
#         similarity = round(similarity, 2)
#         results_df.at[token1, token2] = similarity
#
#     end = time.time()
#     duration_secs = round(end - start, 2)
#     duration_mins = round(duration_secs / 60, 2)
#     print('run duration: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))
#     print('\nresults:')
#     print(results_df)
#     print(results_df.columns)
#     results_df.to_pickle('./results/glove-twitter-25.pkl')
#
# if __name__=="__main__":
#     controller ()
