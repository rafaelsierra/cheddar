# -*- coding: utf-8 -*-
from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import User
from feeds.models import Site, Post


class Folder(BaseModel):
    user = models.ForeignKey(User, related_name='folders')
    name = models.CharField(max_length=32)

    class Meta:
        ordering = ('name', )


class UserSite(BaseModel):
    user = models.ForeignKey(User, related_name='my_sites')
    site = models.ForeignKey(Site, related_name='usersite')
    folder = models.ForeignKey(Folder, null=True, blank=True, related_name='usersite')

    class Meta:
        unique_together = (('user', 'site'),)


class UserPost(BaseModel):
    user = models.ForeignKey(User, related_name='my_posts')
    post = models.ForeignKey(Post, related_name='userpost')
    is_read = models.BooleanField(default=False, db_index=True)
    is_starred = models.BooleanField(default=False, db_index=True)
    is_shared = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = (('user', 'post'),)
