from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse
admin.autodiscover()

js_info_dict = {
    'packages': ('accounts','feeds'),
}

class TempHome(View):
    def get(self, request):
        if request.user.is_anonymous():
            return HttpResponseRedirect(reverse('accounts:login'))
        else:
            return HttpResponseRedirect(reverse('feeds:home'))

urlpatterns = patterns('',
    url(r'^$', TempHome.as_view(), name='home'),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', name='js-catalog'),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^feeds/', include('feeds.urls', namespace='feeds')),
    url(r'^admin/', include(admin.site.urls)),
    
)
