#!/usr/bin/env python

import cgi
import urllib
import urllib2
try:
    import  json
except ImportError:
    import  json

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class localsearchError(Exception):
    G_GEO_SUCCESS               = 200
    G_GEO_SERVER_ERROR          = 500
    G_GEO_MISSING_QUERY         = 601
    G_GEO_UNKNOWN_ADDRESS       = 602
    G_GEO_UNAVAILABLE_ADDRESS   = 603
    G_GEO_BAD_KEY               = 610
    G_GEO_TOO_MANY_QUERIES      = 620

    _STATUS_MESSAGES = {
        G_GEO_SUCCESS               : 'SUCCESS',
        G_GEO_SERVER_ERROR          : 'Server Error.',
        G_GEO_MISSING_QUERY         : 'Parameters are missing. Please refer to the format and structure your input.',
        G_GEO_UNKNOWN_ADDRESS       : 'Unknown address error.Please add more details in your from and to fields for appropriate results',
        G_GEO_UNAVAILABLE_ADDRESS   : 'G_GEO_UNAVAILABLE_ADDRESS',
        G_GEO_BAD_KEY               : 'G_GEO_BAD_KEY',
        G_GEO_TOO_MANY_QUERIES      : 'Too many queries at this point of time. Please try later.',
    }
    def __init__(self,status_code,url,response):
        self.status = status_code
        self.url = url
        self.response = response

    def __str__(self):
        if self.status in self._STATUS_MESSAGES:
            if self.response is not None and 'responseDetails' in self.response:
                retval = 'Error %s' % (self.response['responseDetails'])
            else:
                retval = 'Error %s' % (self.status, self._STATUS_MESSAGES[self.status])
        else:
            retval = str(self.status)
        return retval

    def __unicode__(self):
        return unicode(self.__str__())

STATUS_OK = localsearchError.G_GEO_SUCCESS

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""
          <html>
        <meta name='txtweb-appkey' content='3b58eea1-0988-4976-a200-02b12ecc8bfd' />
            <body>
             <h2>Welcome to seaarchAROUND on txtWeb!</h2>
              <form action="/LocalSearch" method="get">
                <div>Enter Input:<input type="text" name="txtweb-message" size="40"></div>
                <div><input type="submit" value="Local Search"></div>
              </form>
            </body>
          </html>""")




def newapp_key(query):
    api_key="AIzaSyAhGQbqVw72VpAq274yX3heyuYSxmYZ71k"#http://code.google.com/apis/maps/signup.html
    query=query.split(" ")
    query="+".join(query)
    
    locsearch_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query='+query+'&sensor=true&key='+api_key
    url = locsearch_url
    #print url
    request = urllib2.Request(
        url, None, {'Referer': "http://rishabhderoy.appspot.com"})#put your referrer in here
    response = urllib2.urlopen(request)
    res=""
    # Process the JSON string.
    results = json.load(response)
    
    status_code = results['status']
    returnedResults = None
    if len(results['results'])>0 :
        for i in range(len(results['results'])):
            if returnedResults is None:
                    returnedResults = results
            else:
                returnedResults['results'].extend(results['results'])


            res += str(i+1)+".)"
            res += results['results'][i]['name']+ " Location :"
            res += results['results'][i]['formatted_address']
            res += "<br>"
            res += "  "
                #results['responseData']['results'][i]['phoneNumbers']=[]
                #print results['responseData']['results'][i]['phoneNumbers'][0]['number']
    else:
            res = "No entries found. Please try again with other nearby landmarks and append the city name"
    return res

def localsearch(query):
    api_key = 'AIzaSyChyQKoy20g7uxFxkza34Rj8ig1AMTXx00'#http://code.google.com/apis/maps/signup.html
    query=query.split(" ")
    query="+".join(query)
    
    locsearch_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query='+query+'&sensor=true&key='+api_key
    url = locsearch_url
    #print url
    request = urllib2.Request(
        url, None, {'Referer': "http://rishabhderoy.appspot.com"})#put your referrer in here
    response = urllib2.urlopen(request)

    # Process the JSON string.
    results = json.load(response)
    status_code = results['status']
    returnedResults = None
    res= ""
    pro=["ZERO_RESULTS","REQUEST_DENIED","INVALID_REQUEST"]
    if status_code in pro :
        res = "No entries found. Please try again with other nearby landmarks and append the city name"
    elif (status_code == "OVER_QUERY_LIMIT") :
        
        res =newapp_key(query)
    else:
        if len(results['results'])>0 :
            for i in range(len(results['results'])):
                if returnedResults is None:
                    returnedResults = results
                else:
                    returnedResults['results'].extend(results['results'])
                res += str(i+1)+".)"
                res += results['results'][i]['name']+ " Location :"
                res += results['results'][i]['formatted_address']
                res += "<br>"
                res += "  "
                #results['responseData']['results'][i]['phoneNumbers']=[]
                #print results['responseData']['results'][i]['phoneNumbers'][0]['number']
        else:
            res = "No entries found. Please try again with other nearby landmarks and append the city name"
    return res


class LocalSearch(webapp.RequestHandler):
    def get(self):
        message = cgi.escape(self.request.get('txtweb-message')) #get hold of txtweb-message here
        if message == "": #If message is empty, reply with a welcome message
            self.response.out.write("""<html><head><meta name="txtweb-appkey" content="3b58eea1-0988-4976-a200-02b12ecc8bfd" /></head><body><p>To use this app : reply to txtWeb using @locsearch[space][what you want to search for with city preferably]<br> Eg: @dirsearch cafe near jayanagar bangalore</p></body></html>""")
        else:
            res = localsearch(message)
            if res == "":
                self.response.out.write("""<html><head><meta name="3b58eea1-0988-4976-a200-02b12ecc8bfd" /></head><body>Sorry no listings found. Please try again with closeby landmarks and append the city name.<br/></body></html>""")
            else:
                self.response.out.write("""<html><head><meta name="txtweb-appkey" content="3b58eea1-0988-4976-a200-02b12ecc8bfd" /></head><body>"""+res+"""<br/></body></html>""")
application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/LocalSearch',LocalSearch)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

