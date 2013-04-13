# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from feeds.views import HomeView, CheddarJSView, UserSiteList, UserPostList,\
    MarkPostAsRead, ImportSubscriptionsFormView, proxy_favicon, StarPost
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^proxy/site/(?P<pk>\d+)/favicon.ico$', proxy_favicon, name='proxy-favicon'),
    url(r'^my/sites/$', UserSiteList.as_view(), name='my-sites'),
    url(r'^my/sites/import/$', ImportSubscriptionsFormView.as_view(), name='import'),
    url(r'^my/sites/import/success/$', TemplateView.as_view(template_name='feeds/import-success.html'), name='import-success'),
    url(r'^my/posts/read/$', UserPostList.as_view(), name='post-list-read'),
    url(r'^my/posts/unread/$', UserPostList.as_view(), name='post-list-unread'),
    url(r'^my/posts/mark-as-read/$', MarkPostAsRead.as_view(), name='post-mark-as-read'),
    url(r'^my/posts/(?P<pk>.+)/star/$', StarPost.as_view(), name='post-star-it'),
    url(r'^cheddar.js', CheddarJSView.as_view(), name='cheddarjs'),
    
)