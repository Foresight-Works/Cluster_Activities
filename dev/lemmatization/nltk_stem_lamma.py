from tokens_similarity import *
import nltk
#nltk.download('wordnet')
#nltk.download('punkt')
from nltk.tokenize import RegexpTokenizer
wnl = nltk.WordNetLemmatizer()
porter = nltk.PorterStemmer()
lancaster = nltk.LancasterStemmer()

pattern = '\(.+?\)|\w*\d{1,}\.*\d{1,}\w*|\w+'
punctuation = "-|=|\+|_|\.|:|\/|\*|\'|,|!|\?|`|\(|\)"
regex_tokenizer = RegexpTokenizer(pattern)
tokenized_names = []
for name in task_names:
    #tokens = regex_tokenizer.tokenize(name)
    tokens = nltk.word_tokenize(name)
    tokens = [t.lower() for t in tokens]
    # punctuation symbols
    symbol_removed = [re.sub(punctuation, '', t) if len(t) == 1 else t for t in tokens]
    symbol_removed = [t for t in symbol_removed if t]
    lemmatized = [wnl.lemmatize(t) for t in symbol_removed]
    lancaster_stemmed = [lancaster.stem(t) for t in symbol_removed]
    porter_stemmed = [lancaster.stem(t) for t in symbol_removed]

    print(30*'-')
    print('task name:        ', name)
    print('tokens:           ', tokens)
    print('symbol_removed:   ', symbol_removed)
    print('lemmatized:       ', lemmatized)
    print('lancaster_stemmed:', lancaster_stemmed)
    print('porter_stemmed:   ', porter_stemmed)

    tokenized_names.append(tokens)
