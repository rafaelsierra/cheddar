# -*- coding: utf-8 -*-
from accounts.models import UserSite, Folder
from base.views import LoginRequiredMixin
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView
from feeds.mixins import FeedListMixin
from feeds.models import Site, Post
import json
from django.views.generic.edit import FormView
from feeds.forms import ImportSubscriptionForm
from django.core.urlresolvers import reverse_lazy
import ipdb

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
        
    
class ImportSubscriptionsFormView(FormView, LoginRequiredMixin):
    template_name = 'feeds/import.html'
    form_class = ImportSubscriptionForm
    success_url = reverse_lazy('feeds:import-success')
    
    def form_valid(self, form):
        user = self.request.user
        for feed in form.result.feeds:
            site = Site.objects.get_or_create(feed_url=feed['url'], defaults={
                'title':feed['title'],
            })[0]
            
            # Links the user with site
            usersite = user.my_sites.get_or_create(user=user, site=site)[0]
            
            # Currently only one folder per site is allowed
            if feed['tags']:
                tag = feed['tags'][0]
                folder = user.folders.get_or_create(name=tag[:32])[0] # Trim at 32 chars
                usersite.folder = folder
                usersite.save()
        return super(ImportSubscriptionsFormView, self).form_valid(form)
                    
                    
    
    
class UserPostList(ListView, LoginRequiredMixin):
    template_name = 'feeds/ajax/post-list.html'
    context_object_name = 'posts'
    model = Post
    paginate_by = 42
    
    def get_site(self):
        '''Returns site instance if set or None'''
        if 'site' in self.request.REQUEST:
            return Site.objects.get(id=self.request.REQUEST['site'])
        
    
    def get_queryset(self):
        is_read = self.kwargs.get('is_read', False)
        if is_read:
            queryset = UserSite.posts.read(self.request.user)
        else:
            queryset = UserSite.posts.unread(self.request.user)
        
        if self.get_site():
            queryset = queryset.filter(site=self.get_site())
        
        return queryset
    

class MarkPostAsRead(View, LoginRequiredMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(MarkPostAsRead, self).dispatch(*args, **kwargs)
    
    
    def post(self, request):
        if not 'id' in request.POST:
            response = {'error': True, 'message': _('No post informed')} 
        else:
            get_object_or_404(Post, id=request.POST['id']).mark_as_read(request.user)
            response = {'success': True}
            
        return HttpResponse(json.dumps(response), content_type='application/json')