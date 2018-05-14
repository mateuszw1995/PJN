from WNQuery import *
import networkx
import matplotlib.pyplot as plt
import math

def printSynset(wnid):
    print(wnquery.getSynset(wnid, 'n').toString())

def dfs(wnquery, wnid, pos, rel):
    res = []
    ids = wnquery.lookUpRelation(wnid, pos, rel)
    res.append(wnid)
    printSynset(wnid)
    for i in ids:
        graph.append((wnid, i))
        res.extend(dfs(wnquery, i, pos, rel))
    return res


warnings_file = open('warnings.txt', 'w')
wnquery = WNQuery("plwordnet-3.1-visdisc.xml")

print("Znajdź wszystkie znaczenia rzeczownika szkoda oraz wymień ich synonimy (jeśli posiadają).")
meanings = wnquery.lookUpLiteral('szkoda', 'n')
for meaning in meanings:
    print(meaning.toString())

print("Znajdź domknięcie przechodnie relacji hiperonimi dla pierwszego znaczenia wyrażenia wypadek drogowy i przedstaw je w postaci grafu skierowanego.")
meaning = wnquery.lookUpSense('wypadek drogowy', 1, 'n')
graph = []
dfs(wnquery, meaning.wnid, 'n', 'hypernym')

G = networkx.DiGraph()
G.add_edges_from(graph)
plt.figure(figsize=(12, 3))
networkx.draw_spring(G, with_labels=True)
plt.show()


print("Znajdź bezpośrednie hiponimy rzeczownika wypadek1.")
meaning = wnquery.lookUpSense('wypadek', 1, 'n')
relation = wnquery.lookUpRelation(meaning.wnid, meaning.pos, 'hyponym')
for meaning in relation:
    printSynset(meaning)

print("Znajdź hiponimy drugiego rzędu dla rzeczownika wypadek1.")
meaning = wnquery.lookUpSense('wypadek', 1, 'n')
relation = wnquery.lookUpRelation(meaning.wnid, meaning.pos, 'hyponym')
for meaning in relation:
    meaning2 = wnquery.getSynset(meaning, 'n')
    relation2 = wnquery.lookUpRelation(meaning2.wnid, meaning2.pos, 'hyponym')
    for rel in relation2:
        printSynset(rel)

print("Przedstaw w postaci grafu skierowanego (z etykietami dla krawędzi) relacje semantyczne pomiędzy następującymi grupami leksemów")

def compute_reations(literals):
    synsets=[]
    for literal, pos in literals.items():
        synsets.append(wnquery.lookUpSense(literal, pos, 'n'))
    synsets_ids = [synset.wnid for synset in synsets]
    G = networkx.DiGraph()
    for synset in synsets:
        for target_id, relation_type in synset.ilrs:
            if target_id in synsets_ids:
                G.add_edge('\n'.join(filter(lambda x: x in literals, [synonym.literal for synonym in synset.synonyms])),
                           '\n'.join(filter(lambda x: x in literals, [synonym.literal for synonym in wnquery.lookUpID(target_id, 'n').synonyms])),
                           rel=relation_type)
    plt.figure(figsize=(20, 20))
    pos = networkx.spring_layout(G)
    networkx.draw(G, pos, with_labels=True, arrows=False)
    networkx.draw_networkx_edge_labels(G, pos, label_pos=0.2)
    plt.show()


compute_reations({'szkoda': 1, 'strata': 1, 'uszczerbek': 1, 'szkoda majątkowa': 1, 'uszczerbek na zdrowiu': 1, 'krzywda': 1,
             'niesprawiedliwość': 1, 'nieszczęście': 2})
compute_reations({'wypadek': 1, 'wypadek komunikacyjny': 1, 'kolizja': 2, 'zderzenie': 2, 'kolizja drogowa': 1,
             'katastrofa budowlana': 1, 'wypadek drogowy': 1})

print("Znajdź wartość miary pokrewieństwa semantycznego Leacocka-Chodorowa pomiędzy następującymi parami leksemów:")

synsets = [(wnquery.lookUpSense('szkoda', 2, 'n'), wnquery.lookUpSense('wypadek', 1, 'n')),
           (wnquery.lookUpSense('kolizja', 2, 'n'), wnquery.lookUpSense('szkoda majątkowa', 1, 'n')),
           (wnquery.lookUpSense('nieszczęście', 2, 'n'), wnquery.lookUpSense('katastrofa budowlana', 1, 'n'))]
names = ['szkoda - wypadek', 'kolizja - szkoda majątkowa', 'nieszczęście - katastrofa budowlana']
i = 0
for synset_pair in synsets:
    paths = []
    first_to_top = wnquery.getReach(synset_pair[0].wnid, 'n', 'hypernym', True)
    second_to_top = wnquery.getReach(synset_pair[1].wnid, 'n', 'hypernym', True)
    for first_on_path in first_to_top:
        for second_on_path in second_to_top:
            if first_on_path[0] == second_on_path[0]:
                paths.append(first_on_path[1] + second_on_path[1] - 1)
    distance = min(paths)
    print(names[i] + " " + str(-math.log(distance / (2.0 * (max(wnquery.getMaxDepth(wnid, 'n', 'hypernym') for wnid in wnquery.m_ndat))))))
    i += 1
