from setup import *
import cProfile
pr = cProfile.Profile()
pr.enable()

start = time.time()
checked = []
print('results_dir:', results_dir)
num_executors = 8
matrices_dir = os.path.join(results_dir, 'distance_matrices')

similarity_functions = [lcs_similarity, embedding_similarity]
tokens = open(os.path.join(results_dir, 'tokens.txt')).read().split('\n')
print('{n} tokens'.format(n=len(tokens)))
print('{n} executors'.format(n=num_executors))
print('tokens and embeddings')

pr.enable()
model_name = config.get('language_models', 'tokens')
tokens_embeddings = api.load("{m}".format(m=model_name))
vocab_embeddings, not_in_vocabulary = filter_embeddings(tokens, tokens_embeddings)
np.save(os.path.join(results_dir, 'vocab_embeddings.npy'), vocab_embeddings)
print('{n} tokens | {e} embeddings'.format(n=len(tokens), e=len(vocab_embeddings)))

for function in similarity_functions:
    print('metric:', function)
    print('similarity calculation')
    tokens_similarity = run_similarity(tokens, num_executors, function)
    end = time.time()
    duration_secs = round(end - start, 2)
    duration_mins = round(duration_secs / 60, 2)
    print('similarity calculation processes: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))
    tokens_similarity = tokens_similarity.fillna(0)
    print('tokens_similarity_loops')
    print(tokens_similarity.info())
    df_info(tokens_similarity).to_excel('{f}_info.xlsx'.format(f=function.__name__))
    results_file = os.path.join(matrices_dir, '{f}.pkl'.format(f=function.__name__))
    tokens_similarity.to_pickle(results_file)

pr.disable()
pr.print_stats(sort='time')