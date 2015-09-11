#!/usr/bin/python
''' reducer is provided a list of temporary files containing mapper results

    reducer reads each file and aggregates counts of words and email classifications

    reducer then applies a Naive Bayes classifier against the same data set as used
    to buld the training parameters, classifying emal records and comparing the
    results to known classsifications.
'''
from __future__ import print_function
import math
import re
import string
import sys
# store statistics on the original list of words of interest
keywords = {}
# counts of each email classification
hamcount = 0
spamcount = 0
# counts of words in each email classification
spamwordcount = 0
hamwordcount = 0

filelist = sys.argv
while len(filelist) > 1:
    with open(filelist.pop(), 'r') as cfile:
        for line in cfile:
            tokens = line.split()
            word = tokens[0]
            # special case for count of email classification
            if word == '__CLASS__':
                hamcount += int(tokens[1])
                spamcount += int(tokens[2])
            # regular case of count of word
            else:
                if word not in keywords.keys():
                    keywords[word] = [0, 0]
                keywords[word][0] += int(tokens[1])
                keywords[word][1] += int(tokens[2])
                hamwordcount += int(tokens[1])
                spamwordcount += int(tokens[2])
# total number of unique words
vocabcount = len(keywords)
# total number of email records
doccount = spamcount + hamcount

# counters for determining error rate
correct = 0
incorrect = 0

# regular expression for removing punctuation
punctuation = re.compile('[%s]' % re.escape(string.punctuation))
with open('enronemail_1h.txt', 'r') as cfile:
    for line in cfile:
        # words to be used in Naive Bayes classification
        nbwords = {}
        tokens = line.split('\t', 2)
        eid = tokens[0]
        isspam = tokens[1]
        # build bag of words for email record
        text = tokens[len(tokens) - 1].lower()
        text = punctuation.sub('', text)
        docwords = re.findall(r"\w+", text)
        for word in docwords:
            if word in keywords.keys():
                if word not in nbwords:
                    nbwords[word] = 1
                else:
                    nbwords[word] += 1

        # calculate the probability of the email record being spam or ham
        # natural log conversion is used to avoid floating point underflow

        # start with the prior probability of a spam record
        logpspam = math.log(spamcount / float(doccount))
        for word in nbwords:
            # add the probability of the word being present in this classification
            # multiplied by the number of times the word appears in the record
            logpspam += (nbwords[word] * 
                (math.log(keywords[word][1] + 1 / float(spamwordcount + vocabcount))))

        # start with the prior probability of a ham record
        logpham = math.log(hamcount / float(doccount))
        for word in nbwords:
            # add the probability of the word being present in this classification
            # multiplied by the number of times the word appears in the record
            logpham += (nbwords[word] * (math.log(keywords[word][0] + 1 / float(hamwordcount + vocabcount))))

        # determine the classification, based on comparison of log probabilities
        nbclass = '0' 
        if logpspam > logpham:
            nbclass = '1'

        # add some statistics
        if isspam == nbclass:
            correct += 1
        else:
            incorrect += 1

        # emit the results
        #print('\t'.join([eid, isspam, nbclass, str(isspam == nbclass)]), file=sys.stderr)
        print('\t'.join([eid, isspam, nbclass]))
# print some statistics
print('correct: {}, incorrect: {}, training error: {}'.format(correct, incorrect,
    str(float(incorrect) / (correct + incorrect))), file=sys.stderr)

    