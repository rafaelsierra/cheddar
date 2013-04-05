# -*- coding: utf-8 -*-
from base.models import BaseModel, BaseModelManager
from celery import task
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import time as timefilter, \
    date as datefilter
from django.utils import timezone
from django.utils.timezone import is_aware, utc
from feeds.signals import start_feed_update
from feeds.tasks import update_site_feed, make_request
from feeds.utils import feedopen
import base64
import celery
import datetime
import hashlib


class SiteManager(BaseModelManager):
    def need_update(self):
        '''Returns what sites needs update'''
        return self.get_query_set().filter(next_update__lte=timezone.now())
        

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
    # Control fields
    feed_errors = models.IntegerField(default=0) # TODO: Inactivate sites with to much errors
    last_update = models.DateTimeField()
    next_update = models.DateTimeField(auto_now_add=True, db_index=True)
    task_id = models.CharField(default='', blank=True, null=True, max_length=36)
    
    objects = SiteManager()
    
    class Meta:
        ordering = ('title',)
        index_together = [
            ['feed_errors', 'last_update'],
        ]        
    
    @property
    def task(self):
        '''Returns the current task running this site'''
        if not self.task_id:
            return None
        return update_site_feed.AsyncResult(self.task_id)
    
    
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

    
    def set_next_update(self, save=True):
        '''
        Calculates when this site should update again.
        
        This is a pretty simple function to calculate the average seconds between
        posts.
        '''
        intervals = []
        for post in self.posts.order_by('-captured_at'):
            # Checks if already have the desired intervals
            if len(intervals) >= settings.CHEDDAR_HISTORY_SIZE:
                break
            
            # I don't know if this is a good thing
            # Update: Turns out, it is
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
            
        self.next_update = timezone.now()+datetime.timedelta(seconds=eta)
        if save:
            self.save()
        return self.next_update
    

    def favicon(self):
        'TODO: This'



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
    
    def _get_userpost(self, user):
        # Cyclic import
        from accounts.models import UserPost
        return UserPost.objects.get_or_create(user=user, post=self)[0]
    
    def mark_field(self, user, field, value):
        '''Mark this post's field as `value`'''
        userpost = self._get_userpost(user)
        setattr(userpost, field, value)
        userpost.save()
        
    def mark_as_read(self, user):
        self.mark_field(user, 'is_read', True)
    
    def mark_as_unread(self, user):
        self.mark_field(user, 'is_read', False)
    
    def mark_as_starred(self, user):
        self.mark_field(user, 'is_starred', True)
    
    def mark_as_unstarred(self, user):
        '''Does "unstarred" even exists as word?'''
        self.mark_field(user, 'is_starred', False)

    def as_base64(self):
        return u'data:text/html;base64,{}'.format(base64.encodestring(self.content.encode('utf-8')))

    def captured_at_display(self):
        u'''Returns a prettier date format'''

        now = datetime.datetime.now(utc if is_aware(self.captured_at) else None)
        if self.captured_at < now:
            delta = now - self.captured_at
        else:
            delta = self.captured_at - now        
        
        if delta.days >= 1:
            return datefilter(self.captured_at)
        else:
            return timefilter(self.captured_at)
        
    
    class Meta:
        ordering = ('-created_at',)


# 
# Connecting signals
#
post_save.connect(start_feed_update, sender=Site, dispatch_uid='feeds.tasks.start_feed_update')
