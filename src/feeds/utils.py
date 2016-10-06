# -*- coding: utf-8 -*-
import requests
from django.conf import settings
import logging
from bs4 import BeautifulSoup


def download(url):
    '''Returns a JSON serializable dictionary with the following keys:
        - status_code
        - text
        - headers
        - url
    '''
    with requests.Session() as session:
        session.max_redirects = settings.MAX_FINAL_URL_TRIES

        response = session.get(
            url,
            headers={'user-agent': settings.CRAWLER_USER_AGENT},
            timeout=settings.CRAWLER_TIMEOUT
        )
        return {
            'status_code': response.status_code,
            'text': response.text,
            'headers': response.headers,
            'url': response.url
        }


def get_final_url(url, times_left=settings.MAX_FINAL_URL_TRIES):
    '''Loops over url until it doesn't change (e.g. feedburner or shortened)'''

    # Avoids recursive exaustion
    if times_left < 1:
        return url

    logging.debug(u'Checking final URL for {!r}'.format(url))
    try:
        post = download(url)
    except (requests.ConnectionError, requests.HTTPError):
        logging.error(u'Failed trying to download {!r}'.format(url))
        return url

    if url != post['url']:
        logging.info(u'Final URL for {!r} diverges from {!r}'.format(url, post['url']))
        # Try again until find a final URL (or tire out)
        return get_final_url(post['url'], times_left - 1)
    else:
        logging.debug(u'Post URL {!r} checked OK'.format(url))

    return post['url']


def get_sanitized_html(html):
    '''Fixes DOM and remove crap tags'''
    # html must be some kind of string
    if not isinstance(html, str):
        return html

    bs = BeautifulSoup(html, 'html.parser')
    for tag in bs.find_all():
        if tag.name in ('script', 'style', 'iframe', 'frame', 'frameset'):
            tag.extract()
            continue
        for attr, value in list(tag.attrs.items()):
            if tag.name == 'a' and attr == 'href':
                continue
            if tag.name == 'img' and attr == 'src':
                continue
            if tag.name == 'video' and attr == 'src':
                continue
            del tag[attr]
    html = bs.prettify()

    return html


def find_link_to_feed(html):
    '''Parses HTML and returns <link>s to feeds'''
    soup = BeautifulSoup(html, 'html.parser')
    content_types = ['application/rss+xml', 'application/atom+xml', 'application/rdf+xml']
    links = soup.find_all('link')
    for link in links:
        if link.get('type', '').lower().strip() in content_types:
            return link.get('href')
