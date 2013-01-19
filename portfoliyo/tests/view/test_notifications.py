"""Tests for notification-email-sending debug view."""
import mock
import pytest

from portfoliyo.notifications import render
from portfoliyo.view.notifications import send_email, show_email




class TestSendEmail(object):
    @pytest.fixture
    def response(self, request):
        """Get a response based on params."""
        params = request.getfuncargvalue('params')
        req = mock.Mock()
        req.user.profile.id = params.get('profile_id', 1)
        req.user.email = params.get('email', 'foo@example.com')
        req.user.is_active = params.get('active', True)
        req.GET = params.get('GET', {})
        tgt = 'portfoliyo.view.notifications.render.send'
        with mock.patch(tgt) as mock_send:
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
    def test_send_email(self, response, params):
        if 'response' in params:
            assert response.content == params['response']
        if 'send_args' in params:
            args, kw = params['send_args']
            response.mock_send.assert_called_with(*args, **kw)



class TestShowEmail(object):
    @pytest.fixture
    def response(self, request):
        """Get a response based on params."""
        params = request.getfuncargvalue('params')
        req = mock.Mock()
        req.user.profile = 'profile'
        req.GET = params.get('GET', {})
        tgt = 'portfoliyo.view.notifications.render.render'
        with mock.patch(tgt) as mock_render:
            mock_render.return_value = (
                params.get('subject', 'subject'),
                params.get('text', 'text'),
                params.get('html', 'html'),
                )
            response = show_email(req)
        response.mock_render = mock_render
        return response




    @pytest.mark.parametrize('params', [
            { # shows email HTML by default
                'response': "html",
                'content-type': 'text/html',
                'render_args': (['profile'], {'clear': False}),
                },
            { # shows plain text instead if asked
                'GET': {'text': '1'},
                'response': "text",
                'content-type': 'text/plain',
                'render_args': (['profile'], {'clear': False}),
                },
            { # clears notifications if asked
                'GET': {'clear': '1'},
                'response': "html",
                'content-type': 'text/html',
                'render_args': (['profile'], {'clear': True}),
                },
            ])
    def test_send_email(self, response, params):
        if 'response' in params:
            assert response.content == params['response']
        if 'content_type' in params:
            assert response['content-type'] == params['content-type']
        if 'render_args' in params:
            args, kw = params['render_args']
            response.mock_render.assert_called_with(*args, **kw)


    def test_no_notifications(self):
        """Response message if no notifications found."""
        req = mock.Mock(GET={})
        tgt = 'portfoliyo.view.notifications.render.render'
        with mock.patch(tgt) as mock_render:
            mock_render.side_effect = render.NothingToDo
            response = show_email(req)

        assert response.content == "No notifications found."
        assert response['content-type'] == 'text/plain'
