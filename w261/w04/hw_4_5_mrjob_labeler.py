''' assigns centroid labels to data points

    this step is done separately from the centroid calculations
    to simplify the data processing
'''
from __future__ import print_function
from numpy import argmin, array, random
from mrjob.job import MRJob
from mrjob.step import MRStep
import sys

from hw_4_5_mrjob import MinDist

class MRLabeler(MRJob):

    centroid_points=[]
    k = -1
    CENTROIDFILE = '/tmp/centroids.txt'
    
    def steps(self):
        return [
            MRStep(mapper_init = self.mapper_init, 
                   mapper=self.mapper,
                   combiner = self.combiner,
                   reducer=self.reducer,
                   reducer_final=self.reducer_final)
               ]
    #load centroids info from file
    def mapper_init(self):
        self.centroid_points=[]
        with open(self.CENTROIDFILE, 'rb') as fin:
            header = True
            for line in fin:
                if header:
                    self.k = int(line.strip())
                    header = False
                else:
                    self.centroid_points.append(map(float,line.strip().split(',')))
        
    # determine the closest centroid for each data point
    def mapper(self, _, line):
        row = line.strip().split(',')
        label = int(row[1])
        D = (map(float,row[3:]))
        centroid = MinDist(D, self.centroid_points)
        yield centroid, (label, 1)
    
    # combine sum of data points locally
    def combiner(self, centroid, inputdata):
        counts = [0, 0, 0, 0]
        for label, n in inputdata:
            counts[label] += n
        for i in range(len(counts)):
            yield centroid, (i, counts[i])

   
    # sum the counts for centroids and classes
    currentcentroid = ''
    counts = []
    def reducer(self, centroid, inputdata): 
        if not centroid == self.currentcentroid:
            for i in range(len(self.counts)):
                yield self.currentcentroid, (i, self.counts[i])
            self.counts = [0, 0, 0, 0]
            self.currentcentroid = centroid
        for label, n in inputdata:
            self.counts[label] += n
            
    def reducer_final(self):
        for i in range(len(self.counts)):
            yield self.currentcentroid, (i, self.counts[i])
        
      
if __name__ == '__main__':
    MRKmeans.run()