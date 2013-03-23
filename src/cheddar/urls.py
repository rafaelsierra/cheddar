from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^feeds/', include('feeds.urls', namespace='feeds')),
    url(r'^admin/', include(admin.site.urls)),
)
