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


@pytest.fixture(scope='function')
def factories(request):
    from portfoliyo.tests import factories
    return factories


@pytest.fixture(scope='function')
def teacher(
        request,
        factories,
        email='test@example.com',
        password='testpw',
        is_staff=True,
        ):

    teacher = factories.ProfileFactory.create(
        user__email=email,
        user__password=password,
        user__is_staff=is_staff,
        )
    teacher.user.password = password
    return teacher
