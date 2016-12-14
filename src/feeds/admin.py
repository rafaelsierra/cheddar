# -*- coding: utf-8 -*-
from django.contrib import admin
from feeds.models import Site, Post
import datetime
from django.utils import timezone


class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'title', 'updated_at', 'last_update', 'next_update', 'feed_errors')
    list_filter = ('is_active',)
    search_fields = ('title', 'url')
    readonly_fields = ('title', 'url', 'next_update', 'last_update')
    actions = ['force_worker']

    def force_worker(self, request, queryset):
        for site in queryset:
            self.last_update = site.next_update = timezone.now() - datetime.timedelta(hours=24)
            site.save()
            site.update_feed()
    force_worker.short_description = u"Force another site worker"


class PostAdmin(admin.ModelAdmin):
    raw_id_fields = ('site',)
    list_display = ('small_title', 'author', 'site_name', 'created_at', 'captured_at')
    search_fields = ('title', 'content', 'site__title')

    def site_name(self, instance):
        return instance.site.title if instance.site.title else str(instance.site.id)

    def small_title(self, instance):
        'Returns a small text to display on admin'
        return instance.title[:80]

admin.site.register(Site, SiteAdmin)
admin.site.register(Post, PostAdmin)
