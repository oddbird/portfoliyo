"""Selenium tests for home page."""
from .base_test import BaseTest

from .login_page import LoginPage



class TestHomePage(BaseTest):

    def test_login_and_logout(self):
        login_pg = LoginPage(self.selenium)

        self.selenium.get('%s%s' % (self.live_server_url, '/login/'))
        self.assertFalse(login_pg.is_user_logged_in)

        login_pg.login()

        self.assertTrue(login_pg.is_user_logged_in)
        self.assertEqual(login_pg.username_text, 'test@example.com')

        login_pg.click_logout()

        self.assertFalse(login_pg.is_user_logged_in)
