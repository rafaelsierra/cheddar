# -*- coding: utf-8 -*-
from django.contrib import admin
from feeds.models import Site, Post
import datetime

class SiteAdmin(admin.ModelAdmin):
    list_display = ('url', 'title', 'updated_at', 'next_update', 'next_update_eta')
    list_filter = ('is_active',)
    search_fields = ('title', 'url')
    readonly_fields = ('title', 'url')
    actions = ['start_worker']
    
    def start_worker(self, request, queryset):
        for site in queryset:
            site.update_feed()
    start_worker.short_description = u"Start site's worker"
        
    def next_update(self, instance):
        return instance.updated_at + datetime.timedelta(seconds=instance.next_update_eta())
    

class PostAdmin(admin.ModelAdmin):
    raw_id_fields = ('site',)
    list_display = ('small_title','author', 'site_name', 'created_at', 'captured_at')
    search_fields = ('title', 'text', 'site__title')
    
    def site_name(self, instance):
        return instance.site.title if instance.site.title else unicode(instance.site.id)
    
    def small_title(self, instance):
        'Returns a small instance to display on admin'
        return instance.title[:80]
    
admin.site.register(Site, SiteAdmin)
admin.site.register(Post, PostAdmin)