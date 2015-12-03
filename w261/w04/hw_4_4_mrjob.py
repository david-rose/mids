''' count the number of page-visitor combinations and
    for each page list the most frequent visitors
    
    the data does not effectively support this operation since it
    only lists unique page visits, therefore every visitor
    will show up as having visited once, and therefore every visitor
    is the most frequent visitor
'''
from __future__ import print_function
from mrjob.job import MRJob
import sys

class FrequentVisitors(MRJob):

    def mapper(self, _, line):
        ''' enumerate page visitors
        '''
        row = line.split(',')
        if row[0] == 'V':
            # page ID, visitor ID
            yield row[1], row[3]
    
    # data structures to manage reducer logic
    visitors = {}
    currentpage = ''
        
    def reducer(self, page, visitor):
        ''' sum page visitor counts
        '''
        if not page == self.currentpage:
            ''' page id has changed in the stream, so process and emit
                the information for the current page
            '''
            if len(self.visitors) > 0:
                frequentv = []
                maxv = 0
                for v in self.visitors:
                    if self.visitors[v] > maxv:
                        frequentv = [v]
                        maxv = self.visitors[v]
                    elif self.visitors[v] == maxv:
                        frequentv.append(v)
                # emit results
                for v in frequentv:
                    yield self.currentpage, v                
            # reset counters
            self.visitors = {}
            self.currentpage = page
        for v in visitor:
            if not v in self.visitors:
                self.visitors[v] = 0
            self.visitors[v] += 1
    
    # process any remaining values after stream closes
    def reducer_final(self):
        if len(self.visitors) > 0:
            frequentv = []
            maxv = 0
            for v in self.visitors:
                if self.visitors[v] > maxv:
                    frequentv = [v]
                elif self.visitors[v] == maxv:
                    frequentv.append(v)
            for v in frequentv:
                yield self.currentpage, v                
         
if __name__ == '__main__':
    FrequentVisitors.run()