'''
'''
from __future__ import print_function
from mrjob.job import MRJob
from mrjob.step import MRStep
import sys

class FrequentPages(MRJob):

    def steps(self):
        return [
            MRStep(mapper=self.mapper,
                   combiner=self.combiner,
                   reducer=self.reducer,
                   reducer_final=self.reducer_final)
        ]

    def mapper(self, _, line):
        ''' enumerate page visits
        '''
        row = line.split(',')
        if row[0] == 'V':
            yield row[1], 1
    
    def combiner(self, page, i):
        yield page, sum(i)

    # track top five frequent pages in sorted order
    topfive = [['',0]]
    
    def inserttopfive(self, page, total):
        for j in range(0, len(self.topfive)):
            if total > self.topfive[j][1]:
                self.topfive.insert(j, (page, total))
                if len(self.topfive) > 5:
                    self.topfive.pop()
                break
    
    def reducer(self, page, i):
        ''' sum page counts
        '''
        total = sum(i)
        self.inserttopfive(page, total)
        
    def reducer_final(self):
        for i in range(0, len(self.topfive)):
            yield(self.topfive[i][0], self.topfive[i][1])

if __name__ == '__main__':
    FrequentPages.run()