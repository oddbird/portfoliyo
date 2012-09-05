from django.test.utils import override_settings
import mock

from portfoliyo import admin



def test_login_redirect():
    """Login method redirects to login page."""
    request = mock.Mock()
    request.user.is_authenticated.return_value = False
    request.get_full_path.return_value = "/attempted/path/"
    with override_settings(LOGIN_URL="/login/"):
        response = admin.site.login(request)

    assert response.status_code == 302
    assert response['Location'] == "/login/?next=/attempted/path/"



def test_login_redirect_warning():
    """Logged-in user w/out admin perms gets a warning on redirect."""
    request = mock.Mock()
    request.user.is_authenticated.return_value = True
    request.get_full_path.return_value = "/attempted/path/"
    with mock.patch("portfoliyo.admin.messages") as mock_messages:
        response = admin.site.login(request)

    assert response.status_code == 302
    assert mock_messages.warning.call_count == 1
