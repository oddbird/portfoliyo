from selenium.webdriver.common.by import By

from . import base



class HomePage(base.BasePage):

    page_title = 'Portfoliyo'


    def go_to_home_page(self):
        self.get_relative_path('/')
