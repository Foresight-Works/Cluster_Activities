# Source: https://stackoverflow.com/questions/41348343/python-write-umlauts-into-file

import io
l = ["Bücher", "Hefte", "Mappen"]
lu = [u"Bücher", u"Hefte", u"Mappen"]
for index, i in enumerate(l):
    print(i, i.encode("macroman"), lu[index], lu[index].encode("macroman"))
    if '\\x9' in str(i.encode("macroman")):
        print(i)
