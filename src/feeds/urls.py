# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from feeds.views import HomeView, CheddarJSView, UserSiteList

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='register'),
    url(r'^my/sites/$', UserSiteList.as_view(), name='my-sites'),
    url(r'^cheddar.js', CheddarJSView.as_view(), name='cheddarjs'),
    
)