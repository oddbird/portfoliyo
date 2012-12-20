from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.common.action_chains import ActionChains



class Page(object):
    """Base class for all Pages."""
    def __init__(self, selenium):
        self.selenium = selenium
        self.timeout = 30


    def get_relative_path(self, url):
        self.selenium.get('%s%s' % (self.selenium.live_server, url))


    def is_element_present(self, by, value):
        self.selenium.implicitly_wait(0)
        try:
            self.selenium.find_element(by, value)
            return True
        except NoSuchElementException:
            # this will return a snapshot, which takes time.
            return False
        finally:
            # set back to where you once belonged
            self.selenium.implicitly_wait(self.timeout)


    def is_element_visible(self, by, value):
        try:
            return self.selenium.find_element(by, value).is_displayed()
        except (NoSuchElementException, ElementNotVisibleException):
            # this will return a snapshot, which takes time.
            return False


    def mouse_over_element(self, by, value):
        # This doesn't work to trigger :hover in Firefox, so is unused.
        element = self.selenium.find_element(by, value)
        ActionChains(self.selenium).move_to_element(element).perform()


    def wait_for_ajax(self):
        WebDriverWait(self.selenium, self.timeout).until(
            lambda s: s.execute_script("return $.active == 0"),
            "Wait for AJAX timed out after %s seconds" % self.timeout,
            )


    def type_in_element(self, locator, text):
        """
        Type a string into an element.

        Clear the element first then type the string via send_keys.

        Arguments:
        locator -- a locator for the element
        text -- the string to type via send_keys

        """
        text_fld = self.selenium.find_element(*locator)
        text_fld.clear()
        text_fld.send_keys(text)
