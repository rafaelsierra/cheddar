# -*- coding: utf-8 -*-
import feedparser
import celery
import urllib2
from django.conf import settings
from feeds.tasks import make_request, parse_feed
    
def urlopen(url):
    request = urllib2.Request(url)
    request.add_header('User-Agent', settings.CRAWLER_USER_AGENT)
    # http://docs.celeryproject.org/en/latest/userguide/tasks.html#avoid-launching-synchronous-subtasks
    chain = make_request.s(request)|parse_feed.s()
    #feed = chain().get()    
    import ipdb;ipdb.set_trace()