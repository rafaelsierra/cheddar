# -*- coding: utf-8 -*-
from django import template
from django.template.base import TemplateSyntaxError
from accounts.models import UserSite

register = template.Library()

@register.simple_tag(takes_context=True)
def show_unread_count_for_site(context, site=None, user=None):
    if not user:
        user = context.get('user', None)
        if not user and user.is_authenticated():
            # Don't not raise anything so you can use this with anonymous user 
            return ''
        
    if not site:
        site = context.get('site', None)
        if not site:
            raise TemplateSyntaxError('You must inform what site you want to count')
    
    return UserSite.posts.unread(user).filter(site=site).count()
    
    
@register.assignment_tag(takes_context=True)
def get_site_folder(context, site=None, user=None):
    if not user:
        user = context.get('user', None)
        if not user and user.is_authenticated():
            # Don't not raise anything so you can use this with anonymous user 
            return ''
        
    if not site:
        site = context.get('site', None)
        if not site:
            raise TemplateSyntaxError('You must inform what site you want to count')
    
    try:
        usersite = UserSite.objects.get(user=user, site=site)
    except UserSite.DoesNotExist:
        return None
    else:
        return usersite.folder    