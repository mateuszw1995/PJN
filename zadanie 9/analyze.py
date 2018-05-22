from gensim.models.word2vec import *

model = Word2Vec.load("model")
for phrase in [
    "sąd_najwyższy",
    "trybunał_konstytucyjny",
    "kodeks_cywilny",
    "kpk",
    "sąd_rejonowy",
    "szkoda",
    "wypadek",
    "kolizja",
    "szkoda_majątkowa",
    "nieszczęście",
    "rozwód"
]:
    print(phrase)
    print(model.wv.most_similar(phrase, topn=3))
    print()

def print_resultant(x, y, z):
    print("%s - %s + %s = " % (x, y, z))
    for result in model.wv.similar_by_vector(model.wv[x] - model.wv[y] + model.wv[z], topn=5):
        print(result)
    print()

print_resultant("sąd_najwyższy", "kpc", "konstytucja")
print_resultant("pasażer", "mężczyzna", "kobieta")
print_resultant("samochód", "droga", "rzeka")

import numpy as np
from sklearn.manifold import TSNE
from matplotlib import pyplot as plt
from gensim.models.phrases import Phrases, Phraser

labels = [
    "szkoda",
    "strata",
    "uszczerbek",
    "szkoda majątkowa",
    "krzywda",
    "niesprawiedliwość",
    "nieszczęście"
]

bigram = Phraser.load("bigram")
trigram = Phraser.load("trigram")

X = np.array([model.wv[trigram[bigram[w.lower().split()]]].reshape(300) for w in labels])

X_embedded = TSNE(n_components=2).fit_transform(X)

# plot the result
vis_x = X_embedded[:, 0]
vis_y = X_embedded[:, 1]

fig, ax = plt.subplots()
ax.scatter(vis_x, vis_y)

for i, txt in enumerate(labels):
    ax.annotate(txt, (vis_x[i], vis_y[i]))

plt.show()
