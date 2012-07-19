from .base import *

SESSION_COOKIE_SECURE = True
# http://en.wikipedia.org/wiki/Strict_Transport_Security
SECURE_HSTS_SECONDS = 86400
SECURE_FRAME_DENY = True
SECURE_SSL_REDIRECT = True

DEBUG = False
TEMPLATE_DEBUG = False

# Causes CSS/JS to be served in a single combined, minified file, with a name
# based on contents hash (thus can be safely far-futures-expired). With the
# below two settings, run "python manage.py collectstatic" followed
# by "python manage.py compress": the contents of ``STATIC_ROOT`` can then be
# deployed into production.
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

# Use memcached rather than local-memory cache. See
# http://docs.djangoproject.com/en/dev/topics/cache/ for more configuration
# options. For faster caching, install pylibmc in place of python-memcached and
# replace MemcachedCache with PyLibMCCache.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# import local settings, if they exist
local_settings = abspath(join(dirname(__file__), "local.py"))
if exists(local_settings):
    exec(open(local_settings).read())
