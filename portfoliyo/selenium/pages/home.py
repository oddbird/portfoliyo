from selenium.webdriver.common.by import By

from .base import BasePage



class HomePage(BasePage):

    page_title = 'Portfoliyo'


    def go_to_home_page(self):
        self.get_relative_path('/')
