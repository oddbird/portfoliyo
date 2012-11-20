from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from page import Page

class BasePage(Page):

    _user_name_locator = (By.CSS_SELECTOR, '.meta .settingslink')
    _logout_locator = (By.CSS_SELECTOR, '#logoutform > button')

    @property
    def is_user_logged_in(self):
        return self.is_element_visible(*self._user_name_locator)

    @property
    def username_text(self):
        return self.selenium.find_element(*self._user_name_locator).text

    def click_logout(self):
        logout = self.selenium.find_element(*self._logout_locator)
        self.mouse_over_element(*self._user_name_locator)
        WebDriverWait(self.selenium, self.timeout).until(lambda s: logout.is_displayed())
        logout.click()
