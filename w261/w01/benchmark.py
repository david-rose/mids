#!/Users/david/anaconda/bin/python
from __future__ import print_function
import re
import string
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
import sys
records = []
labels = []
# regular expression for removing punctuation
punctuation = re.compile('[%s]' % re.escape(string.punctuation))

# read the input data and create separate lists for content and classification
with open('enronemail_1h.txt', 'r') as cfile:
    for line in cfile:
        tokens = line.split('\t', 2)
        eid = tokens[0]
        label = tokens[1]
        # prepare text
        text = tokens[len(tokens) - 1].lower()
        text = punctuation.sub('', text)
        records.append(text) # content
        labels.append(label) # classification
# prepare the features, using the SciKit-Learn CountVectorizer
data = CountVectorizer().fit_transform(records)

# train and test using the Multinmial Naive Bayes implemenation
clf = MultinomialNB()
clf.fit(data, labels)
results = clf.predict(data)
# measure and report training error
incorrect = 0
for a,b in zip(labels, results):
    incorrect += not a == b
print('Multinomial NB Training Error: ', str(float(incorrect) / len(results)), file=sys.stderr)

# train and test using the Multinmial Naive Bayes implemenation
clf = BernoulliNB()
clf.fit(data, labels)
results = clf.predict(data)
# measure and report training error
incorrect = 0
for a,b in zip(labels, results):
    incorrect += not a == b
print('Bernoulli NB Training Error:   ', str(float(incorrect) / len(results)), file=sys.stderr)

