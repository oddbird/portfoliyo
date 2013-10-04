from portfoliyo.settings.default import *

# settings that are always required for a successful test run
DEFAULT_FILE_STORAGE = 'portfoliyo.tests.storage.MemoryStorage'
NOTIFICATION_EMAILS = True
COMPRESS_ENABLED = False
CELERY_ALWAYS_EAGER = True
# avoid actually calling out to Mixpanel in tests
MIXPANEL_ID = None
# avoid actually calling out to Pusher in tests
PUSHER_APPID = None
PUSHER_KEY = None
PUSHER_SECRET = None

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
