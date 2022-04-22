def uppercase_characters(token):
    uppercased = False
    c = 0
    for l in token:
        if l.isupper():
            c += 1
    if c == len(token): uppercased = True
    return uppercased

for i in ['jingOO', 'BANANA']:
    print(uppercase_characters(i))