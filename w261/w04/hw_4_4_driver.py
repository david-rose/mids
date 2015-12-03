import csv
from mrjob import util
import sys
from hw_4_4_mrjob import FrequentVisitors

util.log_to_null() # to suppress a 'no handler found' message

# construct list of page ids and urls to satisfy the requirement
# this is essentially a join; it makes better sense to do this in
# the driver as doing so in hadoop offers no advantages and incurs
# additional network overhead; mrjob output is parsed and augmented with
# the url information
pageinfo = {}
# read in the page attributes including the url; this could also have
# been preprocessed so that the page attributes were in their own file
with open('flattened.data', 'rb') as fin:
    csvreader = csv.reader(fin, delimiter = ',', quotechar = '"')
    for line in csvreader:
        if line[0] == 'A':
            pageid = line[1]
            url = line[4]
            pageinfo[pageid] = url

mr_job = FrequentVisitors(args=sys.argv[1:])
with mr_job.make_runner() as runner:
    runner.run()
    for line in runner.stream_output():
        page, visitor = line.replace('"', '').split()
        print pageinfo[page], page, visitor