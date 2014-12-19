#! /usr/bin/python
# -*- coding: utf-8 -*-
"""



"""
from nltk.stem.snowball import SnowballStemmer
import pymongo
import re
import sys

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['ysearch']
cTerm = db['term']
cReview = db['review']
cBusiness = db['business']
cInspection = db['inspection']
stemmer = SnowballStemmer("english", ignore_stopwords=True)
maxMatch = 100

def query(p):
    #convert search term to stemmed version
    term = re.sub(r'\W+$', '', p)
    term = stemmer.stem(re.sub(r'\W', '', term.lower()))

    # first, search for the term
    if cTerm.find({'term' : p}).count() == 1:
        match = cTerm.find({'term' : p}).next()
        matchCount = len(match['posting'])
        displayList = []
        i = 0
        for post in match['posting']:
            i += 1
            if i > maxMatch:
                break
            display = initDisplay()
            display['qterm'] = p
            docID = post[0]
            idx = post[1]
            display['idx'] = idx
            # second, search for the review
            if cReview.find({'reviewID' : docID}).count() == 1:
                r = cReview.find({'reviewID' : docID}).next()
                display['rdate'] = r['reviewDate']
                businessID = r['businessID']
                display['rtext'] = r['reviewText'].encode('utf-8')
                # third, search for the business
                if cBusiness.find({'yelpID': businessID}).count() == 1:
                    b = cBusiness.find({'yelpID': businessID}).next()
                    display['bname'] = b['name'].encode('utf-8')
                    hdID = b['hdID']
                    # fourth, search for the restaurant inspections
                    if cInspection.find({'hdID' : hdID}).count() > 0:
                        inslist = []
                        for ins in cInspection.find({'hdID' : hdID}):
                            inslist.append({'idate' : ins['date'], 'itype' : ins['type'], 'iscore' : ins['score']})
                        display['inslist'] = inslist
            displayList.append(formatResult(display))
        print 'The term <b>{0}</b> is found in {1} reviews<br/>'.format(p, matchCount)
        if matchCount > maxMatch:
            print 'Display is currently limited to the first {0} reviews<br/>'.format(maxMatch)
        for d in displayList:
            print '<hr>'
            print d
            pass
    else:
        print 'the term <b>{0}</b> matches zero documents'.format(p)

def formatResult(d):
    s = '<table>'
    s = ''.join((s, '<tr><td colspan=3>', d['bname'], '</td></tr>'))
    s = ''.join((s, '<tr><td colspan=3>Review Date: ', d['rdate'], '</td></tr>'))
    termEnd = -1
    reviewText = d['rtext']
    idx = d['idx']
    m = re.search(r'[\s.,;!]', reviewText[idx:])
    if m:
        termEnd = idx + m.start()
    termEnd = max(termEnd, idx + len(d['qterm']))
    start = max([0, idx - 40])
    end = min([idx + 40, len(reviewText)])
    try:
        s = ''.join((s, '<tr><td colspan=3>&quot;{0}<b>{1}</b>{2}&quot;</td></tr>'.format(reviewText[start:idx], reviewText[idx:termEnd], reviewText[termEnd:end])))
    except:
        s = ''.join((s, '<tr><td colspan=3>Encoding error occurred on original review text</td></tr>'))
    s = ''.join((s, '<tr><td colspan=3><u>Recent Inspections (type, date, score):</u></td></tr>'))
    for i in d['inslist']:
        s = ''.join((s, '<tr><td>&nbsp;&nbsp;', i['itype'], '</td><td>', i['idate'], '</td><td>', i['iscore'], '</td></tr>'))
    s = ''.join((s, '</table>'))
    return s

def initDisplay():
    d = {}
    d['qterm'] = ''
    d['idx'] = ''
    d['rdate'] = ''
    d['rtext'] = ''
    d['bname'] = ''
    d['inslist'] = []
    return d

#query('coli')
if __name__ == '__main__':
	query(sys.argv[1])
