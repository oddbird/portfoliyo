from .base import *

# import local settings, if they exist
local_settings = abspath(join(dirname(__file__), "local.py"))
if exists(local_settings):
    exec(open(local_settings).read())

if DEBUG:
# use console email backend in debug mode, unless overridden in local
    try:
        EMAIL_BACKEND
    except NameError:
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


if DEBUG_TOOLBAR:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE_CLASSES += [
        'portfoliyo.view.debug.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': True,
        'HIDE_DJANGO_SQL': True,
        }


if SPEED_TRACER:
    INSTALLED_APPS += ['speedtracer']
    MIDDLEWARE_CLASSES.insert(0, 'speedtracer.middleware.SpeedTracerMiddleware')
