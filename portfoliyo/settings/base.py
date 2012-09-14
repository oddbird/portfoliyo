"""
Default Django settings for portfoliyo project.

"""
import os
from os.path import abspath, dirname, exists, join

BASE_PATH = dirname(dirname(dirname(abspath(__file__))))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = [
    ("Carl Meyer", "carl@oddbird.net"),
    ("Jonny Gerig Meyer", "jonny@oddbird.net"),
]

MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "portfoliyo",
        "USER": os.environ.get("USER", "portfoliyo"),
        }
    }

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# Absolute path to the directory that holds static files.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = join(BASE_PATH, "collected-assets")

# URL that handles the static files served from STATIC_ROOT.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

# A list of locations of additional static files
STATICFILES_DIRS = [join(BASE_PATH, "static")]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

# Make this unique, and don't share it with anybody.
SECRET_KEY = "-p++6p5gmhd_3wz43nl5&_6==tz_d*^yaf)@w@=w)3o!glwixd"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "session_csrf.context_processor",
    "portfoliyo.google_analytics.context_processor",
    "portfoliyo.village.pusher.context_processor",
]

MIDDLEWARE_CLASSES = [
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.transaction.TransactionMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "session_csrf.CsrfMiddleware",
]

ROOT_URLCONF = "portfoliyo.urls"

TEMPLATE_DIRS = [
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don"t forget to use absolute paths, not relative paths.
    join(BASE_PATH, "templates"),
]

DATE_FORMAT = "m/d/Y"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "floppyforms",
    "widget_tweaks",
    "form_utils",
    "south",
    "portfoliyo.landing",
    "portfoliyo.users",
    "portfoliyo.village",
]

MESSAGE_STORAGE = "django.contrib.messages.storage.fallback.FallbackStorage"

INSTALLED_APPS += ["icanhaz", "messages_ui", "ajax_loading_overlay"]
ICANHAZ_DIRS = [join(BASE_PATH, "jstemplates")]
MIDDLEWARE_CLASSES.insert(
    MIDDLEWARE_CLASSES.index(
        "django.contrib.messages.middleware.MessageMiddleware"
        ) + 1,
    "messages_ui.middleware.AjaxMessagesMiddleware",
    )

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'portfoliyo.wsgi.application'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG is False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django.request":{
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

INSTALLED_APPS += ["compressor"]
COMPRESS_CSS_FILTERS = ["compressor.filters.css_default.CssAbsoluteFilter",
                        "compressor.filters.cssmin.CSSMinFilter"]

INSTALLED_APPS += ["djangosecure"]
MIDDLEWARE_CLASSES.insert(0, "djangosecure.middleware.SecurityMiddleware")
SESSION_COOKIE_HTTPONLY = True


INSTALLED_APPS += ["registration"]
ACCOUNT_ACTIVATION_DAYS = 7
LOGIN_URL = "/login/"
AUTHENTICATION_BACKENDS = ["portfoliyo.users.auth_backend.EmailBackend"]
LOGIN_REDIRECT_URL = "/"

DEFAULT_FROM_EMAIL = 'Portfoliyo <noreply@portfoliyo.org>'

PORTFOLIYO_SMS_BACKEND = 'portfoliyo.sms.console.ConsoleSMSBackend'
PORTFOLIYO_SMS_DEFAULT_FROM = '+15555555555'
