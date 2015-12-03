#!/usr/bin/python
''' reducer aggregates some statistics
'''
from __future__ import print_function
import sys
items = {}
baskets = {}
maxbasket = 0
for line in sys.stdin:
    tokens = line.split()
    item = tokens[0]
    basketsize = int(tokens[1])
    basketkey = tokens[2]
    items[item] = 1
    # store size of each individual basket
    baskets[basketkey] = basketsize
    # keep running maximum of basket size
    maxbasket = max(maxbasket, basketsize)
# calculate some statistics
# mean basket size
meanbasket = sum(baskets.values())/float(len(baskets))
# standard deviation of basket size
std = (sum([(x - meanbasket)**2 for x in baskets.values()]) 
       / float(len(baskets)))**0.5
# emit results
results = ('total baskets: {}, unique items: {}, largest basket size: {},\n'
           + 'mean basket size: {:0.2f}, std deviation: {:0.2f}') \
    .format(len(baskets), len(items), maxbasket, meanbasket, std)
print(results, file=sys.stdout)