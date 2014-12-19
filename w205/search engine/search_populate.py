#! /usr/bin/python
# -*- coding: utf-8 -*-
"""



"""

import pymongo
import re
import simplejson

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["ysearch"]

def insertTerm(fname):
    try:
        db.drop_collection('term')
    except:
        pass
    cTerm = db["term"]
    with open(fname, 'r') as f:
        i = 0
        for line in f:
            tokens = line.split('\t')
            if len(tokens[0]) < 1024 and len(tokens[1]) < 16777216:
                # mongodb can't index keys longer than 1024 byes
                d = {}
                d['term'] = tokens[0]
                d['posting'] = simplejson.loads(tokens[1])
                try:
                    cTerm.insert(d)
                    i += 1
                    if i % 1000 == 0:
                        print i,' ',
                except Exception as e:
                    print '\n',tokens[0],'\n',repr(e)

    cTerm.create_index([('term',pymongo.ASCENDING)])

def insertReview(fname):
    try:
        db.drop_collection('review')
    except:
        pass
    cReview = db['review']
    with open(fname, 'r') as f:
        i = 0;
        for line in f:
            tokens = line.split('\t')
            d = simplejson.loads(tokens[1])
            '''
            businessID
            reviewID
            reviewDate
            reviewText
            reviewRating
            '''
            try:
                cReview.insert(d)
                i += 1
                if i % 1000 == 0:
                    print i,' ',
            except Exception as e:
                print '\n',d,'\n',repr(e)

    cReview.create_index([('reviewID',pymongo.ASCENDING)])

def insertBusiness(fname):
    try:
        db.drop_collection('business')
    except:
        pass
    cBusiness = db['business']
    with open(fname, 'r') as f:
        i = 0
        for line in f:
            # ensure that this line contains valid data
            if re.match(r'^"\d+"\t{.+}$',line):
                r = {}
                tokens = line.split('\t', 1)
                hdID = tokens[0].replace('"', '')
                r['hdID'] = hdID
                d = simplejson.loads(tokens[1])
                v = getValue(d, 'id').encode('utf-8')
                r['yelpID'] = v
                v = getValue(d, 'rating')
                r['rating'] = v
                v = getValue(d, 'review_count')
                r['review_count'] = v
                v = getValue(d, 'name').encode('utf-8')
                r['name'] = v
                v = getValue(d, 'categories')
                v = deListify(v, 1).encode('utf-8')
                r['categories'] = v
                v = getValue(d, ['location', 'neighborhoods'])
                v = deListify(v, -1).encode('utf-8')
                r['neighborhoods'] = v
                v = getValue(d, ['location', 'postal_code'])
                r['postal_code'] = v
                v = getValue(d, ['location', 'coordinate', 'latitude'])
                r['latitude'] = v
                v = getValue(d, ['location', 'coordinate', 'longitude'])
                r['longitude'] = v
                try:
                    cBusiness.insert(r)
                    i += 1
                    if i % 1000 == 0:
                        print i,' ',
                except Exception as e:
                    print '\n',r,'\n',repr(e)

    cBusiness.create_index([('yelpID',pymongo.ASCENDING)])

def getValue(d, keys):
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
                    return getValue(d[k], keys)
                elif isinstance(d[k], list) and isinstance(d[k][0], dict):
                    return getValue(d[k][0], keys)
                else:
                    return d[k]
            else:
                return ''

def deListify(theList, i):
    ''' create a comma-delimited string from a list '''
    if i == -1:
        newList = theList
    else:
        newList = []
        for item in theList:
            newList.append(item[i])
    return ','.join(newList)

def insertInspection(fname):
    try:
        db.drop_collection('inspection')
    except:
        pass
    cInspection = db['inspection']
    with open(fname, 'r') as f:
        i = 0
        for line in f:
            # ensure that this line contains valid data
            if re.match(r'^\d+,',line):
                d = {}
                tokens = line.split(',')
                hdID = tokens[0]
                score = tokens[1]
                t = tokens[2].replace('"','')
                date = '{0}/{1}/{2}'.format(t[4:6],t[-2:],t[:4])
                itype = tokens[3].replace('"','')
                itype = itype.replace('\r\n','')
                d['hdID'] = hdID
                d['score'] = score
                d['date'] = date
                d['type'] = itype
                try:
                    cInspection.insert(d)
                    i += 1
                    if i % 1000 == 0:
                        print i,' ',
                except Exception as e:
                    print '\n',d,'\n',repr(e)

    cInspection.create_index([('hdID',pymongo.ASCENDING)])




insertTerm('sf_inverted_index.txt')
insertReview('sf_review_all.txt')
insertBusiness('sf_business_all.txt')
insertInspection('../sf/inspections_plus.csv')
