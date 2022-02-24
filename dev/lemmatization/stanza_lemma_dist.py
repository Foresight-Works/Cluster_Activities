from tokens_similarity import *
import stanza

nlp = stanza.Pipeline(lang="en")


def lemmatize_text(text):
    '''
    :params:
    text: input text
    param1: stanza's language model
    :return: list of token-lemma tuple for each token in text
    '''

    text_tokens_lemmas = []
    doc = nlp(text)
    tokens_lemmas = [(word.text, word.lemma) \
                     for sent in doc.sentences for word in sent.words]
    for token_lemma in tokens_lemmas:
        token = token_lemma[0]
        lemma = token_lemma[1]
        #print('{t}:{l}'.format(t=token, l=lemma))
        if ('_' not in token) and (token != lemma) and (lemma != 'None'):
            text_tokens_lemmas.append(token_lemma)

    return text, text_tokens_lemmas


results_path = os.path.join(results_dir, 'lemmas.txt')
names_clusters = {}

num_executors = 6
if __name__ == '__main__':
    start = time.time()
    if num_executors <= 1:
        for task_name in task_names:

            print('Task analyzed:', task_name)
            task_name, text_tokens_lemmas = lemmatize_text(task_name)
            if text_tokens_lemmas:
                names_clusters[task_name] = text_tokens_lemmas
                #write_name_cluster(results_path, task_name, text_tokens_lemmas)

    else:
        executor = ProcessPoolExecutor(num_executors)
        for result in executor.map(lemmatize_text, task_names):
            task_name, text_tokens_lemmas = result
            print('Task analyzed:', task_name)
            names_clusters[task_name] = text_tokens_lemmas
            #write_name_cluster(results_path, task_name, text_tokens_lemmas)

    end = time.time()
    duration = end - start
    print('calculation duration:', duration)
