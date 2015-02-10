# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from feeds.views import HomeView, UserSiteList, MarkPostAsRead, \
    ImportSubscriptionsFormView, proxy_favicon, StarPost, MarkAllAsRead
from accounts.views import UnsubscribeFeed

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^my/posts/all/$', HomeView.as_view(), {'filtering': 'all'}, name='post-list-all'),    
    url(r'^my/posts/read/$', HomeView.as_view(), {'filtering': 'read'}, name='post-list-read'),
    url(r'^my/posts/unread/$', HomeView.as_view(), {'filtering': 'unread'}, name='post-list-unread'),
    url(r'^my/posts/starred/$', HomeView.as_view(), {'is_starred':True}, name='post-list-starred'),
    
    url(r'^sites/(?P<site>\d+)/read/$', HomeView.as_view(), {'is_read':False}, name='post-list-unread'),
    
    url(r'^proxy/site/(?P<pk>\d+)/favicon.ico$', proxy_favicon, name='proxy-favicon'),
    url(r'^my/sites/$', UserSiteList.as_view(), name='my-sites'),
    url(r'^my/sites/subscribe/$', UserSiteList.as_view(), name='subscribe'),
    url(r'^my/sites/unsubscribe/$', UnsubscribeFeed.as_view(), name='unsubscribe'),
    url(r'^my/sites/import/$', ImportSubscriptionsFormView.as_view(), name='import'),
    url(r'^my/sites/import/success/$', TemplateView.as_view(template_name='feeds/import-success.html'), name='import-success'),
    
    url(r'^my/posts/mark-as-read/$', MarkPostAsRead.as_view(), name='post-mark-as-read'),
    url(r'^my/posts/mark-all-as-read/$', MarkAllAsRead.as_view(), name='post-mark-all-as-read'),
    url(r'^my/posts/(?P<pk>.+)/star/$', StarPost.as_view(), name='post-star-it'),
)