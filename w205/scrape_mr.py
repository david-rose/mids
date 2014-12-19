
# -*- coding: utf-8 -*-
"""

"""
import json
from lxml import html
import math
from mrjob.job import MRJob
import random
import re
import socket
import sys
import time
import traceback
import urllib2

WWW_HOST = 'www.yelp.com'
BIZ_PATH = '/biz/'
REVIEWSPERPAGE = 40
LONG_WAIT_PERIOD = 120
# maximum wait time between queries, in seconds
WAIT_PERIOD = 10 
HTTP_RETRIES = 5
HTTP_TIMEOUT = 3
HTTP_HEADERS = [{
    'User-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
},
{
    'User-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
},
{
    'User-agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
},
{
    'User-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0)',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}
]


class Scrape(MRJob):

    def mapRetrieveURL(self, _, line):
        ''' construct URLs to be used for retrieving reviews in the next step'''
        # ensure that this line contains valid data
        isValid = re.match(r'^"\d+"\t.+$',line)
        if isValid:
            businessID = self.parseBusinessID(line)
            if businessID is not None:
                try:
                    url = 'http://{0}{1}/{2}'.format(WWW_HOST, BIZ_PATH, businessID)
                    doc = self.getDocFromURL(url)            
                    pageCount = 1
                    reviewCount = -1
                    e = doc.find_class('page-of-pages')
                    if e is not None:
                        s = re.search('Page \d+ of (\d+)', e[0].text_content(), re.DOTALL)
                        if s:
                            pageCount = int(s.group(1))
                    e = doc.xpath("//span[@itemprop='reviewCount']")
                    if len(e) > 0:
                        reviewCount = e[0].text_content()
                    print '{0} contains {1} pages and {2} reviews'.format(businessID, pageCount, reviewCount)
                    # set pageCount to a small integer to limit number of URLs visited for each business ID
                    # pageCount = 1
                    for i in range(0, pageCount):
                        if i == 0:
                            url = 'http://{0}{1}/{2}'.format(WWW_HOST, BIZ_PATH, businessID)
                        else:
                            url = 'http://{0}{1}/{2}?start={3}'.format(WWW_HOST, BIZ_PATH, businessID, i * REVIEWSPERPAGE)
                        yield(businessID, url)
                except:
                    print sys.exc_info()[0], sys.exc_info()[1]
                    traceback.print_exc(sys.exc_info()[2])
                finally:
                    time.sleep(WAIT_PERIOD * random.random())

    def parseBusinessID(self, line):
        r = line.split('\t', 1)
        j = json.loads(r[1])
        businessID = None
        for key in j:
            if key == 'id':
                businessID = j[key]
        return businessID.encode('utf-8') if businessID else businessID

    def parseBusinessIDFromURL(self, url):
        businessID = None
        m = re.match(r'http://www.yelp.com/biz//([^ ?]+)', url)
        if m:
            businessID = m.group(1)
        return businessID.encode('utf-8') if businessID else businessID

    def mapHandleErrorURL(self, _, line):
        ''' retry the URLs that reported errors in the original run '''
        s = line.split()
        url = s[0]
        key = self.parseBusinessIDFromURL(url)
        try:
            self.longWait()
            doc = self.getDocFromURL(url)
            reviewList = doc.xpath("//div[@class='review-content']")
            for review in reviewList:
                reviewRating = None
                reviewDate = None
                reviewText = None
                rating = review.find('.//meta[@itemprop="ratingValue"]')
                if rating is not None:
                    reviewRating = rating.get('content')
                date = review.find('.//meta[@itemprop="datePublished"]')
                if date is not None:
                    reviewDate = date.get('content')
                text = review.find(".//p[@itemprop='description']")
                if text is not None:
                    reviewText = text.text_content()
                reviewProps = {'reviewRating': reviewRating, 'reviewDate': reviewDate, 'reviewText': reviewText}
                yield(key.encode('utf-8'), reviewProps)
        except:
            print sys.exc_info()[0], sys.exc_info()[1]
            traceback.print_exc(sys.exc_info()[2])
        finally:
            time.sleep(WAIT_PERIOD * random.random())
        
        
    def mapRetrieveReview(self, key, url):
        ''' retrieve a page of reviews, and extract each review from the html response '''
        try:
            self.longWait()
            doc = self.getDocFromURL(url)
            reviewList = doc.xpath("//div[@class='review-content']")
            for review in reviewList:
                reviewRating = None
                reviewDate = None
                reviewText = None
                rating = review.find('.//meta[@itemprop="ratingValue"]')
                if rating is not None:
                    reviewRating = rating.get('content')
                date = review.find('.//meta[@itemprop="datePublished"]')
                if date is not None:
                    reviewDate = date.get('content')
                text = review.find(".//p[@itemprop='description']")
                if text is not None:
                    reviewText = text.text_content()
                reviewProps = {'reviewRating': reviewRating, 'reviewDate': reviewDate, 'reviewText': reviewText}
                yield(key.encode('utf-8'), reviewProps)
        except:
            print sys.exc_info()[0], sys.exc_info()[1]
            traceback.print_exc(sys.exc_info()[2])
        finally:
            time.sleep(WAIT_PERIOD * random.random())

    """
    <div class="review-content">
        <div class="biz-rating biz-rating-very-large clearfix">
            <div itemprop="reviewRating" itemscope itemtype="http://schema.org/Rating">                        
                <div class="rating-very-large">
                    <i class="star-img stars_3" title="3.0 star rating">
                        <img alt="3.0 star rating" class="offscreen" height="303" src="http://s3-media3.fl.yelpcdn.com/assets/2/www/img/c2252a4cd43e/ico/stars/v2/stars_map.png" width="84">
                    </i>
                    <meta itemprop="ratingValue" content="3.0">
                </div>
            </div>
            <span class="rating-qualifier">
                <meta itemprop="datePublished" content="2014-09-10">
                9/10/2014
            </span>
        </div>
        <p itemprop="description" lang="en">Pros: open late, fast, inexpensive, fresh naan, tender meat (tried lamb curry and chicken tikka masala)<br><br>Cons: very poor customer service (cashier especially), no option to modify spice level despite offering &#34;mild, medium, spicy&#34; on the menu, visited twice and both times the tables were sticky.</p> 
    </div>
    """

    def getDocFromURL(self, url):
        attempt = 0
        while attempt < HTTP_RETRIES:
            attempt += 1
            try:
                # timeout extends longer for each retry
                timeout = attempt * HTTP_TIMEOUT
                request = urllib2.Request(url, None, headers=self.getHeaders())
                response = urllib2.urlopen(request, timeout=timeout)
                doc = html.fromstring(response.read())
                return doc
            except socket.timeout as e:
                if attempt == HTTP_RETRIES:
                    print url,repr(e)
                    raise e
            except Exception as e:
                print url,repr(e)
                raise e
                
    def getHeaders(self):
        ''' randomize the http headers, in a vain attempt to confuse the server '''
        i = 4 * random.random()
        j = math.floor(i)
        if j == 4:
            j = 3
        return HTTP_HEADERS[int(j)]
        
    def longWait(self):
        ''' take a long pause every 1 out of 10 (approximately) iterations '''
        j = 10 * random.random()
        if j > 9:
            time.sleep(LONG_WAIT_PERIOD)
        
    def steps(self):
        return [
            self.mr(mapper=self.mapRetrieveURL),
            self.mr(mapper=self.mapRetrieveReview),
#            self.mr(mapper=self.mapHandleErrorURL)
        ]

if __name__ == '__main__':
    Scrape.run()

