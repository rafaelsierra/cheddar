# -*- coding: utf-8 -*-
# Django settings for a Dockerized cheddar
from .default import *  # NOQA
import djcelery


USE_X_FORWARDED_HOST = True
ALLOWED_HOST = ['*']

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '',
    }
}

SECRET_KEY = 'something to test'

TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

djcelery.setup_loader()
