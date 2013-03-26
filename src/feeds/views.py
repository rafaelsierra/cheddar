# -*- coding: utf-8 -*-
from django.views.generic.list import ListView
from feeds.mixins import FeedListMixin
from django.views.generic.base import TemplateView
from base.views import LoginRequiredMixin
from feeds.models import Site

class HomeView(TemplateView, LoginRequiredMixin):
    template_name = 'feeds/home.html'

    
class CheddarJSView(TemplateView):
    template_name = 'feeds/cheddar.js'
    
    def dispatch(self, *args, **kwargs):
        response = super(CheddarJSView, self).dispatch(*args, **kwargs)
        response['Content-Type'] = 'text/javascript'
        return response
    

class UserSiteList(ListView, LoginRequiredMixin):
    template_name = 'feeds/ajax/site-list.html'
    model = Site
    
    def get_queryset(self):
        queryset = super(UserSiteList, self).get_queryset()
        queryset = queryset.filter(usersite__user=self.request.user)
        return queryset
        
    