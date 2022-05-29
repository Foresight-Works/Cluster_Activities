import re
punctuation_marks="=|-|\+|_|\.|:|\/|\*|\'|,|\?"
def normalize(text, punctuation_marks=punctuation_marks):
    '''
    Identify texts in tokens by the presence of symbols
    '''
    text = text.replace('&amp', '')
    tokens = text.split(' ')
    for token in tokens:
        # Entities and Numbers
        if re.findall('\d', token):
            if re.findall('[A-Za-z]', token):
                text = text.replace(token, '<name>')
            else:
                text = text.replace(token, '<number>')
        elif re.findall(punctuation_marks, token):
            text = text.replace(token, '<name>')
    text = text.replace('<name> <name>', '<name>').replace('<number> <number>', '<number>')
    return text

text = 'HP2 for Trainset #026 DM2'
print(normalize(text))