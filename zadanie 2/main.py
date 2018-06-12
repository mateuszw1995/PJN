#-*- coding: utf-8 -*-
import json
import re
import requests
from elasticsearch_dsl import connections, Text, DocType, Date, Keyword, Index
from elasticsearch_dsl import Search
import matplotlib.pyplot as plt
ELASTIC_ADDRESS = "http://localhost:9200/"

connections.create_connection(hosts=['localhost'], timeout=20)
Index(name='judgments').delete()

put_body = {
  "settings": {
    "analysis": {
      "analyzer": {
        "my_morfologik": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "morfologik_stem"
          ]
        }
      }
    }
  },
  "mappings": {
    "doc": {
      "properties": {
        "text_field": {
          "type": "text",
          "analyzer": "my_morfologik"
        },
        "date_field": {
          "type": "date"
        },
        "signature": {
          "type": "keyword"
        },
        "judges": {
          "type": "keyword"
        }
      }
    }
  }
}

requests.put(ELASTIC_ADDRESS+"judgments", json=put_body)

class Judgment(DocType):
  text_field = Text()
  date_field = Date()
  signature = Keyword()
  judges = Keyword()

  class Meta:
    index = 'judgments'

for index in range(145, 175):
  path = ('judgments-%s.json' % index)
  data = json.load(open(path, encoding='utf-8'))['items']
  data = [j for j in data if re.match(r'^2007-', j['judgmentDate'])]

  for j in data:
      text = j["textContent"]
      date = j["judgmentDate"]
      signature = j["id"]
      judges = j["judges"]

      Judgment(text_field=text, date_field=date, signature=signature, judges=[judge['name'] for judge in judges]).save()

query = Search().query("match", text_field="szkodę")
query.execute()
print("Znajdź liczbę orzeczeń, w których występuje słowo szkoda: %d" % query.count())

query = Search().query("match_phrase", text_field="trwałemu uszczerbkowi na zdrowiu")
query.execute()
print("Znajdź liczbę orzeczeń, w których występuje fraza trwały uszczerbek na zdrowiu, dokładnie w tej kolejności ale w dowolnej formie fleksyjnej: %d" % query.count())

query = Search().query("span_near",
                       clauses=[
                           {"span_term":{"text_field":"trwały"}},
                           {"span_term":{"text_field":"uszczerbek"}},
                           {"span_term":{"text_field":"na"}},
                           {"span_term":{"text_field":"zdrowie"}}
                        ],
                       slop=2,
                       in_order= True)
query.execute()
print("Jak wyżej, ale z uwzględnieniem możliwości wystąpienia maksymalnie 2 dodatkowych słów pomiędzy dowolnymi elementami frazy: %d" % query.count())

query = Search()
query.aggs.bucket('best', 'terms', field='judges', size=3, shard_size=100)

for judge in query.execute().aggregations.best:
    print(judge)

query = Search()
query.aggs.bucket('judgments', 'date_histogram', field='date_field', interval='month')

buckets = [bucket.doc_count for bucket in query.execute().aggregations.judgments['buckets']]
#print(buckets)

plt.bar([x for x in range(1, 13)], buckets)

plt.title('judgments / month')
plt.xlabel('month')
plt.ylabel('judgments monthly histogram')
plt.show()
