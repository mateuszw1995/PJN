import os
import json

class DataManager:
    JUDGMENT_DATE_KEY = "judgmentDate"
    COURT_TYPE_KEY = "courtType"

    def __init__(self, data_dir):
        self.data_dir = data_dir

    def get_judgment_year(self, json_content):
        return int(json_content[self.JUDGMENT_DATE_KEY][:4])

    def judgments_generator(self, year='all'):
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json') and filename.startswith('judgments'):
                with open(os.path.join(self.data_dir, filename), 'r', encoding="utf8") as content_file:
                    content = content_file.read()
                    parsed = json.loads(content)
                    for judgment in parsed["items"]:
                        if year != 'all' and year == self.get_judgment_year(judgment) or year == 'all':
                            try:
                                if(judgment[self.COURT_TYPE_KEY] in ["COMMON", "SUPREME"]):
                                    yield judgment
                            except:
                                print("not common or supreme: " + str(judgment["caseNumber"]))

data_manager = DataManager(r"C:\Users\Mateusz\Desktop\klasyfikacja")

import re
generator = data_manager.judgments_generator(year=2007)

def contain_digit(x):
    return re.search(r'\d', x) is not None

def is_top_20(word):
    tops = ['art','do','na','nie','przez','dnia','sd','si','jest','sdu','od','ust','za','ustawy','nr','oraz','kpc','to','poz','prawa']
    return word in tops

def create_bag_of_words(text):
    return [x.lower() for x in re.findall(r'\b\w\w+\b', text, re.UNICODE)
                       if not contain_digit(x) and not is_top_20(x)]

def remove_html(x):
    return re.sub("<[^>]*>", "", x)

def remove_linebreaks(x):
    return re.sub("-\n", "", x)

def extract_justification(content):
    text = remove_linebreaks(remove_html(content["textContent"]))
    justification_string = 'UZASADNIENIE'
    splitted = re.split(justification_string, text, flags=re.IGNORECASE, maxsplit=1)
    if len(splitted) > 1:
        return splitted[1]
    return False

import re

judgments_groups_regex = {
    r'A?C.*': ('sprawy cywilne', []),
    r'A?U.*': ('sprawy z zakresu ubezpieczenia społecznego', []),
    r'A?K.*': ('sprawy karne', []),
    r'G.*': ('sprawy gospodarcze', []),
    r'A?P.*': ('sprawy w zakresie prawa pracy', []),
    r'R.*': ('sprawy w zakresie prawa rodzinnego', []),
    r'W.*': ('sprawy o wykroczenia', []),
    r'Am.*': ('sprawy w zakresie prawa konkurencji', []),
}

def assign_to_group(content):
    for judg_regex in judgments_groups_regex.keys():
        if re.match(judg_regex, content['courtCases'][0]['caseNumber'].split()[1]):
            justification = extract_justification(content)
            if justification:
                judgments_groups_regex[judg_regex][1].append(create_bag_of_words(justification))
            return

c = 0
while True:
    try:
        content = generator.__next__()
        assign_to_group(content)
        c += 1
    except StopIteration:
        break

for judg_regex in judgments_groups_regex.keys():
    print("%s: %d" % (judgments_groups_regex[judg_regex][0], len(judgments_groups_regex[judg_regex][1])))
print("Total number of judgments: %d" % c)

import random

def split_dataset(data, test_ratio=0.25):
    random.shuffle(data)
    split_num = int(test_ratio * len(data))
    train_data = data[split_num:]
    test_data = data[:split_num]
    return train_data, test_data

import requests

def send_post_request(sample):
    text = ' '.join(sample)
    r = requests.post("http://localhost:9201/", data=text.encode('utf-8') )
    r.encoding = 'utf-8'
    return r.text

def process_post_response(text):
    flexed = []
    base = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if ':' in line:
            try:
                splitted = line.split(':', 1)[0].split()
                line_before = lines[index-1]
                base.append(splitted[0].lower())
                flexed.append(line_before.split()[0])
            except:
                print(line)
    return flexed, base

training_x = []
training_y = []
test_x = []
test_y = []
base_training_x= []
base_test_x = []
for key in (r'A?C.*', r'A?U.*', r'A?K.*', r'A?P.*'):
    data = judgments_groups_regex[key][1]
    train_data, test_data = split_dataset(data)
    for sample in train_data:
        flexed, base = process_post_response(send_post_request(sample))
        base_training_x.append(base)
        training_x.append(flexed)
        training_y.append(key)
    for sample in test_data:
        flexed, base = process_post_response(send_post_request(sample))
        base_test_x.append(base)
        test_x.append(flexed)
        test_y.append(key)

print(len(training_x))
print(len(training_y))
print(len(test_x))
print(len(test_y))
print(len(base_training_x))
print(len(base_test_x))

from sklearn.feature_extraction.text import TfidfVectorizer
def prepare_tfidf(training, test):
    vectorizer = TfidfVectorizer()
    training = vectorizer.fit_transform([' '.join(sample) for sample in training])
    test = vectorizer.transform([' '.join(sample) for sample in test])
    return training, test

transformed_training_x, transformed_test_x = prepare_tfidf(training_x, test_x)
transformed_base_training_x, transformed_base_test_x = prepare_tfidf(base_training_x, base_test_x)

print(transformed_training_x.shape)
print(transformed_base_training_x.shape)
print(transformed_test_x.shape)
print(transformed_base_test_x.shape)

from sklearn import svm
clf_base = svm.SVC(C=100, kernel='rbf', gamma=0.01)
clf_base.fit(transformed_base_training_x, training_y)

clf_flexed = svm.SVC(C=100, kernel='rbf', gamma=0.01)
clf_flexed.fit(transformed_training_x, training_y)

# multiclass classification
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support, confusion_matrix


def make_predition(clf, test_x, test_y, text=""):
    prediction_result = clf.predict(test_x)
    print(text)
    print("accuracy " + str(accuracy_score(test_y, prediction_result)))
    print("confusion matrix: \n" + str(confusion_matrix(test_y, prediction_result)))
    print(str(classification_report(test_y, prediction_result,
                                    target_names=[judgments_groups_regex[key][0] for key in clf.classes_])))
    print("micro-average: " + str(precision_recall_fscore_support(test_y, prediction_result, average='micro')[:-1]))
    print("macro-average: " + str(precision_recall_fscore_support(test_y, prediction_result, average='macro')[:-1]))


make_predition(clf_base, transformed_base_test_x, test_y, text="BASE")
make_predition(clf_flexed, transformed_test_x, test_y, text="\nFLEXED")


# binary class classification# binary
def make_prediction(clf, test_x, test_y, training_x, training_y, text=""):
    y_true = []
    y_pred = []

    macro_prec = 0
    macro_recall = 0
    macro_f1 = 0

    for key in (r'A?C.*', r'A?U.*', r'A?K.*', r'A?P.*'):
        training_y_for_bin = [label == key for label in training_y]
        test_y_for_bin = [label == key for label in test_y]

        clf.fit(training_x, training_y_for_bin)
        prediction_result = clf.predict(test_x)
        precision, recall, f1_score = precision_recall_fscore_support(test_y_for_bin, prediction_result,
                                                                      average='binary')[:-1]

        macro_prec += precision * 0.25
        macro_recall += recall * 0.25
        macro_f1 += f1_score * 0.25
        y_true.extend(test_y_for_bin)
        y_pred.extend(prediction_result)

        print("%s \t %s" % (text, judgments_groups_regex[key][0]))
        print("confusion matrix: \n" + str(confusion_matrix(test_y_for_bin, prediction_result)))
        print("precision: %f" % precision)
        print("recall: %f" % recall)
        print("f1 score: %f\n" % f1_score)

    print(
        "micro: precision %f  recall %f  score %f" % precision_recall_fscore_support(y_true, y_pred, average='binary')[
                                                     :-1])
    print("macro: precision %f  recall %f  score %f" % (macro_prec, macro_recall, macro_f1))


make_prediction(svm.SVC(C=100, kernel='rbf', gamma=0.01), transformed_base_test_x, test_y,
                transformed_base_training_x, training_y, text="BASE")
make_prediction(svm.SVC(C=100, kernel='rbf', gamma=0.01), transformed_test_x, test_y,
                transformed_training_x, training_y, text="\nFLEXED")

