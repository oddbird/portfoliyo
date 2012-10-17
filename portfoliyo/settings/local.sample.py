"""
Settings overrides for a particular deployment of this app. The defaults should
be suitable for local development; settings below may need adjustment for a
staging or production deployment.

Copy settings/local.sample.py to settings/local.py and modify as needed.

"""
# If your database is named something other than "portfoliyo", or it's on a
# host other than local socket, or the username needed to connect to it is
# different from your shell user, or a password is required, you'll need to
# uncomment this DATABASES section and fill it out appropriately.

#DATABASES = {
#    "default": {
#        "ENGINE": "django.db.backends.postgresql_psycopg2",
#        "NAME": "portfoliyo",
#        "USER": os.environ.get("USER", "portfoliyo"),
#        "PASSWORD": "",
#        "HOST": "",
#        }
#}

#DEBUG = False
#TEMPLATE_DEBUG = False

#PORTFOLIYO_BASE_URL = 'https://www.portfoliyo.org'

# This email address will get emailed on 500 server errors.
#ADMINS = [
#    ("Some One", "someone@example.com"),
#]

# Absolute path to directory where static assets will be collected by the
# "collectstatic" management command, and can be served by front-end webserver.
# Defaults to absolute filesystem path to "collected-assets/" directory.
#STATIC_ROOT = ""

# Base URL where files in STATIC_ROOT are deployed. Defaults to "/static/".
#STATIC_URL = ""

# Causes CSS/JS to be served in a single combined, minified file, with a name
# based on contents hash (thus can be safely far-futures-expired). With the
# below two settings uncommented, run "python manage.py collectstatic" followed
# by "python manage.py compress": the contents of ``STATIC_ROOT`` can then be
# deployed into production.
#COMPRESS_ENABLED = True
#COMPRESS_OFFLINE = True

# A unique (and secret) key for this deployment.
#SECRET_KEY = ""

# If a mail server is not available at localhost:25, set these to appropriate
# values:
#EMAIL_HOST = ""
#EMAIL_PORT = ""
# If the mail server configured above requires authentication and/or TLS:
#EMAIL_USE_TLS = True
#EMAIL_HOST_USER = ""
#EMAIL_HOST_PASSWORD = ""

# Configure Twilio SMS-sending as follows:
#PORTFOLIYO_SMS_BACKEND = 'portfoliyo.sms.backends.twilio.TwilioSMSBackend'
#TWILIO_ACCOUNT_SID = 'your account sid here'
#TWILIO_AUTH_TOKEN = 'your auth token here'
#PORTFOLIYO_SMS_DEFAULT_FROM = '+15555555555'

# Configure Pusher as follows:
#PUSHER_APPID = 'your appid'
#PUSHER_KEY = 'your key'
#PUSHER_SECRET = 'your secret'

# Uncomment this (and modify LOCATION appropriately) to use memcached rather
# than local-memory cache. This (or some other out-of-process cache backend) is
# required if running under a multi-process webserver such as
# Apache/mod_wsgi. See http://docs.djangoproject.com/en/dev/topics/cache/ for
# more configuration options. For faster caching, install pylibmc in place of
# python-memcached and replace MemcachedCache with PyLibMCCache.
#CACHES = {
#    "default": {
#        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
#        "LOCATION": "127.0.0.1:11211",
#        "KEY_PREFIX": "", # add a global key prefix here if necessary
#    }
#}
