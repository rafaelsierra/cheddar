# -*- coding: utf-8 -*-
# Django settings for a Dockerized cheddar
from .default import *  # NOQA

import os

PROJECT_ROOT = '/opt/cheddar'
USE_X_FORWARDED_HOST = True

DEBUG = bool(os.environ.get('DEBUG', False))
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['POSTGRES_DB'],
        'USER':  os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ['POSTGRES_HOST'],
    }
}

CELERY_BROKER_URL = os.environ['CELERY_BROKER_URL']
CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

TIME_ZONE = os.environ.get('TIME_ZONE', 'America/Chicago')
LANGUAGE_CODE = os.environ.get('LANGAGE_CODE', 'en-us')

MEDIA_ROOT = '/var/cheddar/media'
STATIC_ROOT = '/var/cheddar/static'

SECRET_KEY = os.environ.get('SECRET_KEY', 'secret key unset')

CORS_ORIGIN_ALLOW_ALL = os.environ.get('CORS_ORIGIN_ALLOW_ALL', '') == 'YES' # You need to shout this out
CORS_ORIGIN_WHITELIST = os.environ.get('CORS_ORIGIN_WHITELIST', '').split(',') # Comma separated values

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'stream': {
            'level': 'INFO',
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        '': {
            'handlers': ['stream'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

