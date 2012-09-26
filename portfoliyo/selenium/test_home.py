"""Selenium tests for home page."""
from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver



class TestHomePage(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(TestHomePage, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestHomePage, cls).tearDownClass()
        cls.selenium.quit()

    def test_landing(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
