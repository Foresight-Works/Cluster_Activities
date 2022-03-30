import pandas as pd
import stanza
import time
from concurrent.futures import ProcessPoolExecutor

exclude = ['ba5 & ba8 - shaft f (type ii) amendment - delink effluent pit {4b1-4} [approved]',\
           'ba5 & ba8 - bd amendment (type ii) - shaft a location shift {4b4-1}',\
           'installation bypass-station man (incl. valves and pipes) "umleitdampfeinf�hrung"']
names = open('../results/cluster_key.txt').read().split('\n')
checked = 0

# cluster_key = cluster_key[checked:]
names = names[:100]
print('{n} unique task cluster_key'.format(n=len(names)))

nlp = stanza.Pipeline(lang="en")

names_errors = {}
start = time.time()
def lemmatize_text(text):
    '''
    :params:
    text: input text
    param1: stanza's language model
    :return: list of token-lemma tuple for each token in text
    '''

    text_tokens_lemmas = []
    doc = nlp(text)
    try:
        tokens_lemmas = [(word.text, word.lemma) \
                         for sent in doc.sentences for word in sent.words]
    except KeyError as e:
        names_errors[name] = str(e)

    for token_lemma in tokens_lemmas:
        token = token_lemma[0]
        lemma = token_lemma[1]
        #print('{t}:{l}'.format(t=token, l=lemma))
        if (len(token) > 1) & ('_' not in token) & (token != lemma) & (lemma != 'None'):
            text_tokens_lemmas.append(token_lemma)
    #print(text, text_tokens_lemmas)

    return text, text_tokens_lemmas


results_path = './results/lemmas.txt'
names_clusters = {}
text_tokens_lemmas = []
tokens_lemmas = {}
num_executors = 6
if __name__ == '__main__':
    start = time.time()
    if num_executors <= 1:
        for index, name in enumerate(names):
            #print('Task {i}: {t}'.format(i=checked + index, t=name))
            #if name == exclude[0]:
                # Ignore KeyError: "Constituency parser not trained with tag 'GW'"
            name, text_tokens_lemmas = lemmatize_text(name)
            if text_tokens_lemmas:
                names_clusters[name] = text_tokens_lemmas

    else:
        executor = ProcessPoolExecutor(num_executors)
        for result in executor.map(lemmatize_text, names):
            name, text_tokens_lemmas = result
            #print('Task analyzed:', name)
            names_clusters[name] = text_tokens_lemmas
            #write_name_cluster(results_path, name, text_tokens_lemmas)

    end = time.time()
    duration_secs = round(end - start, 2)
    duration_mins = round(duration_secs / 60, 2)
    print('run processes: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))
    print('Lemmatization encountered {n} errors'.format(n=len(names_errors)))
    for k, v in names_errors.items(): print(k, v)