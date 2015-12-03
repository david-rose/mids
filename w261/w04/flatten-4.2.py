#!/usr/bin/python
''' 
'''
from __future__ import print_function
import csv
import re
import string
import sys
infile = sys.argv[1]
outfile = sys.argv[2]
with open(infile, 'rb') as fin, open(outfile, 'w') as fout:
    csvreader = csv.reader(fin, delimiter = ',', quotechar = '"')
    visitorid = ''
    for line in csvreader:
        linetype = line[0]
        if linetype == 'C':
            visitorid = line[2]
            continue
        if linetype == 'V':
            line.append(visitorid)
        print(','.join(line), file=fout)

        

        

        