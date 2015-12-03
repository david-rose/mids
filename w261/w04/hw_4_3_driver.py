from __future__ import print_function
from mrjob import util
import sys
from hw_4_3_mrjob import FrequentPages
util.log_to_null() # to suppress a 'no handler found' message

# list for storing most frequent pages
# we do this step here since multiple reducer tasks may run and their
# combined output needs to be processed
topfive = [['',0]]
def inserttopfive(page, total):
    for j in range(0, len(topfive)):
        if total > topfive[j][1]:
            topfive.insert(j, (page, total))
            if len(topfive) > 5:
                topfive.pop()
                break

mr_job = FrequentPages(args=sys.argv[1:])
with mr_job.make_runner() as runner:
    runner.run()
    for line in runner.stream_output():
        page, total = line.split()
        inserttopfive(page, int(total))
for i in range(0, len(topfive)):
    print('page: {}, visits: {}'.format(topfive[i][0], 
                                        topfive[i][1]), file=sys.stdout)