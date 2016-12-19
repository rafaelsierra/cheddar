# -*- coding: utf-8 -*-
import requests
import datetime
import time

import celery
import feedparser
from pytz.exceptions import AmbiguousTimeError

from celery.utils.log import get_task_logger
from django.conf import settings
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.timezone import make_aware, get_current_timezone

from feeds.utils import download
logger = get_task_logger(__name__)


SITE_WORKER_CACHE_KEY = u'site-worker-{id}'
CHECK_CACHE_KEY = 'check-sites-worker'


@celery.task()
def make_request(url):
    '''Open the URL and returns a tuple with:
        (
            status_code
            headers,
            text
        )

    This function is basically a celery task for the download utility
    '''
    try:
        response = download(url)
    except (requests.ConnectionError, requests.HTTPError) as error:
        logger.error('Failed trying to download {}: {!r}'.format(url, error))
        return -1, None, ''

    return [response['status_code'], dict(response['headers']), response['text']]


@celery.task()
def parse_feed(rawdata):
    '''Parse the feed and returns whatever feedparser.parse returns'''
    if rawdata[0] < 0:
        # Error downloading feed
        logger.error('Cannot parse feed because HTTP status code is invalid')
        return {'feed_error': True}
    result = feedparser.parse(rawdata[2].strip())
    if result.bozo > 0 and not result.entries:
        return {'feed_error': True}
    else:
        return result


@celery.task()
def update_site_feed(feed, site_id):
    '''This functions handles the feed update of site and is kind of recursive,
    since in the end it will call another apply_async onto himself'''
    from feeds.models import Post, Site
    from feeds.utils import get_final_url
    from feeds.utils import get_sanitized_html
    # Avoids running two instances at the time
    # Update task_id for this site
    site = Site.objects.get(id=site_id)
    site.task_id = update_site_feed.request.id
    site.save()

    # Update this site info
    if 'feed' not in feed:
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

        # For some reason, some Google Alerts returns a not valid FQDN info after parsed
        # and then we must check if it starts with "http"
        if 'link' in info and info['link'].startswith('http'):
            site.url = info['link']
        if site.feed_errors > 0:
            site.feed_errors = 0
        site.save()

    # Create posts
    if 'entries' not in feed:
        logger.warn(u"Site {} feed did not returned any post".format(site.id))
    else:
        new_posts_found = 0
        for entry in feed['entries']:
            # Without link we can't save this post
            if 'link' not in entry:
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
            # Parses the content to avoid broken HTML and script tags
            content = get_sanitized_html(content)

            author = entry.get('author')

            if 'published_parsed' in entry and entry.get('published_parsed'):
                created_at = datetime.datetime.fromtimestamp(time.mktime(entry['published_parsed']))
                try:
                    created_at = make_aware(created_at, get_current_timezone())
                except AmbiguousTimeError:
                    logger.error('Failed when tring to make {} aware'.format(created_at))
                    created_at = timezone.now()
            else:
                created_at = timezone.now()

            try:
                post, created = site.posts.get_or_create(
                    url_hash=Post.hashurl(url),
                    defaults={
                        'title': title,
                        'url': url,
                        'content': content,
                        'author': author,
                    }
                )
            except IntegrityError:
                # Raised when two posts have the same URL
                logger.warn('Final URL {} is duplicated'.format(url))
                pass
            else:
                if created:
                    new_posts_found += 1
                post.created_at = created_at
                post.save()

        logger.info(
            'Site {site_id} got {new} new posts from {total} in feed'.format(
                site_id=site.id,
                new=new_posts_found,
                total=len(feed['entries'])
            )
        )

    # Updates when is it to run again
    next_update = site.set_next_update(save=False)
    logger.info("Site's {} next update at {}".format(site.id, next_update))
    site.last_update = timezone.now()
    site.save()


@celery.task()
def check_sites_for_update():
    '''Check if site's crawler should run'''
    from feeds.models import Site
    sites = Site.objects.need_update()

    logger.info(u"There are {} sites that needs update".format(sites.count()))

    for site in sites:
        # Checks if this site was put to run recently
        if not site.task or site.task.status in (u'SUCCESS', u'FAILURE', u'REVOKED'):
            logger.warn('Starting task for site {}'.format(site.id))
            site.last_update = timezone.now()
            site.save()
            site.update_feed()
        else:
            logger.warn('Tried to start another task for site {} but status is {}'.format(site.id, site.task.status))
            if site.last_update < (timezone.now() - settings.MAX_UPDATE_WAIT):
                logger.error('Site {} has been running for more time than allowed, revoking task to start another next time'.format(site.id))
                # Revoke site's task and clear its task_id
                site.task.revoke()
                site.task_id = None
                site.save()
