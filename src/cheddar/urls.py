from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cheddar.views.home', name='home'),
    # url(r'^cheddar/', include('cheddar.foo.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
