# -*- coding: utf-8 -*-
# Django settings for cheddar project.
import os
from datetime import timedelta


PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')

CRAWLER_USER_AGENT = 'Cheddar Reader Crawler/1.0'
CRAWLER_TIMEOUT = 30 # Avoid setting a high timeout, unless you can aford it
CRAWLER_MAX_FEED_SIZE = 50*1024*1024 # Maximum size in bytes to read from a feed, this may lead to MemoryErrors when to much high
CRAWLER_MAX_FEED_SITE_SITE = 2*1024*1024 # Maximum site in bytes to read from a feed while adding feeds on the site

MIN_UPDATE_INTERVAL_SECONDS = 600 # Updates at max 6 times per hour
MIN_UPDATE_INTERVAL = timedelta(seconds=MIN_UPDATE_INTERVAL_SECONDS)
MAX_UPDATE_INTERVAL_SECONDS = 12*3600 # Updates at last 2 times per day
MAX_UPDATE_INTERVAL = timedelta(MAX_UPDATE_INTERVAL_SECONDS)
MAX_UPDATE_WAIT = timedelta(seconds=3600) # After 1 hour without updates and supposedly running, force another one
MAX_FEED_ERRORS_ALLOWED = 10 # After this much errors, next update will always be the max interval
MAX_FINAL_URL_TRIES = 10 # How much times we should try to find the final URL for a post
CHEDDAR_HISTORY_SIZE = 20 # How much posts should be considered to calculate next update


# Change this if you want bring caos into your instance
CHEDDAR_DEFAULT_USER_ACTIVE_STATUS = False
LOGIN_REDIRECT_URL = '/'


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'cheddar.db'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


ALLOWED_HOSTS = ['localhost']

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = ()

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = 'dont you dare to forget to change this!! :P'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'cheddar.urls'

WSGI_APPLICATION = 'cheddar.wsgi.application'

TEMPLATE_DIRS = ()

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'corsheaders',
    'feeds',
    'accounts',
    'rest_framework',
    'rest_framework.authtoken',
]

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request"
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'stdout': {
            'level': 'WARN',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['stdout'],
        }
    }
}

#
# Celery
#
CELERY_IMPORTS = (
    'feeds.tasks',
)
CELERY_TASK_ROUTES = {
    'feeds.tasks.make_request': {'queue': 'make_request'},
    'feeds.tasks.parse_feed': {'queue': 'parse_feed'},
    'feeds.tasks.update_site_feed': {'queue': 'update_site_feed'},
}
CELERY_BEAT_SCHEDULE = {
    'check_sites_up': {
        'task': 'feeds.tasks.check_sites_for_update',
        'schedule': timedelta(seconds=60),
    },
}

CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'

CELERY_RESULT_EXPIRES = 10 # 10 seconds to expire the result
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ACKS_LATE = False
CELERY_SEND_EVENTS = True

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_EVENT_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


#
# REST framework
#
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '50/day',
        'user': '100/second',
        'login': '30/minute',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
}
