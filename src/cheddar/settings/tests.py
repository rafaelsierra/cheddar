# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Django settings for testing cheddar
from .default import *  # NOQA


USE_X_FORWARDED_HOST = True
ALLOWED_HOST = ['*']

DEBUG = False
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS.append('django_celery_results')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '',
    }
}

SECRET_KEY = 'something to test'

CELERY_BROKER_URL = 'memory://'
CELERY_TASK_ALWAYS_EAGER = True
CELERY_RESULT_BACKEND = 'django-db'
