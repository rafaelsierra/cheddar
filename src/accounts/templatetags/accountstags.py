# -*- coding: utf-8 -*-
from django import template
from django.template.base import TemplateSyntaxError
from accounts.models import UserSite
from accounts.forms import UnsubscribeFeedForm

register = template.Library()

@register.assignment_tag(takes_context=True)
def get_unread_count_for_site(context, site=None, user=None):
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


@register.simple_tag(takes_context=True)
def show_unread_count_for_site(context, site=None, user=None):
    return get_unread_count_for_site(context, site, user)
    
    
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
    

@register.assignment_tag(takes_context=True)
def get_usersite(context, user, site):
    '''Returns the UserSite instance'''
    return UserSite.objects.get(user=user, site=site)    



@register.assignment_tag(takes_context=True)
def get_unsubscribe_form(context, usersite):
    form = UnsubscribeFeedForm(instance=usersite)
    return form



@register.assignment_tag(takes_context=True)
def get_folder_usersites(context, folder=None):
    '''Returns all the sites a folder contains'''        
    if not folder:
        folder = context.get('folder', None)
        if not folder:
            raise TemplateSyntaxError('You must inform what folder you want to list')
        
    return folder.usersite.actives()
    
       