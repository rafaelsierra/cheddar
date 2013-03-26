# -*- coding: utf-8 -*-
from django.views.generic.list import MultipleObjectMixin
from feeds.models import Post, Site
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from accounts.models import UserSite


class FeedListMixin(MultipleObjectMixin):
    u'''Exactly like MultipleObjectMixin but applies the rules for users and
    works only for feeds, you need to write your own rendering methods
    
    post_read - defines if the queryset returns a list of read or unread posts
        for the user
    
    '''
    
    model = Post
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MultipleObjectMixin, self).dispatch(*args, **kwargs)
    
    def get_queryset(self):
        '''Returns a queryset with the list of user's posts'''
        if self.post_read:
            posts = UserSite.posts.read(self.request.user)
        else:
            posts= UserSite.posts.unread(self.request.user)
            
        return posts
        
        
