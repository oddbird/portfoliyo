from portfoliyo.settings.default import *

# settings that are always required for a successful test run
COMPRESS_ENABLED = False
CELERY_ALWAYS_EAGER = True
# avoid actually calling out to Mixpanel in tests
MIXPANEL_ID = None
