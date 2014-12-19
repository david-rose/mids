
# -*- coding: utf-8 -*-
"""

"""
import csv
from datetime import datetime as dt
import json
import re
import sys

class Extract(object):

    def go(self, fname, printHeaders):
        with open(fname, 'r') as f:
            csvout = csv.writer(sys.stdout, quoting=csv.QUOTE_NONNUMERIC,
                                dialect='excel-tab')
            if int(printHeaders) > 0:
                headers = ['hdid','yelpid','rating','review_count','name','categories',
                           'neighborhoods','postal_code','latitude','longitude',
                           'rev_rating','rev_time_created','rev_username',
                           'rev_excerpt']
                csvout.writerow(headers)
            for line in f:
                # ensure that this line contains valid data
                if re.match(r'^"\d+"\t{.+}$',line):
                    l = []
                    kv = line.split('\t', 1)
                    hdID = kv[0].replace('"', '')
                    l.append(hdID)
                    d = json.loads(kv[1])
                    token = self.getValue(d, 'id').encode('utf-8')
                    l.append(token)
                    token = self.getValue(d, 'rating')
                    l.append(token)
                    token = self.getValue(d, 'review_count')
                    l.append(token)
                    token = self.getValue(d, 'name').encode('utf-8')
                    l.append(token)
                    token = self.getValue(d, 'categories')
                    token = self.deListify(token, 1).encode('utf-8')
                    l.append(token)
                    token = self.getValue(d, ['location', 'neighborhoods'])
                    token = self.deListify(token, -1).encode('utf-8')
                    l.append(token)
                    token = self.getValue(d, ['location', 'postal_code'])
                    l.append(token)
                    token = self.getValue(d, ['location', 'coordinate', 'latitude'])
                    l.append(token)
                    token = self.getValue(d, ['location', 'coordinate', 'longitude'])
                    l.append(token)
                    token = self.getValue(d, ['reviews', 'rating'])
                    l.append(token)
                    token = self.getValue(d, ['reviews', 'time_created'])
                    token = dt.fromtimestamp(int(token)).strftime('%m/%d/%Y')
                    l.append(token)
                    token = self.getValue(d, ['reviews', 'user', 'name']).encode('utf-8')
                    l.append(token)
                    token = self.getValue(d, ['reviews', 'excerpt']).encode('utf-8')
                    token = token.replace('\n', ' ')
                    l.append(token)
                    csvout.writerow(l)

    def getValue(self, d, keys):
        ''' get a value from a dictionary; if keys is a list recurse
            until the lowest level of the hierarchy is reached
        '''
        if isinstance(keys, str):
            return d[keys] if keys in d else ''
        else:
            k = keys.pop(0)
            if len(keys) == 0:
                return d[k] if k in d else ''
            else:
                if k in d:
                    if isinstance(d[k], dict):
                        return self.getValue(d[k], keys)
                    elif isinstance(d[k], list) and isinstance(d[k][0], dict):
                        return self.getValue(d[k][0], keys)
                    else:
                        return d[k]
                else:
                    return ''

    def deListify(self, theList, i):
        ''' create a comma-delimited string from a list '''
        if i == -1:
            newList = theList
        else:
            newList = []
            for item in theList:
                newList.append(item[i])
        return ','.join(newList)


if __name__ == '__main__':
    Extract.go(Extract(), sys.argv[1], sys.argv[2])

