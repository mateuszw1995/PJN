#-*- coding: utf-8 -*-
import json
import re
from gensim.models.phrases import Phrases, Phraser
from gensim.models.word2vec import Word2Vec
from nltk import sent_tokenize
from gensim.models.word2vec import LineSentence

size = 0
sentences = []
pre = open('sentences.txt', 'w', encoding='utf-8')
for index in range(1, 600):
    path = ('judgments-%s.json' % index)
    data = json.load(open(path, encoding="utf8"))['items']

    for j in data:
        text = j['textContent'].replace("-\n", "").lower()
        text = re.sub(r'<[^>]*>', "", text)
        for sentence in sent_tokenize(text, language='polish'):
            pre.write(re.sub('\s+', ' ', sentence).strip() + "\n")
        size += len(text)
        if size >= 1000000000:
            break
    if size >= 1000000000:
        break
pre.close()
print(size)
sentences = LineSentence('sentences.txt')
bigram = Phraser(Phrases(sentences))
bigram.save("bigram")
print("1")
sentence_stream = [bigram[sentence] for sentence in sentences]
trigram = Phraser(Phrases(sentence_stream))
trigram.save("trigram")
print("2")
model = Word2Vec([trigram[bigram[sentence]] for sentence in sentence_stream],
                 window=5, size=300, sg=0, workers=12, min_count=3)
model.save("model")
print("processed")
