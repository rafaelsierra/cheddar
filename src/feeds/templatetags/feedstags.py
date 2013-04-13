# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.assignment_tag(takes_context=True)
def get_if_starred(context, user=None, post=None):
    '''Returns if user has starred post'''
    if not user:
        user = context.get('user')
        if not user:
            return None
        
    if not post:
        post = context.get('post')
        if not post:
            return None
        
    userpost = post.get_userpost(user)
    return userpost.is_starred