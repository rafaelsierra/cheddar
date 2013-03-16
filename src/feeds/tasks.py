# -*- coding: utf-8 -*-
import feedparser
import celery
import urllib2
from celery.contrib import rdb
import ipdb
import logging

logger = logging.getLogger('feeds.tasks')

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


@celery.task()
def update_site_feed(site):
    '''This functions handles the feed update of site and is kind of recursive,
    since in the end it will call another apply_async onto himself'''
    feed = site.getfeed()
    # Updates this site info
    if not 'feed' in feed:
        logger.warn(u"Site {} feed did not returned feed information")
    else:
        info = feed['feed']
        if 'title' in info:
            site.title = info['title']
        if 'link' in info:
            site.url = info['link']
        site.save()
    