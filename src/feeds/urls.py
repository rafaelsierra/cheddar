# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from feeds.views import FeedsListView

urlpatterns = patterns('',
    url('^$', FeedsListView.as_view(), name='register'),
    
)