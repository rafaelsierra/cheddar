# -*- coding: utf-8 -*-
from django.db import models
from base.models import BaseModel, BaseModelManager
from django.contrib.auth.models import User
from feeds.models import Site, Post
from django.db.models import Q

# TODO: Enforce User.email uniqueness


class UserSitePostsManager(BaseModelManager):
    def user_posts(self, user, is_read=None, is_all=None):
        '''Avoid using user_posts directly, use unread or read instead'''
        if not is_all: # False or None is enough
            if is_read is None: # This "None" is used in its true meaning
                query = Q(userpost__user=user)
            else:
                query = Q(userpost__user=user, userpost__is_read=is_read) | Q(userpost__user__isnull=True)
        else:
            query = Q() # Just don't apply any filter

        return Post.objects.filter(
            query,
            site__usersite__user=user,
        )

    def starred(self, user):
        return self.user_posts(user, None).filter(userpost__is_starred=True)

    def unread(self, user):
        return self.user_posts(user, False)

    def read(self, user):
        return self.user_posts(user, True).filter(userpost__is_read=True)

    def all(self, user):
        return self.user_posts(user, is_all=True)


class Folder(BaseModel):
    user = models.ForeignKey(User, related_name='folders')
    name = models.CharField(max_length=32)

    class Meta:
        ordering = ('name', )


class UserSite(BaseModel):
    user = models.ForeignKey(User, related_name='my_sites')
    site = models.ForeignKey(Site, related_name='usersite')
    folder = models.ForeignKey(Folder, null=True, blank=True, related_name='usersite')

    objects = BaseModelManager()
    posts = UserSitePostsManager()

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
