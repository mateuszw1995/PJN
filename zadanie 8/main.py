import json
import re
import codecs
from urllib2 import urlopen, Request
import time

user="mojadresemail"
lpmn="any2txt|wcrft2|liner2({\"model\":\"n82\"})"

url="http://ws.clarin-pl.eu/nlprest2/base"

def upload(file):
        with open (file, "rb") as myfile:
            doc=myfile.read()
            myfile.close()
        print("uploading")
        return urlopen(Request(url+'/upload/',doc,{'Content-Type': 'binary/octet-stream'})).read();

def process(data):
        doc=json.dumps(data).encode()
        taskid = urlopen(Request(url+'/startTask/',doc,{'Content-Type': 'application/json'})).read();
        time.sleep(0.2)

        request_url = url+'/getStatus/' + taskid.decode('utf-8')

        resp = urlopen(Request(request_url))
        data=json.load(resp)
        while data["status"] == "QUEUE" or data["status"] == "PROCESSING" :
            print(data["status"])
            time.sleep(2)
            resp = urlopen(Request(request_url))
            data=json.load(resp)
        if data["status"]=="ERROR":
            print("Error "+data["value"])
            return None
        return data["value"]

judgments = []

for index in range(145, 175):
    path = ('judgments-%s.json' % index)
    data = json.load(open(path))['items']
    data = [j for j in data if re.match(r'^2007-', j['judgmentDate'])]

for j in data:
    date = j['judgmentDate']
    text = j['textContent'].replace("-\n", "")
    text = re.sub(r'<[^>]*>', "", text)
    judgments.append((date, text))

judgments.sort()

all_texts = [text for date, text in judgments]

f = codecs.open('100judgments.txt', 'w', "utf-8")
f.write("\n".join(all_texts[:100]))
f.close()

fileid=upload('100judgments.txt')
fileid = fileid.decode('utf-8')
data={'lpmn':lpmn,'user':user,'file':fileid}
data=process(data)
print("processed")
data=data[0]["fileID"]
processed = urlopen(Request(url+'/download'+data)).read()
print("opened")

f = codecs.open('xml_data', 'w', "utf-8")
f.write(processed.decode('utf-8'))
f.close()

