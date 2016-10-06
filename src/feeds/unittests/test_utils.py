import unittest
import responses

from feeds.utils import download
from feeds.utils import find_link_to_feed
from feeds.utils import get_final_url
from feeds.utils import get_sanitized_html


class DownloadTestCase(unittest.TestCase):
    @responses.activate
    def test_download(self):
        responses.add(
            responses.GET,
            'http://cheddr.net/',
            body='success',
            content_type='text/plain',
            status=200
        )
        response = download('http://cheddr.net/')
        assert response['status_code'] == 200
        assert response['text'] == 'success'
        assert response['headers']['Content-Type'] == 'text/plain'


class FindLinkToFeedTestCase(unittest.TestCase):
    def test_find_link_to_feed_with_link(self):
        html = """<html><head><link rel="alternate" type="application/atom+xml" href="a"></head></html>"""
        assert find_link_to_feed(html) == "a"

    def test_find_link_to_feed_without_href(self):
        html = """<html><head><link rel="alternate" type="application/atom+xml"></head></html>"""
        assert not find_link_to_feed(html)

    def test_find_link_to_feed_without_link(self):
        html = """<html><head><link rel="stylesheet" href="foo.css" ></head></html>"""
        assert not find_link_to_feed(html)

    def test_find_link_to_feed_without_html(self):
        html = """this is totally not html \xe0 \x00>"""
        assert not find_link_to_feed(html)


class GetFinalUrlTestCase(unittest.TestCase):
    @responses.activate
    def test_get_final_url(self):
        responses.add(
            responses.GET,
            'http://cheddr.net/',
            status=302,
            adding_headers={'Location': '/login'}
        )
        responses.add(
            responses.GET,
            'http://cheddr.net/login',
            status=200,
            body='login'
        )
        final_url = get_final_url('http://cheddr.net/')
        self.assertEqual(final_url, 'http://cheddr.net/login')


class GetSatanizedHtmlTestCase(unittest.TestCase):
    def test_prettified_html(self):
        ugly_html = """<p>Hello <b>world!</p>"""
        pretty_html = get_sanitized_html(ugly_html)
        self.assertEqual(pretty_html, """<p>\n Hello\n <b>\n  world!\n </b>\n</p>""")

    def test_sanitized_html(self):
        ugly_html = """<script>rm -Rf /</script><style>color: black</style>Oh"""
        pretty_html = get_sanitized_html(ugly_html)
        self.assertEqual(pretty_html, """Oh\n""")
