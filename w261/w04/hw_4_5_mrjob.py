''' map/reduce approach to determining stable centroids using
    a K-means algorithm    
'''
from __future__ import print_function
from numpy import argmin, array, random
from mrjob.job import MRJob
from mrjob.step import MRStep
from itertools import chain
import sys

# Calculate find the nearest centroid for data point 
def MinDist(datapoint, centroid_points):
    datapoint = array(datapoint)
    centroid_points = array(centroid_points)
    diff = datapoint - centroid_points 
    diffsq = diff*diff
    # Get the nearest centroid for each instance
    sumofsquares = list(diffsq.sum(axis = 1))
    minindex = argmin(sumofsquares)
    return minindex

# Check whether centroids converge
def stop_criterion(centroid_points_old, centroid_points_new, T):
    oldvalue = list(chain(*centroid_points_old))
    newvalue = list(chain(*centroid_points_new))
    Diff = [abs(x-y) for x, y in zip(oldvalue, newvalue)]
    Flag = True
    for i in Diff:
        if i > T:
            Flag = False
            break
    return Flag

class MRKmeans(MRJob):

    centroid_points=[]
    k = -1
    CENTROIDFILE = '/tmp/centroids.txt'
    
    def steps(self):
        return [
            MRStep(mapper_init = self.mapper_init, 
                   mapper=self.mapper,
                   combiner = self.combiner,
                   reducer=self.reducer)
               ]
    # load initial centroids
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
        # print the value of k back to the cache file
        with open(self.CENTROIDFILE, 'w') as fout:
            print('{}'.format(self.k), file = fout)
        
    #load data and output the nearest centroid index and data point 
    def mapper(self, _, line):
        D = (map(float,line.split(',')[3:]))
        centroid = MinDist(D, self.centroid_points)
        yield centroid, (D, 1)
    
    # aggregate data points locally
    def combiner(self, centroid, inputdata):
        count = 0
        bucket = [0] * 1000
        for data, n in inputdata:
            count += n
            data = map(float, data)
            for j in range(0, len(data)):
                bucket[j] += data[j]
        yield centroid, (bucket, count)

   
    # aggregate values for each centroid, then recalculate centroids
    def reducer(self, idx, inputdata): 
        centroids = []
        with open(self.CENTROIDFILE, 'rb') as fin:
            self.k = int(fin.readline().strip())
        num = [0] * self.k 
        for i in range(self.k):
            centroids.append([0.0]*1000)
        for data, n in inputdata:
            num[idx] += n
            data = map(float, data)
            for j in range(0, len(data)):
                centroids[idx][j] += data[j]
        for j in range(0, len(centroids[idx])):
            centroids[idx][j] = centroids[idx][j] / num[idx]
        with open(self.CENTROIDFILE, 'a') as fout:
            print(','.join(str(i) for i in centroids[idx]), file = fout)
        yield idx, (centroids[idx])
      
if __name__ == '__main__':
    MRKmeans.run()