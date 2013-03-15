# -*- coding: utf-8 -*-
from django.db import models
from base.models import BaseModel
from celery import task

from django.db.models.signals import post_save
from feeds.signals import update_site_data
from feeds.utils import urlopen

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
    
    def clean(self):
        # TODO: check if feed_url is a valid feed
        pass
    
    # I don't think update() would be a good name here
    def update_data(self):
        # TODO: Finish this
        urlopen(self.feed_url)
        
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super(Site, self).save(*args, **kwargs)


class Post(BaseModel):
    site = models.ForeignKey(Site, related_name='posts')
    title = models.CharField(max_length=1024)
    content = models.TextField()
    author = models.CharField(max_length=64)
    
    # Unfortunally not all feeds provide unique urls for each post, so we cannot
    # have a unique=True on this field
    url = models.URLField(max_length=256)
    
    # This field is used in forecasting next crawler date
    captured_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-created_at',)


# Signals
post_save.connect(update_site_data, sender=Site, dispatch_uid='feeds.Site.update_site_data')