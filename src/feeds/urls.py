# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from feeds.views import HomeView, CheddarJSView, UserSiteList, UserPostList,\
    MarkPostAsRead

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='register'),
    url(r'^my/sites/$', UserSiteList.as_view(), name='my-sites'),
    url(r'^my/posts/read/$', UserPostList.as_view(), name='post-list-read'),
    url(r'^my/posts/unread/$', UserPostList.as_view(), name='post-list-unread'),
    url(r'^my/posts/mark-as-read/$', MarkPostAsRead.as_view(), name='post-mark-as-read'),
    url(r'^cheddar.js', CheddarJSView.as_view(), name='cheddarjs'),
    
)