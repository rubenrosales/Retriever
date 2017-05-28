import requests
import urllib2
from bs4 import BeautifulSoup
import re
import json

#Purpose: extract info from Instagram's json response and place into dictionary
#In Param: dictionary of image urls and json response
#Returned: dictionary of image urls
def processTags(dict, strippedTags):
    for tag in strippedTags:
        commentCount = int(tag["comments"]["count"])
        if commentCount in dict:
            dict[commentCount].append(tag["display_src"])
        else:
            dict[commentCount] = [tag["display_src"]]
    return dict

#Purpose: make GET request to instagrams search page
#In Param: instagram url, tag
#Returned: response or error
def makeRequest(url, tag):
    request_headers = {
    "Accept-Language": "en-US,en;q=0.5",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    url = url.format(tag)
    req = urllib2.Request(url,headers=request_headers)
    try:
        return urllib2.urlopen(req)
    except URLError as e:
        print e.reason
        return e

#Purpose: extract json from instagram's html response
#In Param: html page
#Returned: json object extracted from html page
def extractJson(soup):
    data  = soup.find_all("script")[1].string
    json_string = data.split('window._sharedData =')[1]

    return json.loads(json_string.strip()[:-1])

#Purpose: main function, calls scraping functions and returns dictionary of image urls
#In Param: tag to search for
#Returned: dictionary of image urls
def scrape(tag):

    ##There's two different types of responses instagram will return
    ## 1. an html page containing all the images in html tags
    ## 2. a json object inside a script tag

    #### Handles first type of response
    #Comments info is not part of the html page so they are defaulted to zero
    imgUrls = {0:[]}
    url = 'https://www.instagram.com/explore/tags/{0}/'
    response = makeRequest(url, tag)
    the_page = response.read()

    returnedUrls = {}
    soup = BeautifulSoup(the_page, "html.parser")

    for link in soup.findAll("img", { "class" : "_icyx7" }):
        imgUrls[0].append(link.get('src'))
    ####

    ####Handles second type of response
    if not imgUrls[0]:
        json_obj = extractJson(soup)

        #IG separates their top posts and recent posts into 2 different objects
        topPostsStrippedTags = json_obj["entry_data"]["TagPage"][0]["tag"]["top_posts"]["nodes"]
        recentPostsStrippedTags = json_obj["entry_data"]["TagPage"][0]["tag"]["media"]["nodes"]

        returnedUrls = processTags(returnedUrls, topPostsStrippedTags)
        returnedUrls = processTags(returnedUrls, recentPostsStrippedTags)

        return returnedUrls
    ####

    return imgUrls
