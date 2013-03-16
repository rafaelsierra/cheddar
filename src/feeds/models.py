# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from base.models import BaseModel
from celery import task

from django.db.models.signals import post_save
from feeds.utils import feedopen
from feeds.tasks import update_site_feed, make_request
from feeds.signals import start_feed_update
import hashlib
from django.utils import timezone

class Site(BaseModel):
    '''
        Every site added by users goes here, 
        url is where you can find the HTML version of the site; 
        feed_url is the unique address where you can find the feed version of site; 
        and title, well, is the title
    '''
    url = models.URLField(null=True, blank=True)
    feed_url = models.URLField(unique=True) # No duplicated feed urls
    title = models.CharField(max_length=256, null=True, blank=True)
    
    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return unicode(self.id)
    
    
    def clean(self):
        # TODO: check if feed_url is a valid feed
        pass
    

    # I don't think update() would be a good name here
    def update_feed(self):
        # Celery has an contrib module to handle instance methods, but I've
        # never used it, so I don't know if we should trust if 
        update_site_feed.delay(self)
        
    
    def save(self, *args, **kwargs):
        '''Force model validation'''
        self.full_clean()
        super(Site, self).save(*args, **kwargs)
        
    
    def getfeed(self):
        '''Opens self.feed_url and parses it'''
        return feedopen(self.feed_url)

    
    def next_update_eta(self):
        '''Returns when this site should update again in seconds
        This is a pretty simple function to calculate the average time between
        posts.
        '''
        intervals = []
        for post in self.posts.all():
            # Checks if already have the desired intervals
            if len(intervals) >= settings.CHEDDAR_HISTORY_SIZE:
                break
            
            if not intervals:
                interval = timezone.now() - post.captured_at
                intervals.append(interval.days*3600 + interval.seconds)
                
            try:
                previous = post.get_previous_by_captured_at()
            except Post.DoesNotExist:
                # End of Posts
                break
            
            interval = post.captured_at - previous.captured_at
            intervals.append(interval.days*3600 + interval.seconds)
            
        # Put eta somewhere between min and max time
        if not intervals:
            return settings.MIN_UPDATE_INTERVAL_SECONDS
        
        eta = sum(intervals)/len(intervals)
        if eta < settings.MIN_UPDATE_INTERVAL_SECONDS:
            eta = settings.MIN_UPDATE_INTERVAL_SECONDS
        elif eta > settings.MAX_UPDATE_INTERVAL_SECONDS:
            eta = settings.MAX_UPDATE_INTERVAL_SECONDS
        return eta


class Post(BaseModel):
    site = models.ForeignKey(Site, related_name='posts')
    title = models.CharField(max_length=1024, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    author = models.CharField(max_length=64, null=True, blank=True)
    url = models.URLField(max_length=4096)
    url_hash = models.CharField(max_length=64, unique=True)
    
    # This field is used in forecasting next crawler date
    captured_at = models.DateTimeField(auto_now_add=True)
    
    @classmethod
    def hashurl(cls, url):
        return hashlib.sha256(url).hexdigest()
    
    def save(self, *args, **kwargs):
        # Sets uniqueness of this post
        if not self.url_hash:
            self.url_hash = Post.hashurl(self.url)
        return super(Post, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ('-created_at',)


# 
# Connecting signals
#
post_save.connect(start_feed_update, sender=Site, dispatch_uid='feeds.tasks.start_feed_update')
