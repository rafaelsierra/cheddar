# -*- coding: utf-8 -*-
from django.db import models
from base.models import BaseModel

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
    
    class Meta:
        ordering = ('-created_at',)
