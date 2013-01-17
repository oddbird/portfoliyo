"""Tests for notification-email-sending debug view."""
import mock
import pytest

from portfoliyo.view.notifications import send_email



@pytest.fixture
def response(request):
    """Get a response based on params."""
    params = request.getfuncargvalue('params')
    req = mock.Mock()
    req.user.profile.id = params.get('profile_id', 1)
    req.user.email = params.get('email', 'foo@example.com')
    req.user.is_active = params.get('active', True)
    req.GET = params.get('GET', {})
    with mock.patch('portfoliyo.view.notifications.render.send') as mock_send:
        mock_send.return_value = params.get('sent', True)
        response = send_email(req)
    response.mock_send = mock_send
    return response




@pytest.mark.parametrize('params', [
        {
            'email': 'foo@example.com',
            'active': True,
            'profile_id': 3,
            'sent': True,
            'response': "Email sent to foo@example.com.",
            'send_args': ([3], {'clear': False}),
            },
        {
            'email': 'foo@example.com',
            'active': True,
            'profile_id': 3,
            'sent': True,
            'GET': {'clear': '1'},
            'response': "Email sent to foo@example.com.",
            'send_args': ([3], {'clear': True}),
            },
        {
            'email': 'foo@example.com',
            'active': True,
            'sent': False,
            'response': "No notifications found; no email sent.",
            },
        {
            'email': 'foo@example.com',
            'active': False,
            'sent': False,
            'response': "User inactive; no email sent.",
            },
        {
            'email': None,
            'active': True,
            'sent': False,
            'response': "User has no email address; no email sent.",
            },
        ])
def test_send_email(response, params):
    if 'response' in params:
        assert response.content == params['response']
    if 'send_args' in params:
        args, kw = params['send_args']
        response.mock_send.assert_called_with(*args, **kw)

