"""Test pusher events."""
from django.core.urlresolvers import reverse
import mock

from portfoliyo.model import events
from portfoliyo.tests import factories



def test_student_event():
    """Pusher event for adding/editing/removing a student."""
    rel = factories.RelationshipFactory.create()
    with mock.patch('portfoliyo.model.events.get_pusher') as mock_get_pusher:
        channel = mock.Mock()
        mock_get_pusher.return_value = {
            'private-students_of_%s' % rel.elder.id: channel,
            }
        events.student_event('some_event', rel.student, rel.elder)

    args = channel.trigger.call_args[0]
    assert args[0] == 'some_event'
    assert len(args[1]['objects']) == 1
    data = args[1]['objects'][0]
    assert data['name'] == rel.student.name
    assert data['id'] == rel.student.id
    assert data['resource_uri'] == reverse(
        'api_dispatch_detail',
        kwargs={
            'api_name': 'v1', 'resource_name': 'user', 'pk': rel.student.pk},
        )
    assert data['village_uri'] == reverse(
        'village', kwargs={'student_id': rel.student.pk})
    assert data['edit_student_uri'] == reverse(
        'edit_student', kwargs={'student_id': rel.student.pk})



def test_group_event():
    """Pusher event for adding/editing/removing a group."""
    group = factories.GroupFactory.create()
    with mock.patch('portfoliyo.model.events.get_pusher') as mock_get_pusher:
        channel = mock.Mock()
        mock_get_pusher.return_value = {
            'private-groups_of_%s' % group.owner.id: channel,
            }
        events.group_event('some_event', group)

    args = channel.trigger.call_args[0]
    assert args[0] == 'some_event'
    assert len(args[1]['objects']) == 1
    data = args[1]['objects'][0]
    assert data['name'] == group.name
    assert data['id'] == group.id
    assert data['resource_uri'] == reverse(
        'api_dispatch_detail',
        kwargs={
            'api_name': 'v1', 'resource_name': 'group', 'pk': group.pk},
        )


def test_pusher_socket_error():
    """
    A pusher socket error is logged to Sentry and then ignored.

    Pusher is not critical enough to be worth causing an action to fail.

    """
    import socket

    get_pusher_location = 'portfoliyo.model.events.get_pusher'
    logger_error_location = 'portfoliyo.model.events.logger.error'
    with mock.patch(get_pusher_location) as mock_get_pusher:
        channel = mock_get_pusher.return_value['channel']
        channel.trigger.side_effect = socket.error('connection timed out')

        with mock.patch(logger_error_location) as mock_logger_error:
            events.trigger('channel', 'event', {})

    mock_logger_error.assert_called_with(
        "Pusher exception: connection timed out",
        exc_info=True,
        extra={'stack': True},
        )


def test_pusher_bad_response():
    """
    Any exception from Pusher is ignored and logged to Sentry.

    Pusher is not critical enough to be worth causing an action to fail.

    """
    get_pusher_location = 'portfoliyo.model.events.get_pusher'
    logger_error_location = 'portfoliyo.model.events.logger.error'
    with mock.patch(get_pusher_location) as mock_get_pusher:
        channel = mock_get_pusher.return_value['channel']
        channel.trigger.side_effect = Exception(
            'Unexpected return status 413')

        with mock.patch(logger_error_location) as mock_logger_error:
            events.trigger('channel', 'event', {})

    mock_logger_error.assert_called_with(
        "Pusher exception: Unexpected return status 413",
        exc_info=True,
        extra={'stack': True},
        )
