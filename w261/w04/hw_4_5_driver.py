''' driver script for Kmeans job
'''
from __future__ import print_function
from numpy import random
from hw_4_5_mrjob import MRKmeans, stop_criterion
from hw_4_5_mrjob_labeler import MRLabeler
from mrjob import util
import sys

util.log_to_null() # to suppress a 'no handler found' message
CENTROIDFILE = '/tmp/centroids.txt'

def countlabels():
    ''' count the number of each classification as labeled in the
        original data set
    '''
    with open('topUsers_Apr-Jul_2014_1000-words.txt', 'rb') as f:
        labels = {}
        for line in f:
            row = line.split(',')
            label = row[1]
            if not label in labels:
                labels[label] = 0
            labels[label] += 1
    return labels

def init_centroids_random_internal(k):
    ''' select initial centroids by choosing data points
        randomly from the data set
    '''
    randoms = sorted(random.randint(0, 1000, size = k))
    centroids = []
    with open('topUsers_Apr-Jul_2014_1000-words.txt', 'rb') as f:
        lineno = 0
        count = 0
        for line in f:
            if lineno in randoms:
                row = line.strip().split(',')
                data = map(float, row[3:])
                # normalize the values
                data = [i / float(row[2]) for i in data]
                centroids.append(data)
                count += 1
                if count == k:
                    break
            lineno += 1
    with open(CENTROIDFILE, 'w') as f:
        print('{}'.format(k), file = f)
        for tuple in centroids:
            print(','.join(str(i) for i in tuple), file = f)
    return centroids

def init_centroids_random_external(k):
    ''' create initial centroids by generating random values
    '''
    centroids = []
    for i in range(k):
        centroid = []
        for j in range(1000):
            centroid.append(random.uniform(0.0, .5))
        centroids.append(centroid)
    with open(CENTROIDFILE, 'w') as fout:
        print('{}'.format(k), file = fout)
        for tuple in centroids:
            print(','.join(str(i) for i in tuple), file = fout)
    return centroids

def init_centroids_perturbed(k):
    ''' create initial centroids by using aggregated values and
        perturbing them with random noise
    '''
    centroids = []
    with open('topUsers_Apr-Jul_2014_1000-words_summaries.txt', 'rb') as f:
        for line in f:
            row = line.strip().split(',')
            if row[0] == 'ALL_CODES':
                data = map(float, row[3:])
                # normalize the values
                data = [i / float(row[2]) for i in data]
                for i in range(k):
                    centroid = []
                    for j in range(len(data)):
                        # modify each value with random number in the
                        # range of +- the value; avoids a small number being modified
                        # by a large number
                        centroid.append(data[j] + random.uniform(-1 * data[j], data[j]))
                    centroids.append(centroid)
                break
    with open(CENTROIDFILE, 'w') as f:
        print('{}'.format(k), file = f)
        for tuple in centroids:
            print(','.join(str(i) for i in tuple), file = f)
    return centroids

def init_centroids_trained(k):
    ''' create initial centroids by choosing the class-specific aggregate values
    '''
    centroids = []
    with open('topUsers_Apr-Jul_2014_1000-words_summaries.txt', 'rb') as f:
        for line in f:
            row = line.strip().split(',')
            if row[0] == 'CODE':
                code = row[1]
                total = int(row[2])
                data = map(float, row[3:])
                # normalize the values
                data = [i / total for i in data]
                centroids.append(data)
    with open(CENTROIDFILE, 'w') as f:
        print('{}'.format(k), file = f)
        for tuple in centroids:
            print(','.join(str(i) for i in tuple), file = f)
    return centroids

def getpurity(clusters):
    majority = 0
    for c in clusters:
        counts = map(int, clusters[c]);
        majority += max(counts)
    return majority / float(1000)
    
def go(centroid_points):
    ''' submit the centroid calculation job;
        follow that with the data labeling job
    '''
    mr_job = MRKmeans(args = ['normalized.txt'])
    iteration = 0
    while(1):
        # save previous centroids to check convergency
        centroid_points_old = centroid_points[:]
        with mr_job.make_runner() as runner: 
            runner.run()
            # capture reducer output
            for line in runner.stream_output():
                key,value =  mr_job.parse_output_line(line)
                centroid_points[key] = value
        iteration += 1
        if stop_criterion(centroid_points_old, centroid_points, 0.001):
            break
    print('centroids converged: {} iterations'.format(iteration), file = sys.stderr)
    mr_job = MRLabeler(args = ['normalized.txt'])
    labels = countlabels()
    clusters = {}
    with mr_job.make_runner() as runner: 
        runner.run()
        for line in runner.stream_output():
            centroid, value =  mr_job.parse_output_line(line)
            label = int(value[0])
            count = int(value[1])
            if not centroid in clusters:
                clusters[centroid] = [0,0,0,0]
            clusters[centroid][label] += count
        for c in sorted(clusters):
            results = map(float, clusters[c])
            print('centroid {}: label 0: {:.4f} label 1: {:.4f} label 2: {:.4f} label 3: {:.4f}'
                  .format(c, results[0] / labels['0'], results[1] / labels['1'], 
                          results[2] / labels['2'], results[3] / labels['3'])
                  )
            # print the actual counts
#             print('centroid {}: counts: {}'.format(c, clusters[c]), 
#                   file = sys.stderr)
        print('purity: {:.4f}'.format(getpurity(clusters)))
        print('', file = sys.stderr)

print('k = 4, random initialization, v1', file = sys.stderr)
go(init_centroids_random_internal(4))
print('k = 4, random initialization, v2', file = sys.stderr)
go(init_centroids_random_external(4))
print('k = 2, perturbed initialization', file = sys.stderr)
go(init_centroids_perturbed(2))
print('k = 4, perturbed initialization', file = sys.stderr)
go(init_centroids_perturbed(4))
print('k = 4, trained initialization', file = sys.stderr)
go(init_centroids_trained(4))
