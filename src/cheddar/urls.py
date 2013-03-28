from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

js_info_dict = {
    'packages': ('accounts','feeds'),
}

urlpatterns = patterns('',
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', name='js-catalog'),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^feeds/', include('feeds.urls', namespace='feeds')),
    url(r'^admin/', include(admin.site.urls)),
    
)
