"""Test pusher events."""
from django.core.urlresolvers import reverse
import mock

from portfoliyo.model import events
from portfoliyo.tests import factories



def test_student_added():
    """Pusher event for adding a student."""
    rel = factories.RelationshipFactory.create()
    g = factories.GroupFactory.create(owner=rel.elder)
    g.students.add(rel.student)
    with mock.patch('portfoliyo.model.events.get_pusher') as mock_get_pusher:
        channel = mock.Mock()
        mock_get_pusher.return_value = {
            'students_of_%s' % rel.elder.id: channel,
            }
        events.student_added(rel.student, rel.elder)

    args = channel.trigger.call_args[0]
    assert args[0] == 'student_added'
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
