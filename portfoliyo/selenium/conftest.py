import pytest
from selenium.webdriver.firefox.webdriver import WebDriver



@pytest.fixture(scope='session')
def selenium(request):
    selenium = WebDriver()
    selenium.live_server = request.getfuncargvalue('live_server')
    request.addfinalizer(selenium.quit)
    return selenium



@pytest.fixture(autouse=True, scope='function')
def _selenium_live_server_helper(request):
    if 'selenium' in request.funcargnames:
        request.getfuncargvalue('transactional_db')
