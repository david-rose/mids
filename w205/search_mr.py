
# -*- coding: utf-8 -*-
"""

"""
import json
from mrjob.job import MRJob
import oauth2
import re
import socket
import sys
import traceback
import urllib
import urllib2

API_HOST = 'api.yelp.com'
PHONE_PATH = '/phone_search/'
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'
SEARCH_LIMIT = 10

# regular expressions for normalizing addresses and names
EXCLUDES = re.compile('\W')
TRAILING_S = re.compile('S$') # JOES -> JOE
TRAILING_ST = re.compile('(\d+)ST$') # 1ST -> 1
TRAILING_ND = re.compile('(\d+)ND$') # 2ND -> 2
TRAILING_RD = re.compile('(\d+)RD$') # 3RD -> 3
TRAILING_TH = re.compile('(\d+)TH$') # 4TH -> 4
LEADING_0 = re.compile('^0+(\d+)$') # 05 -> 5
LEADING_SHARP = re.compile('^#\d+') # remove apt number
BOULEVARD = re.compile('^BOUL\w+')
AVENUE = re.compile('^AVE\w+')
ROAD = re.compile('^ROAD')
STREET = re.compile('^STREET')
HIGHWAY = re.compile('^HIGHW\w+')
PLACE = re.compile('^PLACE')
LANE = re.compile('^LANE')
WEST = re.compile('^WEST')
EAST = re.compile('^EAST')
NORTH = re.compile('^NORTH|^NO')
SOUTH = re.compile('^SOUTH|^SO')
THE = re.compile('^THE$')

# OAuth credentials
CONSUMER_KEY = 'iVW4BGPGDpi__tSPJzguYg'
CONSUMER_SECRET = 'RMNw-hzXY1L8BuSSLlMjPVPxJ90'
TOKEN = 'KwU1ohlhbYk1uwlYw2zp89yFvKiUsPb5'
TOKEN_SECRET = 'ZhJVNzJtM7_ME9_zxXSA6aS28Es'

HTTP_RETRIES = 5
HTTP_TIMEOUT = 3

class GetBusiness(MRJob):

    def mapper(self, _, line):
        p = self.parse('sf', line)
        response = None
        try:
#            response = self.search('phone', PHONE_PATH, p)
#            response = self.search('name_address', SEARCH_PATH, p)
            response = self.search('coordinate', SEARCH_PATH, p)
        except:
            print sys.exc_info()[0], sys.exc_info()[1]
            traceback.print_exc(sys.exc_info()[2])
        yield(p['businessID'], response if response else '')

    def parse(self, src, line):
        """ extract parameters from health department record based on data source """
        r = line.split('\t')
        p = {}
        if src == 'sf':
            p['businessID'] = r[0]
            p['name'] = r[1]
            p['address'] = r[2]
            p['city'] = r[3]
            p['state'] = r[4]
            p['zip'] = r[5]
            p['latitude'] = r[6]
            p['longitude'] = r[7]
            p['phone'] = r[8]
        elif src == 'nyc':
            p['businessID'] = r[0]
            p['name'] = r[1]
            # nyc separates the building number from the street name
            p['address'] = ' '.join([r[3].strip(), r[4].strip()])
            p['city'] = 'NYC'
            p['state'] = 'NY'
            p['zip'] = r[5]
            p['latitude'] = None
            p['longitude'] = None
            p['phone'] = r[6]
        return p        

    def search(self, searchtype, searchpath, p):
        url_params = {'limit': SEARCH_LIMIT}
        if searchtype == 'coordinate':
            url_params['term'] = p['name']
            if p['latitude'] and p['longitude']:
                url_params['ll'] = ','.join([p['latitude'],p['longitude']])
            else:
                url_params['location'] = ' '.join([p['address'], p['city'], p['state'], p['zip']])
        elif searchtype == 'phone':
            if p['phone'] is None:
                return None
            url_params['phone'] = p['phone']
            url_params['ywsid'] = CONSUMER_KEY
        elif searchtype == 'name_address':
            url_params['term'] = p['name'],
            url_params['location'] = ' '.join([p['address'], p['city'], p['state'], p['zip']])
            if p['latitude'] != None and p['longitude'] != None:
                url_params['cll'] = ','.join([p['latitude'],p['longitude']])
        
        response = self.request(API_HOST, searchpath, url_params=url_params)
        businesses = response.get('businesses')
        if not businesses:
            return None
        byName = 1
        id = self.selectByNameAddress(businesses,p['name'],p['address'],byName)
        if id is not None:
            business_path = BUSINESS_PATH + urllib.quote(id.encode('utf-8'))
            response = self.request(API_HOST, business_path)
        else:
            response = None
        return response    
    
    def request(self, host, path, url_params=None):
        url_params = url_params or {}
        encoded_params = urllib.urlencode(url_params)
        url = 'http://{0}{1}?{2}'.format(host, path, encoded_params)
    
        consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
        oauth_request = oauth2.Request('GET', url, {})
        oauth_request.update(
            {
                'oauth_nonce': oauth2.generate_nonce(),
                'oauth_timestamp': oauth2.generate_timestamp(),
                'oauth_token': TOKEN,
                'oauth_consumer_key': CONSUMER_KEY
            }
        )
        token = oauth2.Token(TOKEN, TOKEN_SECRET)
        oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
        signed_url = oauth_request.to_url()
        response = {}
        conn = None
        attempt = 0
        while attempt < HTTP_RETRIES:
            attempt += 1
            try:
                # timeout extends longer for each retry
                timeout = attempt * HTTP_TIMEOUT
                conn = urllib2.urlopen(signed_url, None, timeout)
                response = json.loads(conn.read())
            except (socket.timeout) as e:
                if attempt == HTTP_RETRIES:
                    print '*********************************'
                    print url
                    print 'Meximum retries reached'
                    print 'Exception: ',repr(e)
                    sys.stdout.flush()
            except KeyboardInterrupt as e:
                sys.exit('Keyboard Interrupt, exiting...')
            except Exception as e:
                print '*********************************'
                print signed_url
                print 'Exception: ', repr(e)
                sys.stdout.flush()
                break
            finally:
                if conn:
                    conn.close()
        return response
    
    def normalizeName(self, name):
        name = name.upper()
        tokens = name.split()
        newname = ''
        for t in tokens:
            # remove trailing S
            t = TRAILING_S.sub('',t)
            t = THE.sub('',t)
            t = EXCLUDES.sub('',t)
            if len(t) > 0:
                newname = ' '.join([newname,t])
        return newname
    
    def normalizeAddress(self, addr):
        addr = addr.upper()
        tokens = addr.split()
        newaddr = ''
        for t in tokens:
            t = TRAILING_ST.sub(r'\1',t)
            t = TRAILING_ND.sub(r'\1',t)
            t = TRAILING_RD.sub(r'\1',t)
            t = TRAILING_TH.sub(r'\1',t)
            t = LEADING_0.sub(r'\1',t)
            t = LEADING_SHARP.sub('',t)
            t = BOULEVARD.sub('BLVD',t)
            t = AVENUE.sub('AVE',t)
            t = ROAD.sub('RD',t)
            t = STREET.sub('ST',t)
            t = HIGHWAY.sub('HWY',t)
            t = LANE.sub('LN',t)
            t = PLACE.sub('PL',t)
            t = WEST.sub('W',t)
            t = EAST.sub('E',t)
            t = NORTH.sub('N',t)
            t = SOUTH.sub('S',t)
            if len(t) > 0:
                newaddr = ' '.join([newaddr,t])
        return newaddr.strip()
        
    def selectByNameAddress(self, businesses, name, address, byName):
        searchName = self.normalizeName(name)
        searchAddress = self.normalizeAddress(address)
        id = None
        for b in businesses:
            ''' look for a match based on address'''
            bName = self.normalizeName(b['name'])
            bAddress = ''
            if (b.has_key('location')):
                try:
                    bAddress = self.normalizeAddress(b['location']['address'][0])
                except:
                    pass
            elif (b.has_key('address1')):
                bAddress = self.normalizeAddress(b['address1'])
            else:
                # problems
                raise 'Unknown address format: ' + b
            if bAddress == searchAddress:
                id = b['id']
                break
#            else:
#                print searchName,searchAddress,' : ',bName,bAddress
        if id == None and byName:
            ''' try again, matching on name only to allow for imperfect address match '''
            for b in businesses:
                bName = self.normalizeName(b['name'])
                bAddress = ''
                if (b.has_key('location')):
                    try:
                        bAddress = self.normalizeAddress(b['location']['address'][0])
                    except:
                        pass
                elif (b.has_key('address1')):
                    bAddress = self.normalizeAddress(b['address1'])
                else:
                    # problems
                    raise 'Unknown address format: ' + b
                if bName == searchName:
                    id = b['id']
                    break
        return id
       

if __name__ == '__main__':
    GetBusiness.run()
