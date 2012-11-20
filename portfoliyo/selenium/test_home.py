"""Selenium tests for home page."""
from .base import BaseTest

from .pages.login import LoginPage



class TestHomePage(BaseTest):


    def test_login_and_logout(self):
        login_pg = LoginPage(self.selenium, self.live_server_url)

        login_pg.go_to_login_page()

        assert login_pg.is_user_logged_in == False

        login_pg.login()

        assert login_pg.is_user_logged_in
        assert login_pg.username_text == 'test@example.com'

        login_pg.click_logout()

        assert login_pg.is_user_logged_in == False
