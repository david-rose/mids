#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 14:42:29 2014


"""

from nltk.stem.snowball import SnowballStemmer
import re
import simplejson
import sys

class ReviewWordIndex(object):
    '''
    build inverted index on review text
    '''

    stemmer = SnowballStemmer("english", ignore_stopwords=True)

    wd = {}

    def go(self, fname):
        with open(fname, 'r') as f:
            for line in f:
                j = re.search('({.*})', line)
                s = j.group(1) if j else None
                if s:
                    d = simplejson.loads(s)
                    reviewID = d['reviewID']
                    text = d['reviewText']
                    words = [word for word in re.split('\s',text) if len(word) > 0]
                    lastIdx = 0
                    for word in words:
                        # strip trailing punctuation
                        word = re.sub(r'\W+$', '', word)
                        w = self.stemmer.stem(re.sub(r'\W', '', word.lower()))
                        idx = lastIdx
                        try:
                            idx = text.index(word, lastIdx)
                            lastIdx = idx + 1
                        except:
                            idx = -1
                        l = [reviewID, idx]
                        if w in self.wd:
                            self.wd[w].append(l)
                        else:
                            self.wd[w] = [l]
        for w in sorted(self.wd):
            print '{0}\t{1}'.format(w, simplejson.dumps(self.wd[w]))

if __name__ == '__main__':
    ReviewWordIndex.go(ReviewWordIndex(), sys.argv[1])
