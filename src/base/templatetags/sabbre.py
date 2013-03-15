# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.assignment_tag
def filter_queryset(queryset, **kwargs):
    return queryset.filter(**kwargs)