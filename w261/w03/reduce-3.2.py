#!/usr/bin/python
''' reducer reads stream consisting of [2-itemset, count] pairs

    utilizes order inversion pattern to enable efficient
    stream processing
    
'''
from __future__ import print_function
import sys
# value for identifying left hand side of rule
magic = '*'
minsupport = 100
lhscurrent = ''
rhscurrent = ''
lhscount = 0
itemsetcount = 0
# loop through input
# when key changes, take action depending on which
# component of the key changes
for line in sys.stdin:
    tokens = line.split('\t')
    itemset = tokens[0]
    lhs = itemset.split()[0]
    rhs = itemset.split()[1]
    count = int(tokens[1])

    if not rhs == rhscurrent:
        if itemsetcount > minsupport and not rhscurrent == magic:
            # calculate the confidence for the current itemset
            confidence = itemsetcount / float(lhscount)
            print('{} -> {}\t{:0.8f}'
                  .format(lhscurrent, rhscurrent, confidence),
                 file=sys.stdout)
        # reset loop values for right hand side
        itemsetcount = 0
        rhscurrent = rhs
    if not lhs == lhscurrent:
        # initialize the new lhs
        # reset loop values for left hand side
        lhscount = 0
        lhscurrent = lhs
    if rhs == magic:
        # increment support count for left hand side
        lhscount += count
    else:
        # increment support count for itemset
        itemsetcount += count
# process the last line
if itemsetcount > minsupport and not rhscurrent == magic and lhscount > 0:
    # calculate the confidence for the current itemset
    confidence = itemsetcount / float(lhscount)
    print('{} -> {}\t{:0.8f}'.format(lhscurrent, rhscurrent, confidence),
         file=sys.stdout)
