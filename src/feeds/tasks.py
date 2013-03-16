# -*- coding: utf-8 -*-
import feedparser
import celery
import urllib2
from celery.contrib import rdb
import ipdb
import logging
import datetime
import time

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
    from feeds.models import Post #
    
    feed = site.getfeed()
    # Update this site info
    if not 'feed' in feed:
        logger.warn(u"Site {} feed did not returned feed information".format(site.id))
    else:
        info = feed['feed']
        if 'title' in info:
            site.title = info['title']
        if 'link' in info:
            site.url = info['link']
        site.save()

    # Create posts
    if not 'entries' in feed:
        logger.warn(u"Site {} feed did not returned any post".format(site.id))
    else:
        for entry in feed['entries']:
            # Without link we can't save this post
            if not 'link' in entry:
                continue
            url = entry['link']
            title = entry.get('title', '')
            
            # Try to get content
            if isinstance(entry.get('content'), list):
                try:
                    content = entry.get('content')[0]
                except IndexError:
                    content = u''
            else:
                content = entry.get('content')
                
            if isinstance(content, dict):
                content = content.get('value')
                
            author = entry.get('author')
            
            if 'published_parsed' in entry:
                created_at = datetime.datetime.fromtimestamp(time.mktime(entry['published_parsed']))
            
            post, created = site.posts.get_or_create(url_hash=Post.hashurl(url),
                defaults={
                    'title': title,
                    'url': url,
                    'content': content,
                    'author': author,
                }
            )
            post.created_at = created_at
            post.save()
            
    # Schedule the next update
    update_site_feed.apply_async(args=(site,), countdown=site.next_update_eta())