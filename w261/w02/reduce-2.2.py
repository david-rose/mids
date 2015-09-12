#!/usr/bin/python
'''
    reducer aggregates counts of words from stdin and emits those counts
'''
from __future__ import print_function
import sys
words = {}
for line in sys.stdin:
    tokens = line.split()
    word = tokens[0]
    if word not in words.keys():
        words[word] = 0
    # mapper produces counts based on email classification
    # this reducer is only interested in total counts
    words[word] += int(tokens[1]) + int(tokens[2])
# emit results
for word in sorted(words.keys()):
    # ignore counts for email classification
    if word != '__CLASS__':
        #print('\t'.join([word, str(words[word])]), file=sys.stderr)
        print('\t'.join([word, str(words[word])]))