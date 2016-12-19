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

OGLAF_RSS_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0"><channel><title>Oglaf! -- Comics. Often dirty.</title><link>http://oglaf.com/latest/</link><description>Comics. Often dirty. Updates Sundays.</description><atom:link href="http://oglaf.com/feeds/rss/" rel="self"></atom:link><language>en-us</language><lastBuildDate>Sun, 04 Dec 2016 18:54:12 -0000</lastBuildDate><item><title>Apocrypha</title><link>http://oglaf.com/apocrypha/</link><description>&lt;div style="display:block; background-color: #ccc;"&gt;&lt;p&gt;&lt;img src="http://media.oglaf.com/story/ttapocrypha.gif" /&gt;&lt;/p&gt;&lt;p&gt;&lt;a href="http://oglaf.com/apocrypha/"&gt;&lt;img src="http://media.oglaf.com/archive/arc-apocrypha.png" width="400" height="100" border="0" alt="http://oglaf.com/apocrypha/" /&gt;&lt;/a&gt;&lt;/p&gt;&lt;/div&gt;</description><guid>http://oglaf.com/apocrypha/</guid></item><item><title>The Rack</title><link>http://oglaf.com/therack/</link><description>&lt;div style="display:block; background-color: #ccc;"&gt;&lt;p&gt;&lt;img src="http://media.oglaf.com/story/tttherack.gif" /&gt;&lt;/p&gt;&lt;p&gt;&lt;a href="http://oglaf.com/therack/"&gt;&lt;img src="http://media.oglaf.com/archive/arc-therack.png" width="400" height="100" border="0" alt="http://oglaf.com/therack/" /&gt;&lt;/a&gt;&lt;/p&gt;&lt;/div&gt;</description><guid>http://oglaf.com/therack/</guid></item></channel></rss>
"""


class OglafTestCase(APITestCase):
    @responses.activate
    def setUp(self):
        self.user = User.objects.create(username='sdm', is_active=True)
        self.user.set_password('1234')
        self.user.save()
        self.client.login(username='sdm', password='1234')
        self.feed_url = 'http://oglaf.com/feeds/rss/'

        responses.add(
            responses.GET,
            self.feed_url,
            body=OGLAF_RSS_TEMPLATE
        )
        # Subscribe to this feed
        self.client.post(
            '/v1/feeds/sites',
            {'feed_url': self.feed_url}
        )
        self.site = Site.objects.get(feed_url=self.feed_url)

    def tearDown(self):
        self.user.delete()
        Post.objects.all().delete()
        Site.objects.all().delete()

    def test_content_must_not_be_empty(self):
        # Every post in this feed has a content, as weird as it is, it is still a content
        for post in self.site.posts.all():
            self.assertIn('img', post.content)


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

    def test_patch_post(self):
        # Marks a post as read
        response = self.client.get('/v1/feeds/posts')
        post = response.data['results'][0]
        response = self.client.patch(
            post['resource_url'],
            {'is_read': True}
        )
        self.assertEqual(response.status_code, 200)

        # Stars the post
        response = self.client.patch(
            post['resource_url'],
            {'is_starred': True}
        )
        self.assertEqual(response.status_code, 200)

        # Checks if the changes were saved
        response = self.client.get(post['resource_url'])
        self.assertTrue(response.data['is_read'])
        self.assertTrue(response.data['is_starred'])
        self.assertFalse(response.data['is_shared'])

        # Marks the post as unread
        response = self.client.patch(
            post['resource_url'],
            {'is_read': False}
        )
        self.assertEqual(response.status_code, 200)

        # Checks if the changes were saved
        response = self.client.get(post['resource_url'])
        self.assertFalse(response.data['is_read'])
