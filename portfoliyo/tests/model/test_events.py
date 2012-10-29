"""Test pusher events."""
from django.core.urlresolvers import reverse
import mock

from portfoliyo.model import events
from portfoliyo.tests import factories



def test_student_event():
    """Pusher event for adding/editing/removing a student."""
    rel = factories.RelationshipFactory.create()
    g = factories.GroupFactory.create(owner=rel.elder)
    g.students.add(rel.student)
    with mock.patch('portfoliyo.model.events.get_pusher') as mock_get_pusher:
        channel = mock.Mock()
        mock_get_pusher.return_value = {
            'students_of_%s' % rel.elder.id: channel,
            }
        events.student_event('some_event', rel.student, rel.elder)

    args = channel.trigger.call_args[0]
    assert args[0] == 'some_event'
    assert len(args[1]['objects']) == 1
    data = args[1]['objects'][0]
    assert data['name'] == rel.student.name
    assert data['id'] == rel.student.id
    assert data['groups'] == [g.pk]
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
    group.students.add(factories.ProfileFactory.create(name="A Student"))
    with mock.patch('portfoliyo.model.events.get_pusher') as mock_get_pusher:
        channel = mock.Mock()
        mock_get_pusher.return_value = {
            'groups_of_%s' % group.owner.id: channel,
            }
        events.group_event('some_event', group)

    args = channel.trigger.call_args[0]
    assert args[0] == 'some_event'
    assert len(args[1]['objects']) == 1
    data = args[1]['objects'][0]
    assert data['name'] == group.name
    assert data['id'] == group.id
    assert data['students'][0]['name'] == "A Student"
    assert data['resource_uri'] == reverse(
        'api_dispatch_detail',
        kwargs={
            'api_name': 'v1', 'resource_name': 'group', 'pk': group.pk},
        )
