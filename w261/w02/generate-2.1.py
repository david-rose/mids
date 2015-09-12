#!/usr/bin/python
''' generate a list of key-value pairs where the key is a random integer
    and the value is an empty string
'''
from __future__ import print_function
from random import randint
minrange = 10
maxrange = 99
randcount = 10000
with open('randomnumbers.txt', 'w') as fout:
    for i in range(0, randcount):
        print(' '.join([str(randint(minrange, maxrange)), '']), file=fout)