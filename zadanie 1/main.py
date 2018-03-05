#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
#145 - 174
import string
import matplotlib.pyplot as plt

licznik = 0
tab = []
ustawa445 = 0
szkody = 0

for x in range(1, 3173):
    print x
    file = open('judgments-' + str(x) + '.json')
    try:
        text = file.read()
    finally:
        file.close()

    textContents = re.findall(r'\"textContent\":\".*?\",\"legalBases\":.*?\"judgmentDate\":\"\d\d\d\d', text)

    for textContent in textContents:
        if textContent[-4:] == "2007":
            while 1:
                zl = re.search(r'\d(\d+|\.|,| )* zł', textContent)
                if zl:
                    a = str(zl.group())[:-4]
                    a = string.translate(a, None, ' .')
                    coma = re.findall(r',', a)
                    if len(coma) > 1:
                        a = string.translate(a, None, ',')
                    else:
                        a = string.replace(a, ',', '.')
                    tab.append(float(a))
                    textContent = textContent[zl.end():]
                    licznik += 1
                else:
                    break
            referencedRegulations = re.search(r'\"referencedRegulations\":\[.*?\"text\":\"Ustawa z dnia 23 kwietnia 1964 r\. - Kodeks cywilny.*?}', textContent)
            if referencedRegulations:
                kodeks = re.search(
                    r'\"text\":\"Ustawa z dnia 23 kwietnia 1964 r\. - Kodeks cywilny.*?art\. 445.*?}',
                    referencedRegulations.group())
                if kodeks:
                    ustawa445 += 1
            content = re.search(r'.*?\",\"legalBases\":', textContent)
            if content:
                szkoda = re.findall(r'\b(szkoda|szkody|szkodzie|szkodę|szkodą|szkodo|szkód|szkodom|szkodami|szkodach)\b', content.group())
                if len(szkoda) > 0:
                    szkody += 1
#print licznik
print "Liczba orzeczeń odwołujących się w 2007 roku do artykułu 445: " + str(ustawa445)
print "Liczba orzeczeń w 2007 roku, które zawierają słowo szkoda w dowolnej formie fleksyjnej: " + str(szkody)

tabs = []
tabb = []
for x in tab:
    if x < 1000000:
        tabs.append(x)
    else:
        tabb.append(x)
plt.hist(tab, 50)
plt.title("Wszystkie wartosci pieniezne")
plt.xlabel("Kwota")
plt.ylabel("Czestotliwosc")
plt.show()

plt.hist(tabs, 50)
plt.title("Wartosci pieniezne < 1 mln")
plt.xlabel("Kwota")
plt.ylabel("Czestotliwosc")
plt.show()

plt.hist(tabb, 50)
plt.title("Wartosci pieniezne > 1 mln")
plt.xlabel("Kwota")
plt.ylabel("Czestotliwosc")
plt.show()
