#!/usr/bin/python
''' mapper reads name of file containing chunk of email records and a list of
    words of interest

    mapper emits counts of words, and counts of email classification
'''
from __future__ import print_function
import re
import string
import sys
filename = sys.argv[1]
findwords = sys.argv[2].split()
# regular expression to remove all punctuation
punctuation = re.compile('[%s]' % re.escape(string.punctuation))
with open (filename, "r") as myfile:
    for line in myfile:
        # split line into three tokens: id, classification, email contents
        # both the email subject and the email body are included in the analysis
        tokens = line.split('\t', 2)
        isspam = tokens[1]
        # emit count of email classification, using magic word '__CLASS__'
        if isspam == '0': # ham
            print('__CLASS__', 1, 0)
        else: # spam
            print('__CLASS__', 0, 1)
        # convert text to lower case
        text = tokens[len(tokens) - 1].lower()
        # remove punctuation from text
        text = punctuation.sub('', text)
        # split into individual words
        words = re.findall(r"[\w']+", text)
        for word in words:
            # only report on word if it is in the word list parameter
            # or report on all words if parameter equals '*'
            if word in findwords or sys.argv[2] == '*':
                # emit the word and the classification count
                if isspam == '0': # ham
                    print(word, 1, 0)
                else: # spam
                    print(word, 0, 1)