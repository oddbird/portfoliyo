from .base import *

import os
import urlparse
env = lambda key, returntype=str: returntype(os.environ.get(key, ''))

DATABASES = dict(default={})
def parse_database_url(database, environment_variable='DATABASE_URL'):
    url = urlparse.urlparse(env(environment_variable))
    database.update({
        'NAME': url.path[1:],
        'USER': url.username,
        'PASSWORD': url.password,
        'HOST': url.hostname,
        'PORT': url.port,
        'ENGINE' : {
            'postgres': 'django_postgrespool',
            'mysql': 'django.db.backends.mysql',
            'sqlite': 'django.db.backends.sqlite3',
        }[url.scheme],
        'OPTIONS': {'autocommit': True},
    })
parse_database_url(DATABASES['default'])
del parse_database_url

# support memcachier add-on as well as default memcache add-on
if 'MEMCACHE_SERVERS' not in os.environ:
    os.environ['MEMCACHE_SERVERS'] = os.environ.get('MEMCACHIER_SERVERS', '').replace(',', ';')
if 'MEMCACHE_USERNAME' not in os.environ:
    os.environ['MEMCACHE_USERNAME'] = os.environ.get('MEMCACHIER_USERNAME', '')
if 'MEMCACHE_PASSWORD' not in os.environ:
    os.environ['MEMCACHE_PASSWORD'] = os.environ.get('MEMCACHIER_PASSWORD', '')

# pylibmc can't be imported at build time, so we need a fallback
try:
    import pylibmc
except ImportError:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
            'TIMEOUT': 500,
            'BINARY': True,
        }
    }

DEBUG = False
TEMPLATE_DEBUG = False

TEMPLATE_LOADERS = [
    ('django.template.loaders.cached.Loader', TEMPLATE_LOADERS)
    ]


# This email address will get emailed on 500 server errors.
ADMINS = [
    ('Admin', env('ADMIN_ERROR_EMAILS')),
]

SECRET_KEY = env('DJANGO_SECRET_KEY')

PREPEND_WWW = env('DJANGO_PREPEND_WWW', bool)

# SSL
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env('HSTS_SECONDS', int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# staticfiles / compressor
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_QUERYSTRING_AUTH = False
AWS_HEADERS = {
    'Expires': 'Thu, 15 Apr 2020 20:00:00 GMT',
}
AWS_IS_GZIPPED = True
STATIC_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_STORAGE = 'portfoliyo.storage.CachedS3BotoStorage'
STATICFILES_STORAGE = COMPRESS_STORAGE

# Mailgun
EMAIL_HOST = env('MAILGUN_SMTP_SERVER')
EMAIL_PORT = env('MAILGUN_SMTP_PORT')
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('MAILGUN_SMTP_LOGIN')
EMAIL_HOST_PASSWORD = env('MAILGUN_SMTP_PASSWORD')

# Twilio
PORTFOLIYO_SMS_BACKEND = env('PORTFOLIYO_SMS_BACKEND')
TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN')
PORTFOLIYO_NUMBERS = {
    'us': env('US_NUMBER'),
    'ca': env('CA_NUMBER'),
    }
DEFAULT_COUNTRY_CODE = PORTFOLIYO_COUNTRIES[0][0]
DEFAULT_NUMBER = PORTFOLIYO_NUMBERS[DEFAULT_COUNTRY_CODE]

# Pusher
PUSHER_APPID = env('PUSHER_APPID')
PUSHER_KEY = env('PUSHER_KEY')
PUSHER_SECRET = env('PUSHER_SECRET')

# Sentry/Raven
INSTALLED_APPS += ['raven.contrib.django']
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

REDIS_URL = env('REDISTOGO_URL')
CELERY_ALWAYS_EAGER = False

GOOGLE_ANALYTICS_ID = env('GOOGLE_ANALYTICS_ID')
USERVOICE_ID = env('USERVOICE_ID')
SNAPENGAGE_ID = env('SNAPENGAGE_ID')
MIXPANEL_ID = env('MIXPANEL_ID')
INTERCOM_ID = env('INTERCOM_ID')
CRAZYEGG_ID = env('CRAZYEGG_ID')

PORTFOLIYO_BASE_URL = env('PORTFOLIYO_BASE_URL')

NOTIFICATION_EMAILS = env('PORTFOLIYO_NOTIFICATION_EMAILS', bool)
NOTIFICATION_EXPIRY_SECONDS = env('PORTFOLIYO_NOTIFICATION_EXPIRY_SECONDS', int)
DEBUG_URLS = env('PORTFOLIYO_DEBUG_URLS', bool)
