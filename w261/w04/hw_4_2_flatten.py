#!/usr/bin/python
''' 
'''
from __future__ import print_function
import csv
import sys
with open(sys.argv[1], 'rb') as fin, open(sys.argv[2], 'w') as fout:
    csvreader = csv.reader(fin, delimiter = ',', quotechar = '"')
    visitorid = ''
    for line in csvreader:
        if line[0] == 'C':
            visitorid = line[2]
            continue
        if line[0] == 'V':
            line.append(visitorid)
        print(','.join(line), file=fout)