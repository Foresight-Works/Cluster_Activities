from dev.pipeline.service.cluster_service5.setup import *
import stanza
import spacy

f = open('../../words_pairs/response/CCGT_878Clusters_validation_response.json', )
data = json.load(f)
names = []
for cluster, cluster_names in data.items(): names += cluster_names
names = list(set(names))
names = names[:10]
names = ["I'm drinking water now", "I drank water yesteday", "I drink a lot of beer"]
print('{n} unique task names'.format(n=len(names)))
exclude = ['ba5 & ba8 - shaft f (type ii) amendment - delink effluent pit {4b1-4} [approved]',\
           'ba5 & ba8 - bd amendment (type ii) - shaft a location shift {4b4-1}',\
           'installation bypass-station man (incl. valves and pipes) "umleitdampfeinf�hrung"']

nlp = stanza.Pipeline(lang="en")
spacy_nlp = spacy.load("en_core_web_lg")

names_errors = {}
start = time.time()
def lemmatize_text(text):
    '''
    :params:
    text: input text
    param1: stanza's language model
    :return: list of token-lemma tuple for each token in text
    '''
    print('text:', text)
    name_tokens_lemmas = {}
    try:
        doc = nlp(text)
        tokens_lemmas = [(word.text, word.lemma) \
                         for sent in doc.sentences for word in sent.words]
        print('tokens_lemmas:', tokens_lemmas)
        for token_lemma in tokens_lemmas:
            token = token_lemma[0]
            lemma = token_lemma[1]
            #print('{t}:{l}'.format(t=token, l=lemma))
            if (len(token) > 1) & ('_' not in token) & (token != lemma) & (lemma != 'None'):
                name_tokens_lemmas[token] = lemma
        print(name_tokens_lemmas)

    except KeyError as e:
        names_errors[name] = str(e)
        print(text, str(e))

    return name_tokens_lemmas



# print('Task {i}: {t}'.format(i=checked + index, t=name))
# if name == exclude[0]:
# Ignore KeyError: "Constituency parser not trained with tag 'GW'"
# print('Lemmatization encountered {n} errors'.format(n=len(names_errors)))
# for k, v in names_errors.items(): print(k, v)

names_tokens_lemmas_path = './names_tokens_lemmas/lemmas.txt'
names_clusters = {}
name_tokens_lemmas = []
tokens_lemmas = {}
num_executors = 1
if __name__ == '__main__':
    executor = ProcessPoolExecutor(num_executors)
    start = time.time()
    names_tokens_lemmas, tokens_lemmas = [], {}
    if num_executors <= 1:
        for name_tokens_lemmas in map(lemmatize_text, names): names_tokens_lemmas.append(name_tokens_lemmas)
    else:
        for result in executor.map(lemmatize_text, names): names_tokens_lemmas.append(name_tokens_lemmas)

    print('names_tokens_lemmas')
    print(names_tokens_lemmas)
    for name_tokens_lemmas in names_tokens_lemmas:
        tokens_lemmas.update(name_tokens_lemmas)

    np.save(os.path.join(results_dir, 'tokens_lemmas.npy'), tokens_lemmas)
    tokens_lemmas = np.load(os.path.join(results_dir, 'tokens_lemmas.npy'), allow_pickle=True)[()]
    print('tokens_lemmas')
    for name, lemma in tokens_lemmas.items(): print('{n}:{l}'.format(n=name, l=lemma))
    end = time.time()
    duration_secs = round(end - start, 2)
    duration_mins = round(duration_secs / 60, 2)
    print('run processes: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))
