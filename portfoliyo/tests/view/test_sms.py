"""Tests for SMS-receiving view."""
from xml.etree import ElementTree

from django.conf import settings
from django.test import RequestFactory
from django.test.utils import override_settings
import mock

from portfoliyo.view import sms


def request(data=None, **extra):
    """Return a POST request for twilio_receive."""
    return RequestFactory().post('/_twilio_hook/', data or {}, **extra)


def signed_request(data=None, **extra):
    """Return a POST request with Twilio signature header."""
    extra.setdefault('HTTP_X_TWILIO_SIGNATURE', 'foo')
    return request(data, **extra)


def data(**kw):
    """Get sample POST data with default fallbacks."""
    defaults = {'From': 'from', 'Body': 'body'}
    defaults.update(kw)
    return defaults


@override_settings(TWILIO_AUTH_TOKEN='foo')
@mock.patch('portfoliyo.view.sms.RequestValidator.validate')
@mock.patch('portfoliyo.sms.hook.receive_sms')
def test_calls_receive_sms(mock_receive_sms, mock_validate):
    """Calls receive_sms with POSTed From and Body."""
    mock_validate.return_value = True
    mock_receive_sms.return_value = None

    response = sms.twilio_receive(signed_request(data()))

    assert response.status_code == 200
    mock_receive_sms.assert_called_with('from', 'body')


@override_settings(TWILIO_AUTH_TOKEN='foo')
@mock.patch('portfoliyo.view.sms.RequestValidator.validate')
@mock.patch('portfoliyo.sms.hook.receive_sms')
def test_no_reply(mock_receive_sms, mock_validate):
    """If receive_sms returns None, no reply SMS is sent."""
    mock_validate.return_value = True
    mock_receive_sms.return_value = None

    response = sms.twilio_receive(signed_request(data()))
    xml = ElementTree.XML(response.content)

    assert response.status_code == 200
    assert not list(xml)


@override_settings(TWILIO_AUTH_TOKEN='foo')
@mock.patch('portfoliyo.view.sms.RequestValidator.validate')
@mock.patch('portfoliyo.sms.hook.receive_sms')
def test_reply(mock_receive_sms, mock_validate):
    """If receive_sms returns a string, that is sent as reply SMS."""
    mock_validate.return_value = True
    mock_receive_sms.return_value = "a reply message!"

    response = sms.twilio_receive(signed_request(data()))

    assert response.status_code == 200
    xml = ElementTree.XML(response.content)

    assert response.status_code == 200
    assert len(xml) == 1
    assert xml[0].text == "a reply message!"


@override_settings(TWILIO_AUTH_TOKEN='foo')
@mock.patch('portfoliyo.view.sms.RequestValidator.validate')
@mock.patch('portfoliyo.sms.hook.receive_sms')
def test_splits_long_reply(mock_receive_sms, mock_validate):
    """If receive_sms returns a long string, that is sent as >1 reply SMSes."""
    mock_validate.return_value = True
    mock_receive_sms.return_value = "a" * 161

    response = sms.twilio_receive(signed_request(data()))

    assert response.status_code == 200
    xml = ElementTree.XML(response.content)

    assert response.status_code == 200
    assert len(xml) == 2
    assert xml[0].text == ("a" * 157) + '...'
    assert xml[1].text == '...' + ("a" * 4)


def test_requires_TWILIO_AUTH_TOKEN(monkeypatch):
    """If TWILIO_AUTH_TOKEN setting is not set, returns 403."""
    if hasattr(settings, 'TWILIO_AUTH_TOKEN'):
        monkeypatch.delattr(settings, 'TWILIO_AUTH_TOKEN')
    response = sms.twilio_receive(request())

    assert response.status_code == 403


def test_requires_POST():
    """Responds to GET with 405 Method Not Allowed."""
    response = sms.twilio_receive(RequestFactory().get('/_twilio_hook/'))

    assert response.status_code == 405


@override_settings(TWILIO_AUTH_TOKEN='foo')
def test_requires_twilio_signature():
    """Responds with 403 if X-Twilio-Signature header not present."""
    response = sms.twilio_receive(request())

    assert response.status_code == 403


@override_settings(TWILIO_AUTH_TOKEN='foo')
@mock.patch('portfoliyo.view.sms.RequestValidator.validate')
def test_validation(mock_validate):
    """Responds with 403 if validation function returns False."""
    mock_validate.return_value = False
    response = sms.twilio_receive(signed_request())

    assert response.status_code == 403
