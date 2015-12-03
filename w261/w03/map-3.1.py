#!/usr/bin/python
''' count some things
'''
from __future__ import print_function
import random
import sys
import time
random.seed()
for line in sys.stdin:
    # split line into tokens of items
    tokens = line.split()
    basketsize = len(tokens)
    # generate a basket key
    # this is probably overkill
    basketkey = ''.join([str(random.random()), str(time.time())])
    for token in tokens:
        print('\t'.join([token, str(basketsize), str(basketkey)]), file=sys.stdout)