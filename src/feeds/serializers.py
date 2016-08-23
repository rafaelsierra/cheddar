import json
import time
import types
import datetime


# From http://stackoverflow.com/questions/28473073/python-how-to-pass-feedparser-object-to-a-celery-task
class FeedContentEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, time.struct_time):
            epoch = int(time.mktime(obj))
            return {'__type__': '__time__', 'time': epoch}
        else:
            return json.FeedContentEncoder.default(self, obj)

        if isinstance(obj, unicode):
            return obj.encode('utf-8')


def decode_feed_content(obj):
    if isinstance(obj, types.DictionaryType) and '__type__' in obj:
        if obj['__type__'] == '__time__':
            return datetime.datetime.fromtimestamp(obj['time']).timetuple()
    return obj


def feed_content_json_dumps(obj):
    return json.dumps(obj, cls=FeedContentEncoder)


def feed_content_json_loads(obj):
    return json.loads(obj, object_hook=decode_feed_content)
