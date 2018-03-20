#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
#145 - 174
import string
import matplotlib.pyplot as plt
import operator

licznik = 0
tab = []
ustawa445 = 0
szkody = 0
dane = []

file = open('polimorfologik-2.1.txt')
try:
    slownik_txt = file.read()
finally:
    file.close()

slownik= set()
sl = slownik_txt.split("\n")
for a in sl:
    splt = a.split(";")
    slownik.add(splt[0].lower())
    slownik.add(splt[1].lower())
dict = {}
for x in range(145, 175):
    print x
    file = open('judgments-' + str(x) + '.json')
    try:
        text = file.read()
    finally:
        file.close()
    textContents = re.findall(r'\"textContent\":\".*?\",\"legalBases\":.*?\"judgmentDate\":\"\d\d\d\d', text)
    for textContent in textContents:
        if textContent[-4:] == "2007":
            txt = re.search(r'.*?\"legalBases\"', textContent)
            if txt:
                a = str(txt.group())[15:-14]
                string.replace(a, "-\\n", "")
                words = a.split()

                temp=[]
                for word in words:
                    temp+=word.split("\\n")
                words = temp[:]
                for i in range(len(words)):
                    words[i] = re.sub(r'\W', "", words[i])
                words = filter(lambda word: len(word) > 1 and not re.search(r'\d', word), words)
                licznik += len(words)
                i = 0
                for word in words:
                    word = word.lower()
                    if word in dict:
                        dict[word] = dict[word] + 1
                    else:
                        dict[word] = 1
print(licznik)
sorted_x = sorted(dict.items(), key=operator.itemgetter(1), reverse=True)

nie=[]
for x in sorted_x:
    #print(x[0]+": "+str(x[1]))
    dane.append(x[1])
    if x[0] not in slownik:
        nie.append(x[0])

print(len(nie))
plt.plot(dane)
plt.title("Lista frekwencyjna")
plt.xlabel("Pozycja na liscie frekwencyjnej")
plt.ylabel("Liczba wystapien")
plt.yscale('log',basey=10)
plt.show()

from collections import Counter

wrd=[]
for x in dict:
    wrd.append(x[0])
WORDS = Counter(wrd)

def P(word, N=sum(WORDS.values())):
    "Probability of `word`."
    return WORDS[word] / N

def correction(word):
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)

def candidates(word):
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words):
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in slownik)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

for i in range(30):
    print(nie[i] + " -> " + correction(nie[i]))