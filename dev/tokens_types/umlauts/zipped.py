import os
import io
from zipfile import ZipFile

l = [u"Bücher", u"Hefte", u"Mappen"]
print(l)
with io.open("testfile.txt", mode="a", encoding="UTF8") as fd:
    for line in l:
        fd.write(line + "\n")

with ZipFile('zipped_files.zip', mode='w') as zip: zip.write('input.txt')

