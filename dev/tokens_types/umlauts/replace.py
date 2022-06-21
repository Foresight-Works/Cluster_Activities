# Source: https://stackoverflow.com/questions/41348343/python-write-umlauts-into-file

import io
texts = ['PAYM12020',\
    'Invoice Milestone 06 - Delivery of Train (�berstellung des Fzg.)',\
         'Payment Milestone 01 - Notice To Proceed (NTP, Vertragsbeginn)']

def decoded_string(text):
    encodings = ['utf-8-sig', 'latin-1', 'ISO-8859-1', 'Windows-1252', 'macroman']
    decoded, index = False, 0
    while decoded == False:
        encoding = encodings[index]
        print('encoding using', encoding)
        try:
            decoded_text = text.encode(encoding=encoding)
            #file_posted = zipped_object.read(file_name).decode(encoding=encoding)
            decoded = True
        except UnicodeEncodeError as e:
            print(e)
            index += 1

    return str(decoded_text)

for text in texts:
    print(30*'=')
    print(text)
    no_qmark = text.replace('�', '')
    print(no_qmark)
    decoded = decoded_string(text)
    print(decoded)
    symbol = 'xef'
    cleaned = decoded.replace(symbol, '')

    print(cleaned)
#print(a.encode())