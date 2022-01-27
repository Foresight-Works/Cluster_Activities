import os
import re
from gensim import corpora
from gensim.models import LsiModel
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from gensim.models.coherencemodel import CoherenceModel


def tokenize_name(name):
    punctuation_marks = "=|\+|_|\.|:|\/|\*|\'|,|\?|\(|\)|\[|\]|-"

    tokens = []
    tokens = nltk.word_tokenize(name)
    tokens = list(set(tokens))
    # print('{} tokens'.format(len(tokens)))

    # Split by punctuation: backslah and hyphen
    split_backslash, split_hyphen = [], []
    for t in tokens:
        ts = t.split('/')
        split_backslash += ts
    for t in split_backslash:
        ts = t.split('-')
        split_hyphen += ts
    tokens = [re.sub(punctuation_marks, '', t) for t in tokens]
    tokens = [t for t in split_hyphen if len(t) > 1]

    return tokens


def preprocess_data(doc_set):
    """
    Preprocess (tokenize, removing stopwords, and stem) a list of documents
    Input  : Docuemnts list
    Output : Preprocessed texts
    """
    punctuation_marks = "=|\+|_|\.|:|\/|\*|\'|,|\?|\(|\)|\[|\]|-"

    # initialize regex tokenizer
    tokenizer = RegexpTokenizer(r'\w+')
    # create English stop words list
    en_stop = set(stopwords.words('english'))
    # Create p_stemmer of class PorterStemmer
    p_stemmer = PorterStemmer()
    # pre-processed documents
    texts = []
    # loop through document list
    for i in doc_set:
        # clean and tokenize document string
        raw = i.lower()
        tokens = tokenizer.tokenize(raw)
        tokens = [re.sub(punctuation_marks, '', t) for t in tokens]
        tokens = [t for t in split_hyphen if len(t) > 1]

        # remove stop words from tokens
        stopped_tokens = [i for i in tokens if not i in en_stop]
        # stem tokens
        stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
        # add tokens to list
        texts.append(stemmed_tokens)
    return texts


def prepare_corpus(doc_clean):

    """
    1. Build term dictionary of corpus tokens ({unique term: index}
    2. Converting list of documents (corpus) into Document Term Matrix
    corpus = list of documents

    Input  : clean document
    Output : term dictionary and Document Term Matrix
    """
    # Term dictionary: dictionary
    dictionary = corpora.Dictionary(doc_clean)
    # Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]
    # generate LDA model
    return dictionary,doc_term_matrix

def create_gensim_lsa_model(doc_clean,number_of_topics,words):

    """
    Build LSA model
    Input  : clean document, number of topics and number of words associated with each topic
    Output : return LSA model
    """
    dictionary, doc_term_matrix = prepare_corpus(doc_clean)
    # generate LSA model
    lsamodel = LsiModel(doc_term_matrix, num_topics=number_of_topics, id2word = dictionary)  # train model
    print(lsamodel.print_topics(num_topics=number_of_topics, num_words=words))
    return lsamodel


def compute_coherence_values(dictionary, doc_term_matrix, doc_clean, stop, start=2, step=3):
    """
    Compute c_v coherence for various number of topics to identify the optimum number of topics
    Input   : dictionary : Gensim dictionary
              corpus : Gensim corpus
              texts : List of input texts
              stop : Max num of topics
    Output  : model_list : List of LSA topic models
              coherence_values : Coherence values corresponding to the LDA model with respective number of topics
    """
    coherence_values = []
    model_list = []
    for num_topics in range(start, stop, step):
        # generate LSA model
        model = LsiModel(doc_term_matrix, num_topics=number_of_topics, id2word = dictionary)  # train model
        model_list.append(model)
        coherencemodel = CoherenceModel(model=model, texts=doc_clean, dictionary=dictionary, coherence='c_v')
        coherence_values.append(coherencemodel.get_coherence())
    return model_list, coherence_values


results_dir = '/results'
unique_names = open(os.path.join(results_dir, 'names.txt')).read().split('\n')


number_of_topics = 7
words = 10
clean_text = preprocess_data(unique_names)
model = create_gensim_lsa_model(clean_text,number_of_topics,words)