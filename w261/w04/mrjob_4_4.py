'''
'''
from __future__ import print_function
from mrjob.job import MRJob
import sys

class FrequentVisitors(MRJob):

    def mapper(self, _, line):
        ''' count page visits
        '''
        row = line.split(',')
        if row[0] == 'V':
            yield row[1], row[3]
    
    visitors = {}
    currentpage = ''
        
    def reducer(self, page, visitor):
        ''' sum page visitor counts
        '''
        if not page == self.currentpage:
            if len(self.visitors) > 0:
                #print('page change: current page: {}, new page: {}, visitors: {}'
                #      .format(self.currentpage, page, len(self.visitors)), file=sys.stderr)
                frequentv = []
                maxv = 0
                #print(self.currentpage, len(self.visitors), file=sys.stderr)
                for v in self.visitors:
                    #print('\t', v, self.visitors[v], file=sys.stderr)
                    if self.visitors[v] > maxv:
                        frequentv = [v]
                        maxv = self.visitors[v]
                    elif self.visitors[v] == maxv:
                        frequentv.append(v)
                #print(self.currentpage, frequentv, file=sys.stderr)
                for v in frequentv:
                    yield self.currentpage, v                
            self.visitors = {}
            self.currentpage = page
        for v in visitor:
            if not v in self.visitors:
                self.visitors[v] = 0
            self.visitors[v] += 1
        
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