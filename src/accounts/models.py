# -*- coding: utf-8 -*-
from django.db import models
from base.models import BaseModel, BaseModelManager
from django.contrib.auth.models import User
from feeds.models import Site, Post
from django.db.models import Q

# TODO: Make User.email unique

class UserSitePostsManager(BaseModelManager):
    def user_posts(self, user, is_read):
        '''Avoid using user_posts directly, use unread or read instead'''
        return Post.objects.filter(
            Q(userpost__user=user, userpost__is_read=is_read)|Q(userpost__user__isnull=True),
            site__usersite__user=user,
        )
        
    def unread(self, user):
        return self.user_posts(user, False)
    
    def read(self, user):
        return self.user_posts(user, True).filter(userpost__is_read=True)
            

class Folder(BaseModel):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=32)
    

class UserSite(BaseModel):
    user = models.ForeignKey(User, related_name='my_sites')
    site = models.ForeignKey(Site, related_name='usersite')
    folder = models.ForeignKey(Folder, null=True, blank=True)
    
    posts = UserSitePostsManager()
    
    class Meta:
        unique_together = (('user', 'site'),)
        
        
class UserPost(BaseModel):
    user = models.ForeignKey(User, related_name='my_posts')
    post = models.ForeignKey(Post, related_name='userpost')
    is_read = models.BooleanField(default=False, db_index=True)
    is_starred = models.BooleanField(default=False, db_index=True)
    
    class Meta:
        unique_together = (('user', 'post'),)
    