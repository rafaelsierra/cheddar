# -*- coding: utf-8 -*-
from celery.contrib import rdb
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.cache import cache
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.timezone import make_aware, get_current_timezone
from pytz.exceptions import AmbiguousTimeError
import celery
import datetime
import feedparser
import socket
import time
import urllib2

logger = get_task_logger(__name__)

SITE_WORKER_CACHE_KEY = u'site-worker-{id}'
CHECK_CACHE_KEY = 'check-sites-worker'

@celery.task()
def make_request(request):
    '''Makes the request and returns a tuple (response.getcode(), 
        response.info(), response.read())'''
    try:
        response = urllib2.urlopen(request, timeout=settings.CRAWLER_TIMEOUT)
    except (urllib2.HTTPError, urllib2.URLError, socket.timeout, socket.error), e:
        logger.error('Failed trying to download {}'.format(request.get_full_url()))
        return -1, None, u''
    
    tup = response.getcode(), response.info(), response.read(settings.CRAWLER_MAX_FEED_SIZE)
    response.close()
    return tup
    
    
@celery.task()
def parse_feed(rawdata):
    '''Parse the feed and returns whatever feedparser.parse returns'''
    if rawdata[0] < 0:
        # Error downloading feed
        return {'feed_error': True}
    result = feedparser.parse(rawdata[2])
    if result.bozo > 0:
        return {'feed_error': True}
    else:
        return result


@celery.task()
def update_site_feed(site):
    '''This functions handles the feed update of site and is kind of recursive,
    since in the end it will call another apply_async onto himself'''
    # Avoids running two instances at the time
    cachekey = SITE_WORKER_CACHE_KEY.format(id=site.id)
    if cache.get(cachekey):
        logger.warn('Worker for site {} still running'.format(site.id))
        return
    
    cache.add(cachekey, '1', 60) # Will not run again in 60 seconds        
    
    from feeds.models import Post
    # Update task_id for this site
    site.task_id = update_site_feed.request.id
    site.save()
    
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
            
            if 'published_parsed' in entry and entry.get('published_parsed'):
                created_at = datetime.datetime.fromtimestamp(time.mktime(entry['published_parsed']))
                try:
                    created_at = make_aware(created_at, get_current_timezone())
                except AmbiguousTimeError,e:
                    logger.error('Failed when tring to make {} aware'.format(created_at))
                    created_at = timezone.now()
            else:
                created_at = timezone.now()
               
            try: 
                post, created = site.posts.get_or_create(url_hash=Post.hashurl(url),
                    defaults={
                        'title': title,
                        'url': url,
                        'content': content,
                        'author': author,
                    }
                )
            except IntegrityError:
                # Raised when two posts have the same URL
                pass
            else:
                if created:
                    new_posts_found += 1
                post.created_at = created_at
                post.save()
    
        logger.info('Site {site_id} got {new} new posts from {total} in feed'.format(site_id=site.id, new=new_posts_found, total=len(feed['entries'])))
        
    # Updates when is it to run again
    next_update = site.set_next_update(save=False)
    logger.info("Site's {} next update at {}".format(site.id, next_update))
    site.last_update = timezone.now()
    site.save()    
    
    
@celery.task()
def check_sites_for_update():
    '''Check if site's crawler should run'''
    # Avoids running two instances at the time
    if cache.get(CHECK_CACHE_KEY):
        logger.warn('Worker for checking sites still running')
        return
    
    cache.add(CHECK_CACHE_KEY, '1', 3600) # Will not run again for 1 hour
    
    from feeds.models import Site
    sites = Site.objects.need_update()
        
    logger.info(u"There are {} sites that needs update".format(sites.count()))
    
    for site in sites:
        if not site.task or site.task.status in (u'SUCCESS', u'FAILURE', u'REVOKED'):
            logger.warn('Starting task for site {}'.format(site.id))
            site.update_feed()
        else:
            logger.warn('Tried to start another task for site {} but status is {}'.format(site.id, site.task.status))
            if site.last_update < timezone.now()-settings.MAX_UPDATE_WAIT:
                logger.error('Site {} has been running for more time than allowed, revoking task to start another next time'.format(site.id))
                # Revoke site's task and clear its task_id
                site.task.revoke()
                site.task_id = None
                site.save()
    
    cache.delete(CHECK_CACHE_KEY)
    
    
