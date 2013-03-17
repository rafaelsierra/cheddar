# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

from django.contrib import admin
from accounts.views import RegisterView
from django.views.generic.base import TemplateView
admin.autodiscover()

urlpatterns = patterns('',
    url('register/$', RegisterView.as_view(), name='register'),
    url('register/success/$', 
        TemplateView.as_view(template_name="accounts/user_create_form_success.html"), 
        name="register-success"),
                       
    url('login/$', 'django.contrib.auth.views.login', 
        {'template_name': 'accounts/login.html'}, name="login"),
)