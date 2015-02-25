# -*- coding: utf-8 -*-
import feedparser
import celery
import urllib2
from django.conf import settings
from feeds.tasks import make_request, parse_feed
import socket
import logging
import sgmllib
from bs4 import BeautifulSoup


def build_request(url):
    '''Returns a urllib2.Request instance to urlopen'''
    request = urllib2.Request(url)
    request.add_header('User-Agent', settings.CRAWLER_USER_AGENT)
    return request
    
    

def get_final_url(url, times_left=settings.MAX_FINAL_URL_TRIES):
    '''Loops over url until it doesn't change (e.g. feedburner or shortened)'''
    
    # Avoids recursive exaustion
    if times_left < 1:
        return url
    
    logging.debug(u'Checking final URL for {}'.format(url))
    try:
        post = urllib2.urlopen(build_request(url), timeout=settings.CRAWLER_TIMEOUT)
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



def get_sanitized_html(html):
    '''Fixes DOM and remove crap tags'''
    # html must be some kind of string 
    if not isinstance(html, basestring):
        return html
    
    bs = BeautifulSoup(html)
    for tag in ('script', 'style'):
        for item in bs.findAll(tag):
            item.extract()
    html = bs.prettify()
    
    return html



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
        