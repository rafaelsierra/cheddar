from django.contrib.auth.models import User

import responses

from rest_framework.test import APITestCase

from feeds.models import Post, Site

RSS_TEMPLATE = """
<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
 <title>RSS Title</title>
 <description>This is an example of an RSS feed</description>
 <link>{site_url}</link>
 <lastBuildDate>Mon, 06 Sep 2010 00:01:00 +0000 </lastBuildDate>
 <pubDate>Sun, 06 Sep 2009 16:20:00 +0000</pubDate>
 <ttl>1800</ttl>

 <item>
  <title>Example entry</title>
  <description>Here is some text containing an interesting description.</description>
  <link>{post_url}</link>
  <pubDate>Sun, 06 Sep 2009 16:20:00 +0000</pubDate>
 </item>

</channel>
</rss>
"""


class PostsTestCase(APITestCase):
    @responses.activate
    def setUp(self):
        self.user = User.objects.create(username='sdm', is_active=True)
        self.user.set_password('1234')
        self.user.save()
        self.client.login(username='sdm', password='1234')
        self.feed_url = 'http://somesite.com/somefeed.xml'

        responses.add(
            responses.GET,
            self.feed_url,
            body=RSS_TEMPLATE.format(site_url=self.feed_url, post_url=self.feed_url)
        )
        # Subscribe to this feed
        self.client.post(
            '/v1/feeds/sites',
            {'feed_url': self.feed_url}
        )

        # Add some posts to an unsubscribed site
        responses.add(
            responses.GET,
            'http://someothersite.com/feed.xml',
            body=RSS_TEMPLATE.format(site_url='http://someothersite.com/feed.xml', post_url='http://someothersite.com/feed.xml')
        )
        Site.objects.create(
            feed_url='http://someothersite.com/feed.xml',
            next_update='1970-01-01',
            last_update='1970-01-01'
        )

    def tearDown(self):
        self.user.delete()
        Post.objects.all().delete()
        Site.objects.all().delete()

    def test_post_indexing(self):
        # Subscribe to a new site
        self.assertEqual(Post.objects.filter(site__feed_url=self.feed_url).count(), 1)

    def test_list_all_posts(self):
        response = self.client.get('/v1/feeds/posts')
        self.assertEqual(response.status_code, 200)

        # There should be 2 posts on database and 1 on the API
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(len(response.data['results']), 1)

        # Checks post data
        post = response.data['results'][0]
        self.assertFalse(post['is_read'])
        self.assertFalse(post['is_shared'])
        self.assertFalse(post['is_starred'])
        site = self.client.get(post['site'])
        self.assertEqual(site.data['title'], 'RSS Title')
