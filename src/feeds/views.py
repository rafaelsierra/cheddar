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
from django.views.generic.base import View
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from feeds.forms import ImportSubscriptionForm
from feeds.models import Site, Post
import base64
import json
import logging
import urllib2
from django.views.generic.detail import SingleObjectMixin
from accounts.forms import AddFolderForm, SubscribeFeedForm
import datetime
from xml.etree.ElementTree import Element, Comment, tostring
from xml.dom import minidom

logger = logging.getLogger('feeds.views')


class HomeView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'feeds/home.html'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['order'] = self.get_ordering()
        context['current_site'] = self.get_site()
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
        '''Returns what order will be applied in the query'''
        order = None
        # Checks if the order was sent in GET/POST or right from URL
        if 'order' in self.request.REQUEST:
            order = self.request.REQUEST['order'].lower()
        if 'sort' in self.kwargs:
            order = self.kwargs['order'].lower()

        if order not in ('asc', 'desc'):
            # If no order was sent yet (or is wrong), checks if it is in the session
            return self.request.session.get('ordering', 'asc')
        else:
            # If a order method is sent in the URL, change the user session ordering
            self.request.session['ordering'] = order

        return order

    def get_post_filter(self):
        '''Returns a string with the kind of posts de user wishes do see, defaults to "unread"'''
        filtering = None
        if 'filtering' in self.request.REQUEST:
            filtering = self.request.REQUEST['filtering'].lower()
        if 'filtering' in self.kwargs:
            filtering = self.kwargs['filtering'].lower()

        if filtering not in ('all', 'unread', 'read'):
            return self.request.session.get('filtering', 'unread')
        else:
            self.request.session['filtering'] = filtering
        return filtering

    def get_queryset(self):
        is_starred = 'is_starred' in self.kwargs

        post_filter = self.get_post_filter()
        order = self.get_ordering()

        if is_starred:
            # When reading starred posts, filtering don't matter
            queryset = UserSite.posts.starred(self.request.user)
        else:
            if post_filter == 'read':
                queryset = UserSite.posts.read(self.request.user)
            elif post_filter == 'unread':
                queryset = UserSite.posts.unread(self.request.user)
            else: # if == 'all'
                queryset = UserSite.posts.all(self.request.user)

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


class UserSiteList(LoginRequiredMixin, ListView):
    '''View to manage subscriptions'''
    template_name = 'feeds/my-sites.html'
    model = Site
    context_object_name = 'sites'

    def get_context_data(self, **kwargs):
        context = super(UserSiteList, self).get_context_data(**kwargs)
        context['folders'] = self.request.user.folders.all()
        context['add_folder_form'] = AddFolderForm()
        context['subscribe_form'] = SubscribeFeedForm() if not hasattr(self, 'subscribe_form') else self.subscribe_form
        if hasattr(self, 'subscribed_success'):
            context['subscribed_success'] = True
        return context

    def get_queryset(self):
        queryset = super(UserSiteList, self).get_queryset()
        queryset = queryset.filter(usersite__user=self.request.user)
        return queryset

    def post(self, request):
        form = SubscribeFeedForm(request.POST)
        if form.is_valid():
            feed_url = form.cleaned_data['feed_url']
            site, created = Site.objects.get_or_create(feed_url=feed_url, defaults={'last_update': datetime.datetime(1990, 1, 1), 'next_update': timezone.now()})
            if created:
                try:
                    site.update_feed()
                except:
                    # Nothing to do here
                    pass
            UserSite.objects.get_or_create(site=site, user=request.user)[0]
            self.subscribed_success = True
        else:
            self.subscribe_form = form

        return self.get(request)


class ImportSubscriptionsFormView(LoginRequiredMixin, FormView):
    template_name = 'feeds/import.html'
    form_class = ImportSubscriptionForm
    success_url = reverse_lazy('feeds:import-success')

    def form_valid(self, form):
        user = self.request.user
        for feed in form.result.feeds:
            site = Site.objects.get_or_create(feed_url=feed['url'], defaults={
                'title': feed['title'],
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


class ExportSubscriptionsView(LoginRequiredMixin, View):
    def get_xml_root(self):
        # Root element
        root = Element('opml')
        root.set('version', '1.0')
        root.append(Comment('Created by Cheddar to {}'.format(self.request.user.username)))
        # Head element
        head = Element('head')
        title = Element('title')
        title.text = 'Subscriptions'
        dc = Element('dateCreated')
        dc.text = str(timezone.now())
        head.append(dc)
        head.append(title)
        # Append to root
        root.append(head)
        return root

    def _get_folder_outline(self, folder):
        folder_outline = Element('outline')
        folder_outline.set('text', folder.name)
        for usersite in folder.usersite.actives():
            outline = Element('outline')
            outline.set('text', usersite.site.title or 'None')
            outline.set('title', usersite.site.title or 'None')
            outline.set('type', 'rss')
            outline.set('xmlUrl', usersite.site.feed_url)
            outline.set('htmlUrl', usersite.site.url if usersite.site.url else usersite.site.feed_url)
            folder_outline.append(outline)
        return folder_outline

    def write_full_opml(self, response):
        folders = self.request.user.folders.actives()
        root = self.get_xml_root()
        body = Element('body')
        # Loops over all the folders to keep them
        for folder in folders:
            folder_outline = self._get_folder_outline(folder)
            body.append(folder_outline)

        for usersite in self.request.user.my_sites.actives().filter(folder__isnull=True):
            outline = Element('outline')
            outline.set('text', usersite.site.title or 'None')
            outline.set('title', usersite.site.title or 'None')
            outline.set('type', 'rss')
            outline.set('xmlUrl', usersite.site.feed_url)
            outline.set('htmlUrl', usersite.site.url if usersite.site.url else usersite.site.feed_url)
            body.append(outline)

        root.append(body)
        response.write(self.prettify(root))

    def write_folder_opml(self, response):
        self.request.user.folders.actives()
        root = self.get_xml_root()
        body = Element('body')

        folder = Folder.objects.get(id=self.request.REQUEST['folder'])
        if folder.user.id != self.request.user.id:
            raise Http404()

        folder_outline = self._get_folder_outline(folder)
        body.append(folder_outline)
        root.append(body)
        response.write(self.prettify(root))

    def prettify(self, elem):
        raw_string = tostring(elem, 'utf-8')
        parsed = minidom.parseString(raw_string)
        return parsed.toprettyxml('    ')

    def get(self, *args, **kwargs):
        response = HttpResponse()
        if 'folder' in self.request.REQUEST:
            self.write_folder_opml(response)
        else:
            self.write_full_opml(response)

        response['Content-Disposition'] = 'attachment; filename="{}-cheddar.ompl"'.format(self.request.user.username)
        return response


class MarkPostAsRead(LoginRequiredMixin, View, SingleObjectMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(MarkPostAsRead, self).dispatch(*args, **kwargs)

    def post(self, request):
        if 'id' not in request.POST:
            response = {'error': True, 'message': _('No post informed')}
        else:
            get_object_or_404(Post, id=request.POST['id']).mark_as_read(request.user)
            response = {'success': True}

        return HttpResponse(json.dumps(response), content_type='application/json')


class MarkAllAsRead(LoginRequiredMixin, View):
    '''Dude, this can take forever...'''
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(MarkAllAsRead, self).dispatch(*args, **kwargs)

    def post(self, request, **kwargs):
        for post in UserSite.posts.unread(request.user):
            post.mark_as_read(request.user)

        return HttpResponse(json.dumps({'success': True}), content_type='application/json')


class StarPost(LoginRequiredMixin, View, SingleObjectMixin):
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


@cache_page(3600 * 24 * 15)
def proxy_favicon(request, pk):
    '''Downloads and cache site's favicon'''
    # TODO: Better improve security here...
    site = get_object_or_404(Site, id=pk)
    if not site.url:
        return HttpResponse(base64.decodestring(DEFAULT_FAVICON), content_type="image/png")

    try:
        favicon = urllib2.urlopen('{}/favicon.ico'.format(site.url).replace('//favicon.ico', '/favicon.ico'))
    except Exception:
        logger.exception('Failed to download site\'s favicon')
        return HttpResponse(base64.decodestring(DEFAULT_FAVICON), content_type="image/png")
    else:
        if favicon.headers.get('Content-Type', '').startswith('text'):
            return HttpResponse(base64.decodestring(DEFAULT_FAVICON), content_type="image/png")
        else:
            return HttpResponse(favicon.read(), content_type=favicon.headers.get('Content-Type', 'image/x-icon'))
