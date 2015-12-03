#!/usr/bin/python
''' map function to generate 2-itemsets

    implements in-memory combiner to aggregate counts of each
    2-itemset to reduce output file size
'''
from __future__ import print_function
import sys
itemsets = {}
magic = '*'
for line in sys.stdin:
    # split line into tokens of items
    items = line.split()
    for i in range(0, len(items)):
        item1 = items[i]
        # create fake itemset to keep count of 1-itemset
        # for use in reduce task
        itemset = ' '.join([item1, magic])
        if itemset not in itemsets:
            itemsets[itemset] = 0
        itemsets[itemset] += 1
        # create all possible combinations of 2-itemsets
        # for this basket
        for j in range(i + 1, len(items)):
            item2 = items[j]
            itemset = ' '.join(sorted([item1, item2]))
            if itemset not in itemsets:
                itemsets[itemset] = 0
            itemsets[itemset] += 1
for itemset in itemsets:
    results = '\t'.join([itemset, str(itemsets[itemset])])
    print(results, file=sys.stdout)