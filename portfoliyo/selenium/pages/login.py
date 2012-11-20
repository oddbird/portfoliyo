from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from portfoliyo.tests import factories

from .base import BasePage



class LoginPage(BasePage):

    page_title = 'Portfoliyo'

    username_locator = (By.ID, 'id_username')
    password_locator = (By.ID, 'id_password')
    submit_locator = (By.CSS_SELECTOR, '#loginform .form-actions > button')


    # def go_to_login_page(self):
    #     self.get_relative_path('/login/')


    def login(self):
        email = 'test@example.com'
        password = 'testpw'

        factories.ProfileFactory.create(
            user__email=email, user__password=password, user__is_staff=True)

        self.selenium.find_element(*self.username_locator).send_keys(email)
        self.selenium.find_element(*self.password_locator).send_keys(password)
        self.selenium.find_element(*self.submit_locator).click()

        WebDriverWait(self.selenium, self.timeout).until(
            lambda s: self.is_user_logged_in)
