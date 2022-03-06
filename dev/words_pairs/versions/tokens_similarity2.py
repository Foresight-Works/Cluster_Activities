import pandas as pd

from setup import *
def lcs_similarity(token1, token2):
    return SequenceMatcher(None, token1, token2).ratio()
def embedding_similarity(embed1, embed2):
    return float(cosine_similarity(embed1, embed2))

start = time.time()
checked = []
tokens_size = 2639


def filter_embeddings(vocab_tokens, embeddings):
    '''
    Filter embeddings dictionary for the vectors of a given vocabulary
    :param vocab_tokens(list): The tokens of an input vocabulary
    :param embeddings (dictionary): Embedding vectors obtained from a language model, keyed by tokens
    '''
    vocab_embeddings, not_in_vocabulary = {}, []
    for token in vocab_tokens:
        try:
            vocab_embeddings[token] = embeddings[token].reshape(1, -1)
        except KeyError as e:
            if 'not in vocabulary' in str(e):
                not_in_vocabulary.append(token)
    return vocab_embeddings, not_in_vocabulary

def calc_similarity(token1, function):
    if 'tokens.txt' in os.listdir(results_dir):
        tokens = open(os.path.join(results_dir, 'tokens.txt')).read().split('\n')
    else: tokens = []
    tokens = tokens[:tokens_size]
    if 'vocab_embeddings.npy' in os.listdir(results_dir):
        vocab_embeddings = np.load(os.path.join(results_dir, 'vocab_embeddings.npy'), allow_pickle=True)[()]
    else: vocab_embeddings = {}
    token_scores = []
    if token1 not in checked:
        checked.append(token1)
        for token2 in tokens:
            score = 0
            if function == lcs_similarity: score = function(token1, token2)
            elif function == embedding_similarity:
                if all(t in list(vocab_embeddings.keys()) for t in [token1, token2]):
                    score = function(vocab_embeddings[token1], vocab_embeddings[token2])
            if score != 0:
                token_scores.append((token1, token2, round(score, 2)))
    return token_scores

def run_similarity(tokens, num_executors, function):
    print('running the local version of run_similarity')
    results_df = pd.DataFrame(columns=tokens, index=tokens)
    tokens_scores = []
    executor = ProcessPoolExecutor(num_executors)
    function_list = len(tokens)*[function]
    print(len(tokens), len(function_list))
    if num_executors > 1:
        for result in executor.map(calc_similarity, tokens, function_list):
            tokens_scores += result
        executor.shutdown()
    else:
        for result in map(calc_similarity, tokens, function_list):
            tokens_scores += result

    for result in tokens_scores:
        token1, token2, score = result
        results_df.at[token1, token2] = score
    return results_df

function = lcs_similarity # embedding_similarity
num_executors = 8


results_dir = '../results'
print('tokens and embeddings')
model_name = config.get('language_models', 'tokens')
tokens_embeddings = api.load("{m}".format(m=model_name))
tokens = open(os.path.join(results_dir, 'tokens.txt')).read().split('\n')
tokens = tokens[:tokens_size]
vocab_embeddings, not_in_vocabulary = filter_embeddings(tokens, tokens_embeddings)
np.save(os.path.join(results_dir, 'vocab_embeddings.npy'), vocab_embeddings)
tokens_similarity = run_similarity(tokens, num_executors, function)
print('{n} executors'.format(n=num_executors))
print('{n} tokens | {e} embeddings'.format(n=len(tokens), e=len(vocab_embeddings)))
end = time.time()
duration_secs = round(end - start, 2)
duration_mins = round(duration_secs / 60, 2)
print('similarity calculation processes: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))
print('tokens_similarity_loops')
print(tokens_similarity.info())
results_file = '{f}.pkl'.format(f=function.__name__)
tokens_similarity.to_pickle(results_file)
