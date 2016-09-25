import datetime
import json
import logging
import time

from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import Site, Post

logger = logging.getLogger('feeds.serializers')


# From http://stackoverflow.com/questions/28473073/python-how-to-pass-feedparser-object-to-a-celery-task
class FeedContentEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, time.struct_time):
            epoch = int(time.mktime(obj))
            return {'__type__': '__time__', 'time': epoch}
        else:
            return super(FeedContentEncoder, self).default(obj)


def decode_feed_content(obj):
    if isinstance(obj, dict) and '__type__' in obj:
        if obj['__type__'] == '__time__':
            return datetime.datetime.fromtimestamp(obj['time']).timetuple()
    return obj


def feed_content_json_dumps(obj):
    return json.dumps(obj, cls=FeedContentEncoder)


def feed_content_json_loads(obj):
    if isinstance(obj, str):
        return json.loads(obj, object_hook=decode_feed_content)
    elif isinstance(obj, bytes):
        return feed_content_json_loads(obj.decode('utf-8'))
    else:
        logger.error('Received some weird content to decode: {!r}'.format(obj))


class SiteSerializer(serializers.ModelSerializer):
    resource_url = serializers.SerializerMethodField()

    def get_resource_url(self, obj):
        return reverse('sites-detail', kwargs={'pk': obj.id})

    class Meta:
        model = Site
        fields = ('id', 'resource_url', 'url', 'feed_url', 'title', 'last_update')
        read_only_fields = ('id', 'url', 'title', 'last_update', 'resource_url')


class SiteAddSerializer(serializers.Serializer):
    feed_url = serializers.URLField()


class PostSerializer(serializers.ModelSerializer):
    resource_url = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    is_shared = serializers.SerializerMethodField()
    date = serializers.DateTimeField(source='captured_at')
    site = serializers.HyperlinkedRelatedField(read_only=True, view_name='sites-detail')

    userpost = None

    def get_resource_url(self, obj):
        return reverse('posts-detail', kwargs={'pk': obj.id})

    def get_userpost(self, obj):
        # TODO: Stop hitting database for each post
        if not self.userpost:
            self.userpost = obj.userpost.get_or_create(user=self.context['request'].user)[0]
        return self.userpost

    def get_is_read(self, obj):
        return self.get_userpost(obj).is_read

    def get_is_starred(self, obj):
        return self.get_userpost(obj).is_starred

    def get_is_shared(self, obj):
        return self.get_userpost(obj).is_shared

    class Meta:
        model = Post
        fields = (
            'id',
            'resource_url',
            'site',
            'title',
            'content',
            'author',
            'is_read',
            'date',
            'is_starred',
            'is_shared',
        )
