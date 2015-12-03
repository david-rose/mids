''' preprocess the data set, normalizing the word counts
'''
from __future__ import print_function
import sys
with open(sys.argv[1], 'rb') as fin, open(sys.argv[2], 'w') as fout:
    for line in fin:
        row = map(int, line.split(','))
        userid = row[0]
        code = row[1]
        total = row[2]
        for j in range(2, len(row)):
            row[j] = float(row[j]) / total
        print('{}'.format(row[0]), file = fout, end = '')
        for j in range(1, 3):
            print(',{}'.format(row[j]), file = fout, end = '')
        for j in range(3, len(row)):
            print(',{:0.8f}'.format(row[j]), file = fout, end = '')
        print('', file = fout)