from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
# from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


class BaseTest(LiveServerTestCase):
    """Base class for all Tests."""
    @classmethod
    def setUpClass(cls):
        profile = FirefoxProfile()
        profile.native_events_enabled = True
        cls.selenium = WebDriver(firefox_profile=profile)
        super(BaseTest, cls).setUpClass()


    @classmethod
    def tearDownClass(cls):
        super(BaseTest, cls).tearDownClass()
        cls.selenium.quit()
