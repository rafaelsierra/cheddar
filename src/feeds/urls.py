# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from feeds.views import HomeView, UserSiteList, MarkPostAsRead, \
    ImportSubscriptionsFormView, proxy_favicon, StarPost, MarkAllAsRead

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^my/posts/read/$', HomeView.as_view(), {'is_read':True}, name='post-list-read'),
    url(r'^my/posts/unread/$', HomeView.as_view(), {'is_read':False}, name='post-list-unread'),
    url(r'^my/posts/starred/$', HomeView.as_view(), {'is_starred':True}, name='post-list-starred'),
    
    url(r'^proxy/site/(?P<pk>\d+)/favicon.ico$', proxy_favicon, name='proxy-favicon'),
    url(r'^my/sites/$', UserSiteList.as_view(), name='my-sites'),
    url(r'^my/sites/import/$', ImportSubscriptionsFormView.as_view(), name='import'),
    url(r'^my/sites/import/success/$', TemplateView.as_view(template_name='feeds/import-success.html'), name='import-success'),
    
    url(r'^my/posts/mark-as-read/$', MarkPostAsRead.as_view(), name='post-mark-as-read'),
    url(r'^my/posts/mark-all-as-read/$', MarkAllAsRead.as_view(), name='post-mark-all-as-read'),
    url(r'^my/posts/(?P<pk>.+)/star/$', StarPost.as_view(), name='post-star-it'),
)