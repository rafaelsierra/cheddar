# -*- coding: utf-8 -*-
import feedparser
import celery
import urllib2


@celery.task()
def make_request(request):
    '''Makes the request and returns a tuple (response.getcode(), 
        response.info(), response.read())'''
    response = urllib2.urlopen(request)
    return response.getcode(), response.info(), response.read()
    
    
@celery.task()
def parse_feed(rawdata):
    '''Parse the feed and returns whatever feedparser.parse returns'''
    return feedparser.parse(rawdata[2])
    