import stanza
import time
import pandas as pd
import numpy as np
import os
nlp = stanza.Pipeline(lang="en", use_gpu= True)
results_dir = 'C:\\Users\\RonyArmon\\Projects_Code\\Cluster_Activities\\results'
names = open(os.path.join(results_dir, 'names.txt')).read().split('\n')
print('{n} unique task names'.format(n=len(names)))

import ast
start = time.time()
cols = ['id', 'text', 'lemma', 'upos', 'xpos', 'head', 'deprel', 'start_char', 'end_char', 'feats']
char_cols = ['start_char', 'end_char']
names_df = pd.DataFrame()
names_errors = {}
for index, name in enumerate(names):
    if index/100 == int(index/100): print('name', index)
    #print(80*'-')
    #print('name {}:'.format(index+1), name)
    try:
        doc = nlp(name)
        doc_sentences = doc.sentences
        results = []
        name_df = pd.DataFrame(columns=cols)
        for sent in doc.sentences:
            for word in sent.words:
                word_dict = ast.literal_eval(str(word))
                if 'feats' not in word_dict.keys():
                    word_dict['feats'] = '_'
                vals = list(word_dict.values())
                cols = list(word_dict.keys())
                word_df = pd.DataFrame([vals], columns = cols)
                name_df = name_df.append(word_df)
        name_df = name_df.rename(columns={'text': 'token', 'id': 'loc'})
        name_df['name_id'] = index+1
        names_df = names_df.append(name_df)
        names_df['token_id'] = np.arange(1, len(names_df)+1)
        names_df = names_df[['token_id', 'name_id', 'loc', 'token', 'lemma', 'upos',\
                             'xpos', 'head', 'deprel', 'start_char', 'end_char', 'feats']]
        #names_df.to_pickle('./results/pos.pkl')  # , index=False)
    except KeyError as e:
        names_errors[name] = str(e)
end = time.time()
duration_secs = round(end - start, 2)
duration_mins = round(duration_secs / 60, 2)
print('run duration: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))
print('POS encountered {n} errors'.format(n=len(names_errors)))
for k, v in names_errors.items(): print(k, v)