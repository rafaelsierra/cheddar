# -*- coding: utf-8 -*-
from accounts.models import Folder, UserSite
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from feeds.models import Site
from feeds.utils import build_request, FindLinkToFeedParser
import urllib2
import socket
import feedparser

class RegisterForm(UserCreationForm):
    '''Extends the default user creation form to add email as a required field'''
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise ValidationError(_("This field is required."))
        return email
    
    class Meta:
        model = User
        fields = ('username', 'email')
        


class AddFolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ('name',)
        
     
        
class SubscribeFeedForm(forms.Form):
    feed_url = forms.URLField()
    
    def clean_feed_url(self):
        '''Checks if the feed_url is actually a feed or if there is a feed available'''
        url = self.cleaned_data['feed_url']
        # First checks if there is already a site with this URL
        if Site.objects.filter(feed_url=url).exists():
            return url
        
        # Now open it just to get the URL content
        request = build_request(url)
        try:
            # In this point you can force a DoS attack by submitting tons of requests to slow sites.
            # But if you do this, I hope you burn in hell with Satan sodomizing you with a fork.
            content = urllib2.urlopen(url, timeout=settings.CRAWLER_TIMEOUT).read(settings.CRAWLER_MAX_FEED_SITE_SITE)
        except (urllib2.HTTPError, urllib2.URLError, socket.error), e:
            raise ValidationError(_(u'Failed trying to parse {}. Error was: {}').format(url, e.message))
        except socket.timeout, e:
            raise ValidationError(_(u'Timeout trying to download {}, server took more than {} seconds to return.').format(url, settings.CRAWLER_TIMEOUT))
            
        
        feed = feedparser.parse(content)

        if feed['bozo'] == 1 and not feed.entries:
            # Invalid feed content, trying to check if there is a feed on the HTML content
            parser = FindLinkToFeedParser()
            parser.feed(content)
            parser.close()
            if parser.feed_url:
                # We've got the feed url, let's just assume it's correct
                # TODO: Not assume it is correct
                return parser.feed_url
            else:
                # Feed URL not found, nothing left to do
                raise ValidationError(_('Your feed URL is not a valid feed nor a site with link to it\'s own RSS or Atom or is too big to check'))
        
        return url



class UnsubscribeFeedForm(forms.ModelForm):
    site = forms.ModelChoiceField(widget=forms.HiddenInput, queryset=Site.objects.all())
    class Meta:
        model = UserSite
        fields = ('site',)