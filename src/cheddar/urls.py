from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

from rest_framework import routers

from accounts import views as accounts_view
from feeds import views as feeds_view

admin.autodiscover()

router = routers.DefaultRouter(trailing_slash=False)
router.register('account', accounts_view.AccountViewSet, base_name='account')
router.register('feeds/sites', feeds_view.SiteViewSet, base_name='sites')

urlpatterns = patterns(
    '',
    url(r'^v1/', include(router.urls)),
    url(r'^v1/obtain-auth-token$', accounts_view.AuthenticateView.as_view(), name='obtain-auth-token'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
