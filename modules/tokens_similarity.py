from setup import *
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
start = time.time()
tokens_file = 'tokens.txt'
checked = []
def calc_similarity(token1):
    '''
    Calculate token similarity for input token compared to all tokens
    from a list of tokens and cluster tokens that are more similar than the
    specified threshold.
    '''
    if tokens_file in os.listdir(results_dir):
        tokens = open(os.path.join(results_dir, tokens_file)).read().split('\n')
    else: tokens = []
    token_scores = []
    if token1 not in checked:
        checked.append(token1)
        for token2 in tokens:
            score = similar(token1, token2)
            token_scores.append((token1, token2, score))
    return token_scores

def run_similarity(tokens, num_executors):
    results_df = pd.DataFrame(columns=tokens, index=tokens)
    tokens_scores = []
    executor = ProcessPoolExecutor(num_executors)
    for result in executor.map(calc_similarity, tokens):
        tokens_scores += result
    executor.shutdown()

    for result in tokens_scores:
        token1, token2, similarity = result
        similarity = round(similarity, 2)
        results_df.at[token1, token2] = similarity

    end = time.time()
    duration_secs = round(end - start, 2)
    duration_mins = round(duration_secs / 60, 2)
    print('similarity calculation duration: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))
    # print('\nresults:')
    # print(results_df)
    # print(results_df.columns)

    return results_df
