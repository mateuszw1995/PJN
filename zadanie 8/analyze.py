import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree
from textwrap import wrap
from collections import Counter

e = xml.etree.ElementTree.parse('xml_data').getroot()

small_counter = Counter()
big_counter = Counter()
phrase_counter = Counter()
common = {}

for chunk in e.findall('chunk'):
    for sentence in chunk.findall('sentence'):
        phrases = {}

    for token in sentence.findall('tok'):
        lex = token.find('lex')
        orth = token.find('orth')
        base = lex.find('base')

        for nam in token.findall('ann'):
            if int(nam.text):
                key = nam.text + "_" + nam.attrib['chan']
                phrases[key] = (phrases.get(key, "") + " " + base.text).strip()

            for p in phrases:
                splitted = p.split("_")

                big_class = "_".join(splitted[2:3])
                small_class = "_".join(splitted[2:])
                phrase = phrases[p]

                small_counter.update([small_class])
                big_counter.update([big_class])
                phrase_counter.update([phrase + " (" + small_class + ")"])

                c = common.get(big_class, Counter())
                c.update([phrase])
                common[big_class] = c

objects = list(small_counter.keys())
objects = ['\n'.join(wrap(l, 12)) for l in objects]
performance = list(small_counter.values())
performance, objects = zip(*sorted(zip(performance, objects)))
y_pos = np.arange(len(objects))

plt.bar(y_pos, performance, align='center', alpha=0.5)
plt.xticks(y_pos, objects, rotation='vertical')
plt.ylabel('Liczba wystapien')
plt.title("klasyfikacja drobnoziarnista")
plt.show()

objects = list(big_counter.keys())
objects = ['\n'.join(wrap(l, 12)) for l in objects]
performance = list(big_counter.values())
performance, objects = zip(*sorted(zip(performance, objects)))
y_pos = np.arange(len(objects))

plt.bar(y_pos, performance, align='center', alpha=0.5)
plt.xticks(y_pos, objects, rotation='vertical')
plt.ylabel('Liczba wystapien')
plt.title("klasyfikacja gruboziarnista")
plt.show()

print("100 najczestszych wyrazen:")
for v, c in phrase_counter.most_common(100):
    print(v + " = " + str(c))
print("\n\n\n")

print("10 najczestszych wyrazen, dla kazdej wysokopoziomowej klasy")
for c in common:
    print(c + ":")
    for v, c in common[c].most_common(10):
        print(v + " = " + str(c))
