"""Selenium tests for home page."""
from .pages.login import LoginPage



def test_login_and_logout(selenium):
    login_pg = LoginPage(selenium, selenium.live_server.url)

    login_pg.go_to_login_page()

    assert not login_pg.is_user_logged_in

    login_pg.login()

    assert login_pg.is_user_logged_in
    assert login_pg.username_text == 'test@example.com'

    login_pg.click_logout()

    assert not login_pg.is_user_logged_in
