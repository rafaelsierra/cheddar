# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

from django.contrib import admin
from accounts.views import RegisterView, ChangeFolder, AddFolderView
from django.views.generic.base import TemplateView
admin.autodiscover()

urlpatterns = patterns('',
    url(r'folder/change/site$', ChangeFolder.as_view(), name="change-folder"),
    url(r'folder/add/$', AddFolderView.as_view(), name="add-folder"),
    
    url(r'register/$', RegisterView.as_view(), name='register'),
    url(r'register/success/$', 
        TemplateView.as_view(template_name="accounts/user_create_form_success.html"), 
        name="register-success"),
                       
    url(r'login/$', 'django.contrib.auth.views.login', 
        {'template_name': 'accounts/login.html'}, name="login"),
)