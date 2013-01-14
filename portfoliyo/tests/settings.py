from portfoliyo.settings.base import *

COMPRESS_ENABLED = False
# avoid actually calling out to Mixpanel in tests
MIXPANEL_ID = None
