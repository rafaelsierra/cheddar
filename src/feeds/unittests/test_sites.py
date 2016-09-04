from django.contrib.auth.models import User
from django.utils import timezone

import responses

from rest_framework.test import APITestCase

from feeds.models import Site

RSS_TEMPLATE = """
<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
 <title>RSS Title</title>
 <description>This is an example of an RSS feed</description>
 <link>http://www.example.com/main.html</link>
 <lastBuildDate>Mon, 06 Sep 2010 00:01:00 +0000 </lastBuildDate>
 <pubDate>Sun, 06 Sep 2009 16:20:00 +0000</pubDate>
 <ttl>1800</ttl>

 <item>
  <title>Example entry</title>
  <description>Here is some text containing an interesting description.</description>
  <link>http://www.example.com/blog/post/1</link>
  <guid isPermaLink="true">7bd204c6-1655-4c27-aeee-53f933c5395f</guid>
  <pubDate>Sun, 06 Sep 2009 16:20:00 +0000</pubDate>
 </item>

</channel>
</rss>
"""


class SitesTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='sdm', is_active=True)
        self.user.set_password('1234')
        self.user.save()
        self.client.login(username='sdm', password='1234')
        self.feed_url = 'http://somesite.com/somefeed.xml'

        responses.add(
            responses.GET,
            self.feed_url,
            body=RSS_TEMPLATE
        )

    def tearDown(self):
        self.user.delete()

    @responses.activate
    def test_subscribe_to_new_site(self):
        # Subscribe to a new site
        self.assertEqual(Site.objects.filter(feed_url=self.feed_url).count(), 0)
        response = self.client.post(
            '/v1/feeds/sites',
            {'feed_url': self.feed_url}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Site.objects.filter(feed_url=self.feed_url).count(), 1)
        self.assertIn('resource_url', response.data)

        # Checks if it is going to return on the list
        response = self.client.get('/v1/feeds/sites')
        self.assertEqual(response.data[0]['feed_url'], self.feed_url)

    @responses.activate
    def test_subscribe_to_existing_site(self):
        # Subscribe to a new site
        Site.objects.create(feed_url=self.feed_url, last_update=timezone.now(), next_update=timezone.now())
        self.assertEqual(Site.objects.filter(feed_url=self.feed_url).count(), 1)
        response = self.client.post(
            '/v1/feeds/sites',
            {'feed_url': self.feed_url}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Site.objects.filter(feed_url=self.feed_url).count(), 1)

        # Checks if it is going to return on the list
        response = self.client.get('/v1/feeds/sites')
        self.assertEqual(response.data[0]['feed_url'], self.feed_url)

    @responses.activate
    def test_unsubscribe_from_site(self):
        # Subscribe to a new site
        self.assertEqual(Site.objects.filter(feed_url=self.feed_url).count(), 0)
        response = self.client.post(
            '/v1/feeds/sites',
            {'feed_url': self.feed_url}
        )
        site_id = response.data['id']
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Site.objects.filter(feed_url=self.feed_url).count(), 1)

        # Unsubscribe from it
        self.client.delete(response.data['resource_url'])

        # It should not return in this list
        response = self.client.get('/v1/feeds/sites')
        self.assertEqual(response.data, [])

        # The site itself must remain
        self.assertEqual(Site.objects.get(id=site_id).id, site_id)

    @responses.activate
    def test_methods_not_allowed(self):
        site_response = self.client.post(
            '/v1/feeds/sites',
            {'feed_url': self.feed_url}
        )

        # PUT is not allowed
        response = self.client.put(
            site_response.data['resource_url'],
            {},
            status=405
        )
        self.assertEqual(response.status_code, 405)

        # So is PATCH
        response = self.client.patch(
            site_response.data['resource_url'],
            {},
            status=405
        )
        self.assertEqual(response.status_code, 405)

    def test_unsubscribe_from_not_subscribed(self):
        response = self.client.delete('/v1/feeds/sites/4', status=404)
        self.assertEqual(response.status_code, 404)
