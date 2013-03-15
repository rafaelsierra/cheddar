# -*- coding: utf-8 -*-
from django.contrib import admin
from feeds.models import Site, Post

class SiteAdmin(admin.ModelAdmin):
    list_display = ('url', 'title', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'url')
    

class PostAdmin(admin.ModelAdmin):
    raw_id_fields = ('site',)
    list_display = ('small_title','author', 'site')
    search_fields = ('title', 'text', 'site__title')
    
    def small_title(self, instance):
        'Returns a small instance to display on admin'
        return instance.title[:80]
    
admin.site.register(Site, SiteAdmin)
admin.site.register(Post, PostAdmin)