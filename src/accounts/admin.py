# -*- coding: utf-8 -*-
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from accounts.models import UserSite
from django.contrib.auth.models import User


class SitesInline(admin.TabularInline):
    model = UserSite


class CheddarUserAdmin(UserAdmin):
    inlines = [SitesInline]


admin.site.unregister(User)
admin.site.register(User, CheddarUserAdmin)
