from flask import Flask, render_template
from app import app
import urllib2
import xml.etree.ElementTree as ET
from scrape import scrape
import ConfigParser
import collections
import datetime 
import dateutil.relativedelta

class FlickrRc(object):
    def __init__(self):
        self._config = None

    def GetApiKey(self):
        return self._GetOption('api_key')
    def _GetOption(self, option):
        try:
            return self._GetConfig().get('Flickr', option)
        except:
            return None
    def _GetConfig(self):
        if not self._config:
            self._config = ConfigParser.ConfigParser()
            configFilePath = r'flickr/secrets.cfg'
            self._config.read(configFilePath)
        return self._config

rc = FlickrRc()

#Purpose: make GET request to specified url and return response
#In Param: url string
#Returned: response or error
def makeRequest(url):
    req = urllib2.Request(url)
    try:
        return urllib2.urlopen(req)
    except URLError as e:
        return e

#Purpose: format URL for flickr api calls
#in param: url string, api key, extra parameter for when a call needs it
#Returned: response or error
def buildFlickrUrl(url, key, param):
    return url.format(key,param)


#Purpose: make flickr api call
#in param: formatted url
#Returned: formatted xml response from api
def flickrApiCall(url):
    response = makeRequest(url)
    the_page = response.read()

    return ET.fromstring(the_page)

#Purpose: build url for for flickr images to be displayed
#in param: flickr url template string, object of individual image details
#Returned: formatted image source url
def buildUrl(flickrImageUrl, photo):
    return flickrImageUrl.format(photo.attrib['farm'],photo.attrib['server'], photo.attrib['id'], photo.attrib['secret'])

#Purpose: find current time one month ago
#in param: none
#Returned: unix formatted timestamp 
def getUnixTime():
    now = datetime.datetime.utcnow()
    prev = now - dateutil.relativedelta.relativedelta(months=1)

    return prev.strftime("%s")

#Purpose: Main function, handles initial request and get/returns images to be displayed
#in param: none
#Returned: dictionary of image urls sorted by number of comments
@app.route('/', methods=["GET"])
def index():
    tag = 'dctech'
    sinceTime = getUnixTime()
    print sinceTime
    #base url for displaying image from flickr on the page
    flickrImageUrl = "https://farm{0}.staticflickr.com/{1}/{2}_{3}.jpg"
    
    #scrape Instagram for posts containng specified tag
    #dictionary format: {# of comments : [array of image urls]}
    allPhotos = scrape(tag)

    #### call flickr api and get an xml response of images containing specified tag
    baseFlickrRetrieveUrl = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key={0}&tags={1}&safe_search=1&min_upload_date='+ sinceTime
    retrieveFlickrUrl = buildFlickrUrl(baseFlickrRetrieveUrl, rc.GetApiKey(), tag)
    print retrieveFlickrUrl
    root = flickrApiCall(retrieveFlickrUrl)
    ####

    #base url for getting individual photo information from flickr api
    baseFlickrCommentsUrl = "https://api.flickr.com/services/rest/?method=flickr.photos.getInfo&api_key={0}&photo_id={1}"

    #iterate through flickr's xml response and extract needed information and place them into a dictionary
    for neighbor in root.iter('photo'):
        #### get individual photo info to extract number of comments from
        commentUrl = buildFlickrUrl(baseFlickrCommentsUrl,rc.GetApiKey(), neighbor.attrib['id'])
        commentRoot = flickrApiCall(commentUrl)
        ####

        commentCount = int(commentRoot.findall('.//comments')[0].text)

        #build image source url
        imgUrl = buildUrl(flickrImageUrl,neighbor)

        if commentCount in allPhotos:
            allPhotos[commentCount].append(imgUrl)
        else:
            allPhotos[commentCount] = [imgUrl]

    sortedPhotos = collections.OrderedDict(sorted(allPhotos.items(), reverse=True))

    return render_template('index.html', photos = sortedPhotos)

if __name__ == '__main__':
    app.run()
