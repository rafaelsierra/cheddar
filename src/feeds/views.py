import datetime

from django.db import transaction, IntegrityError
from django.utils import timezone

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import exceptions
from rest_framework import status
from rest_framework.response import Response

from .serializers import SiteSerializer, SiteAddSerializer, PostSerializer, PostPatchSerializer
from .models import Site, Post

DEFAULT_FAVICON = 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAABtklE\nQVQ4y43TTUvUURQG8N/1ZUAKy2qjEEgUFC2KNpUbtyFueiEpGRsp6AO06FPkvhepxqaQioKJthGB\n0SZqESiFCJWrUINK+s/YbXHHGcmpvHA5z+Ge8/Cc594bYoyUQlEwhJyNrUw0aTiOhHhHUZCXIaCl\ntsN/KCKCiRBLfsrkFCLVbyy+Yf4p76+yvEDrP0myEEuiDIW4vuDTY16Oki39VVEigAo2dbGjj95h\nes80ql6cYu5hUzUNglUPVovaO+grsfN4yl9f4t3YOpKWenMhcvozR6/TuZvKMs9O8OpCqjx0hd6T\nxGYKmnkwe5upQsJ7znP4RsL3u6gs/aEgh2KgvJfpsXSy6xyDbxOeGefjo4SP3GSlmQcR1Vrc0s3g\nNO2dzN5iajR5MvQjdT3YTrawRkFEzzHyFUYqbD3Ak301JYWGJ3P3aiNdrHuRCKroLxNa0+4v83W+\nMc7+yynOlVLsHuDXWoKmLwQfriXcM5Dm/jKV8m0H1xBEmTY8HySuEKsJt2FhJlV19CTJ3xdT3rY5\n5bWnXBTl66OQmkP936nf1Pp8IsQYuRuKoiFhg985ygSTzsaR3435oAsmcnGfAAAAAElFTkSuQmCC\n'


class SiteViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage subscribed sites
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Site.objects.filter(usersite__user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ('GET', 'DELETE'):
            return SiteSerializer
        elif self.request.method == 'POST':
            return SiteAddSerializer

    def update(self, *args, **kwargs):
        raise exceptions.MethodNotAllowed(self.request.method)
    partial_update = update

    def create(self, *args, **kwargs):
        """Override create method to be able to return the site object when created"""
        super(SiteViewSet, self).create(*args, **kwargs)
        serializer = SiteSerializer(self.feed_site)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data)
        )

    def perform_create(self, serializer):
        """Subscribe the user into a site"""
        try:
            with transaction.atomic():
                site, created = Site.objects.get_or_create(
                    feed_url=serializer.validated_data['feed_url'],
                    defaults={
                        'last_update': timezone.make_aware(datetime.datetime(1990, 1, 1)),
                        'next_update': timezone.now()
                    }
                )
        except IntegrityError: # pragma: no cover
            raise exceptions.APIException()
        else:
            self.request.user.my_sites.get_or_create(site=site)
            self.feed_site = site
            if created:
                site.update_feed()

    def perform_destroy(self, instance):
        my_site = self.request.user.my_sites.get(site=instance)
        my_site.delete()


class PostsViewSet(viewsets.ModelViewSet):
    """
    ViewSet to read posts
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostSerializer
        elif self.request.method in ('PATCH', 'PUT'):
            return PostPatchSerializer

    def destroy(self, *args, **kwargs):
        raise exceptions.MethodNotAllowed(self.request.method)
    create = destroy

    def perform_update(self, serializer):
        post = self.get_object()
        userpost = post.userpost.get_or_create(user=self.request.user)[0]
        for key, value in serializer.validated_data.items():
            setattr(userpost, key, value)
        userpost.save()

    def get_queryset(self):
        queryset = Post.objects.filter(site__usersite__user=self.request.user).select_related(
            'site',
        )
        if self.request.GET.get('order', 'asc').lower() == 'asc':
            return queryset.order_by('captured_at')
        return queryset.order_by('-captured_at')
