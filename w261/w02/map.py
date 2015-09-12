#!/usr/bin/python
''' mapper reads from stdin, emits counts of words, and 
    counts of email classifications
'''
from __future__ import print_function
import re
import string
import sys

# regular expression to remove all punctuation
punctuation = re.compile('[%s]' % re.escape(string.punctuation))

# words to be used in analysis
# normalize parameters same as input
findwords = punctuation.sub('', sys.argv[1]).lower().split()

for line in sys.stdin:
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
        if word in findwords or sys.argv[1] == '*':
            # emit the word and the classification count
            if isspam == '0': # ham
                print(word, 1, 0)
            else: # spam
                print(word, 0, 1)