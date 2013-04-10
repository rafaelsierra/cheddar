# -*- coding: utf-8 -*-
import feedparser
import celery
import urllib2
from django.conf import settings
from feeds.tasks import make_request, parse_feed
    

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