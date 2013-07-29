# -*- coding: utf-8 -*-
import feedparser
import celery
import urllib2
from django.conf import settings
from feeds.tasks import make_request, parse_feed
import socket
import logging
import sgmllib
    

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


def get_final_url(url, times_left=settings.MAX_FINAL_URL_TRIES):
    '''Loops over url until it doesn't change (e.g. feedburner or shortened)'''
    
    # Avoids recursive exaustion
    if times_left < 1:
        return url
    
    logging.debug(u'Checking final URL for {}'.format(url))
    try:
        post = urllib2.urlopen(build_request(url), timeout=5)
    except (urllib2.URLError, urllib2.HTTPError, socket.error, socket.timeout), e:
        logging.exception(u'Failed trying to download {}'.format(url))
        return url
    
    if url != post.geturl():
        logging.info(u'Final URL for {} diverges from {}'.format(url, post.geturl()))
        # Try again until find a final URL (or tire out)
        return get_final_url(post.geturl(), times_left-1)
    else:
        logging.debug(u'Post URL {} checked OK'.format(url))
        
    return post.geturl()



class FindLinkToFeedParser(sgmllib.SGMLParser):
    '''Class to parse HTML content and get links to feeds'''
    feed_url = None
        
    def start_link(self, attributes):
        data = {'rel': None, 'type': None, 'href': None}
        content_types = ['application/rss+xml', 'application/atom+xml', 'application/rdf+xml']
        for att in attributes:
            if att[0] in data:
                data[att[0]] = att[1]
        
        if data['type'] in content_types:
            self.feed_url = data['href']
        