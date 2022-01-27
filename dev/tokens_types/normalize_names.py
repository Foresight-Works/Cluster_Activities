#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import re
import os
import time
import nltk

#Data
data_results_path=re.sub('/modules/'+os.path.basename(os.getcwd()),'',os.getcwd()+'/data_results/')
print (data_results_path)

###Patterns and Dictionaries###
'''Patterns'''
e_mail_pattern='^[a-zA-Z0-9_\-\.]{2,}@[a-zA-Z0-9_\-\.]{2,}'
link_pattern='https?:\/\/[a-zA-Z0-9_\-\.\/\?]{2,}'
number_pattern='[0-9]+'
decimal_pattern='[0-9]{1,}\.[0-9]{1,}'
#Dates
date_pattern = '\d{1,2}[\.|\-|\/]\d{1,2}[\.|\-|\/]\d{2,4}'

#punctuation
punctuation_marks="=|\+|_|\.|:|\/|\*|\'|,|?"
punctuation_marks=['-','=','\+','_','\.',':','\/','\*']


def normalize_tokens(sentence):
    split_tokens_list=[]
    tokenized_sentence=nltk.word_tokenize(sentence)

    for index, token in enumerate (split_tokens_list):

        #Phone numbers
        if re.findall(phone_number_il, token):
            split_tokens_list[index]='<phone>'
            pass

        #Web Links
        if re.findall(e_mail_pattern,token):
            split_tokens_list[index]='<דוא"ל>'
            pass

        #Email Addresses
        if re.findall(link_pattern,token):
            split_tokens_list[index]='<קישור>'
            pass

        #Dates
        if re.findall(date_pattern,token):
            split_tokens_list[index]='<תאריך>'
            pass

        #Times
        for time_pattern in time_patterns:
            if re.findall(time_pattern,token):
                split_tokens_list[index]='<שעה>'
                pass

        #numbers
        for index, token in enumerate(split_tokens_list):
            if (re.findall(number_pattern, token)) or (re.findall(decimal_pattern, token)):
                split_tokens_list[index]='<מספר>'

    #punctuation
    for mark in punctuation_marks:
            split_tokens_list=[re.sub(mark,'',token) for token in split_tokens_list]
    split_tokens_list=[token for token in split_tokens_list if len (token)>1]

#     To clean sentences composed only of normalized terms:
#     normalized_terms=['<דוא"ל>','<קישור>','<תאריך>','<מספר>','<אנגלית>']
#     check=[token for token in split_tokens_list if token not in normalized_terms]
#     if not check:
#         split_tokens_list='all tokens cleaned'

    return(split_tokens_list)

# ################# Test #########################
# print ('Starting normalization')
# for index, sentence in enumerate (tokenized_sentences):
#     index+=1
#     result=normalize_tokens(sentence)
#     print ('sentence {c}: {s}\nresult: {r}\n'
#            .format(c=index,s=sentence,r=result))

################# Run #########################

def controller():
    count=0
    normalized_sentences=[]
    print ('Starting normalization')
    executor=ProcessPoolExecutor()
    for result in executor.map(normalize_tokens,tokenized_sentences):
        count+=1
        print ('sentence {c}. result: {r}\n'.format(c=count,r=result))

        with open ('normalization_results.txt','a') as f:
            f.write ("{ns}\n".format (ns=result))

        normalized_sentences.append(result)

    executor.shutdown()

    sentences_df['normalized_sentence']=normalized_sentences

if __name__=="__main__":
    controller ()
    sentences_df=sentences_df.loc[sentences_df['normalized_sentence']!='all tokens cleaned']

    new_sentences_index=[]
    discussion_indices=sentences_df['discussion_index'].unique()
    for discussion_index in discussion_indices:
        discussion_df=sentences_df.loc[sentences_df['discussion_index']==discussion_index]
        discussion_index_list=[discussion_index]*len (discussion_df)
        for sentence_number in range (0,len (discussion_df)):
            sentence_index='S{di}_{sn}'.format(di=discussion_index,sn=sentence_number)
            new_sentences_index.append(sentence_index)

    sentences_df['sentence_index']=new_sentences_index
    sentences_df.to_pickle('./results/normalized_sentences4_all.pkl')
