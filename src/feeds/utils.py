# -*- coding: utf-8 -*-
import feedparser
import celery
import urllib2
from django.conf import settings
from feeds.tasks import make_request, parse_feed
import socket
import logging
    

def build_request(url):
    '''Returns a urllib2.Request instance to urlopen'''
    request = urllib2.Request(url)
    request.add_header('User-Agent', settings.CRAWLER_USER_AGENT)
    return request
    

def feedopen(url):
    request = build_request(url)
    # TODO: This is not working as I expected. I'm having lots of worker 
    # deadlocks and I think this granularity is the cause
    # http://docs.celeryproject.org/en/latest/userguide/tasks.html#avoid-launching-synchronous-subtasks
    #chain = make_request.s(request)|parse_feed.s()
    feed = parse_feed(make_request(request))
    return feed


def get_final_url(url):
    '''Loops over url until it doesn't change (e.g. feedburner or shortened)'''
    logging.debug(u'Checking final URL for {}'.format(url))
    try:
        post = urllib2.urlopen(build_request(url), timeout=5)
    except (urllib2.URLError, urllib2.HTTPError, socket.error, socket.timeout), e:
        logging.exception(u'Failed trying to download {}'.format(url))
        return url
    
    if url != post.geturl():
        logging.info(u'Final URL for {} diverges from {}'.format(url, post.geturl()))
    else:
        logging.debug(u'Post URL {} checked OK'.format(url))
        
    return post.geturl()