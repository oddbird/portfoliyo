from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from .page import Page



class BasePage(Page):
    """Base class for all PYO Pages."""
    user_name_locator = (By.CSS_SELECTOR, '.meta .settingslink')
    logout_locator = (By.CSS_SELECTOR, '#logoutform > button')


    @property
    def is_user_logged_in(self):
        return self.is_element_visible(*self.user_name_locator)


    @property
    def username_text(self):
        return self.selenium.find_element(*self.user_name_locator).text


    def click_logout(self):
        logout = self.selenium.find_element(*self.logout_locator)
        # @@@ JS workaround because move_to_element (mouseover) does not
        # trigger :hover pseudoclass to show submenu in Firefox Driver
        javascript = '$(".meta .useractions").show();'
        self.selenium.execute_script(javascript)
        WebDriverWait(self.selenium, self.timeout).until(
            lambda s: logout.is_displayed())
        logout.click()
        from .home import HomePage
        return HomePage(self.selenium)
