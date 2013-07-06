# -*- coding: utf-8 -*-
from accounts.models import UserSite, Folder
from base.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from feeds.forms import ImportSubscriptionForm
from feeds.mixins import FeedListMixin
from feeds.models import Site, Post
import base64
import ipdb
import json
import logging
import urllib2
from django.views.generic.detail import SingleObjectMixin

logger = logging.getLogger('feeds.views')

class HomeView(ListView, LoginRequiredMixin):
    model = Post
    template_name = 'feeds/home.html'
    context_object_name = 'posts'
    
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['order'] = self.get_ordering()
        return context
    
    def get_site(self):
        '''Returns site instance if set or None'''
        if 'site' in self.request.REQUEST:
            return Site.objects.get(id=self.request.REQUEST['site'])
        elif 'site' in self.kwargs:
            return Site.objects.get(id=self.kwargs['site'])
    
    
    def get_folder(self):
        '''Returns folder instance if set or None'''
        if 'folder' in self.request.REQUEST:
            return Folder.objects.get(id=self.request.REQUEST['folder'])
        elif 'folder' in self.kwargs:
            return Folder.objects.get(id=self.kwargs['folder'])    

    def get_ordering(self):
        sort = None
        if 'order' in self.request.REQUEST:
            order = self.request.REQUEST['order'].lower()
        if 'sort' in self.kwargs:
            order = self.kwargs['order'].lower()
            
        if not order in ('asc', 'desc'):
            return 'asc'
        return order
            

    def get_queryset(self):
        is_read = self.kwargs.get('is_read', False)
        is_starred = 'is_starred' in self.kwargs
        order = self.get_ordering()

        if is_starred:
            queryset = UserSite.posts.starred(self.request.user)
        else:
            if is_read:
                queryset = UserSite.posts.read(self.request.user)
            else:
                queryset = UserSite.posts.unread(self.request.user)

        # You can't filter both at once        
        if self.get_site():
            queryset = queryset.filter(site=self.get_site())
        elif self.get_folder():
            queryset = queryset.filter(site__usersite__folder=self.get_folder())

        # Fake pagination (since reading posts breaks default pagination)
        if 'since' in self.request.REQUEST:
            # Sorting also changes the filter
            if order == 'asc':
                query = {'captured_at__gt': self.request.REQUEST.get('since')}
            else:
                query = {'captured_at__lt': self.request.REQUEST.get('since')}
            queryset = queryset.filter(**query)
            
        # Sort the result
        if order == 'asc':
            queryset = queryset.order_by('captured_at')
        else:
            queryset = queryset.order_by('-captured_at')
            
        queryset = queryset[:42]
            
        return queryset
        

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
                'last_update': timezone.now(),
                'next_update': timezone.now(),
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
                    
                    

class MarkPostAsRead(View, LoginRequiredMixin, SingleObjectMixin):
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



class MarkAllAsRead(View, LoginRequiredMixin):
    '''Dude, this can take forever...'''
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(MarkAllAsRead, self).dispatch(*args, **kwargs)
    
    def post(self, request, **kwargs):
        for post in UserSite.posts.unread(request.user):
            post.mark_as_read(request.user)
            
        return HttpResponse(json.dumps({'success':True}), content_type='application/json')



class StarPost(View, LoginRequiredMixin, SingleObjectMixin):
    '''Star the post of user'''
    model = Post
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(StarPost, self).dispatch(*args, **kwargs)

    
    def post(self, request, *args, **kwargs):
        post = self.get_object()
        if not post:
            return HttpResponseNotFound()
        user = request.user
        userpost = post.get_userpost(user)
        # Just switch it and returns whatever new status is
        userpost.is_starred = not userpost.is_starred
        userpost.save()
        response = {'id': post.id, 'is_starred': userpost.is_starred}
        return HttpResponse(json.dumps(response), content_type='application/json')
    

    
DEFAULT_FAVICON = 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAABtklE\nQVQ4y43TTUvUURQG8N/1ZUAKy2qjEEgUFC2KNpUbtyFueiEpGRsp6AO06FPkvhepxqaQioKJthGB\n0SZqESiFCJWrUINK+s/YbXHHGcmpvHA5z+Ge8/Cc594bYoyUQlEwhJyNrUw0aTiOhHhHUZCXIaCl\ntsN/KCKCiRBLfsrkFCLVbyy+Yf4p76+yvEDrP0myEEuiDIW4vuDTY16Oki39VVEigAo2dbGjj95h\nes80ql6cYu5hUzUNglUPVovaO+grsfN4yl9f4t3YOpKWenMhcvozR6/TuZvKMs9O8OpCqjx0hd6T\nxGYKmnkwe5upQsJ7znP4RsL3u6gs/aEgh2KgvJfpsXSy6xyDbxOeGefjo4SP3GSlmQcR1Vrc0s3g\nNO2dzN5iajR5MvQjdT3YTrawRkFEzzHyFUYqbD3Ak301JYWGJ3P3aiNdrHuRCKroLxNa0+4v83W+\nMc7+yynOlVLsHuDXWoKmLwQfriXcM5Dm/jKV8m0H1xBEmTY8HySuEKsJt2FhJlV19CTJ3xdT3rY5\n5bWnXBTl66OQmkP936nf1Pp8IsQYuRuKoiFhg985ygSTzsaR3435oAsmcnGfAAAAAElFTkSuQmCC\n'
@cache_page(3600*24*15)
def proxy_favicon(request, pk):
    '''Downloads and cache site's favicon'''
    # TODO: Better improve security here...
    site = get_object_or_404(Site, id=pk)
    if not site.url:
        return HttpResponse(base64.decodestring(DEFAULT_FAVICON), content_type="image/png")

    try:
        favicon = urllib2.urlopen('{}/favicon.ico'.format(site.url).replace('//favicon.ico', '/favicon.ico'))
    except Exception, e:
        logger.exception('Failed to download site\'s favicon')
        return HttpResponse(base64.decodestring(DEFAULT_FAVICON), content_type="image/png")
    else:
        if favicon.headers.get('Content-Type', '').startswith('text'):
            return HttpResponse(base64.decodestring(DEFAULT_FAVICON), content_type="image/png")
        else:
            return HttpResponse(favicon.read(), content_type=favicon.headers.get('Content-Type', 'image/x-icon'))