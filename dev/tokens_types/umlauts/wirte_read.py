# Source: https://stackoverflow.com/questions/41348343/python-write-umlauts-into-file

import io
l = [u"Bücher", u"Hefte", u"Mappen"]
print(l)
file_path = "testfile.txt"
with io.open(file_path, mode="a", encoding="UTF8") as fd:
    for line in l:
        fd.write(line + "\n")

lines = open(file_path).read().split('\n')
lines = [u"{l}".format(l=line) for l in lines]
with io.open("testfile1.txt", mode="a", encoding="UTF8") as fd:
    for line in l:
        fd.write(line + "\n")


