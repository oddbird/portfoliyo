from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver



class BaseTest(LiveServerTestCase):
    """Base class for all Tests."""
    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(BaseTest, cls).setUpClass()


    @classmethod
    def tearDownClass(cls):
        super(BaseTest, cls).tearDownClass()
        cls.selenium.quit()
