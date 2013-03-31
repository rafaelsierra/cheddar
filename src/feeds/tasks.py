# -*- coding: utf-8 -*-
from celery.contrib import rdb
from django.conf import settings
import celery
import datetime
import feedparser
import ipdb
import logging
import socket
import time
import urllib2

logger = logging.getLogger('feeds.tasks')

@celery.task()
def make_request(request):
    '''Makes the request and returns a tuple (response.getcode(), 
        response.info(), response.read())'''
    try:
        response = urllib2.urlopen(request, timeout=settings.CRAWLER_TIMEOUT)
    except (urllib2.HTTPError, urllib2.URLError, socket.timeout), e:
        logger.error('Failed trying to download {}'.format(request.get_full_url()))
        return -1, None, u''
    
    return response.getcode(), response.info(), response.read()
    
    
@celery.task()
def parse_feed(rawdata):
    '''Parse the feed and returns whatever feedparser.parse returns'''
    if rawdata[0] < 0:
        # Error downloading feed
        return {'feed_error': True}
    return feedparser.parse(rawdata[2])


@celery.task()
def update_site_feed(site):
    '''This functions handles the feed update of site and is kind of recursive,
    since in the end it will call another apply_async onto himself'''
    from feeds.models import Post 
    feed = site.getfeed()
    # Update this site info
    if not 'feed' in feed:
        logger.warn(u"Site {} feed did not returned feed information".format(site.id))
        if 'feed_error' in feed:
            logger.error('Site {} is with its feed url broken'.format(site.id))
            # TODO: Create a task to use site.url to discover its new feed location
            site.feed_errors += 1
            site.save()
    else:
        info = feed['feed']
        if 'title' in info:
            site.title = info['title']
        if 'link' in info:
            site.url = info['link']
        if site.feed_errors > 0:
            site.feed_errors = 0
        site.save()

    # Create posts
    if not 'entries' in feed:
        logger.warn(u"Site {} feed did not returned any post".format(site.id))
    else:
        new_posts_found = 0
        for entry in feed['entries']:
            # Without link we can't save this post
            if not 'link' in entry:
                continue
            url = entry['link']
            title = entry.get('title', '')
            
            # Try to get content
            if isinstance(entry.get('content'), list):
                try:
                    for content in entry['content']:
                        if content:
                            break
                except IndexError:
                    content = u''
            else:
                content = entry.get('content')
                
            if not content and 'description' in entry:
                content = entry['description']
                
                
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
            if created:
                new_posts_found += 1
            post.created_at = created_at
            post.save()
    
        logger.info('Site {site_id} got {new} new posts from {total} in feed'.format(site_id=site.id, new=new_posts_found, total=len(feed['entries'])))
        
    # Schedule the next update
    update_site_feed.apply_async(args=(site,), countdown=site.next_update_eta())