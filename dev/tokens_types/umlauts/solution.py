# Source: https://stackoverflow.com/questions/41348343/python-write-umlauts-into-file

import io
l = [u"Bücher", u"Hefte", u"Mappen"]
print(l)
with io.open("testfile.txt", mode="a", encoding="UTF8") as fd:
    for line in l:
        fd.write(line + "\n")
