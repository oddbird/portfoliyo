"""Test recording of notifications."""
import mock
import pytest

from portfoliyo.notifications import record



@pytest.fixture
def mock_record(request):
    patcher = mock.patch('portfoliyo.notifications.record._record')
    mock_record = patcher.start()
    request.addfinalizer(patcher.stop)
    return mock_record



@pytest.mark.parametrize('requested', [True, False])
def test_parent_post(mock_record, requested):
    mock_profile = mock.Mock(id=2, notify_parent_text=requested)
    mock_post = mock.Mock(id=3)
    record.parent_post(mock_profile, mock_post)

    mock_record.assert_called_with(
        mock_profile, 'parent post', triggering=requested, data={'post-id': 3})



@pytest.mark.parametrize('requested', [True, False])
def test_teacher_post(mock_record, requested):
    mock_profile = mock.Mock(id=2, notify_teacher_post=requested)
    mock_post = mock.Mock(id=3)
    record.teacher_post(mock_profile, mock_post)

    mock_record.assert_called_with(
        mock_profile, 'teacher post', triggering=requested, data={'post-id': 3})



@pytest.mark.parametrize('requested', [True, False])
def test_new_parent(mock_record, requested):
    mock_profile = mock.Mock(id=2, notify_new_parent=requested)
    mock_signup = mock.Mock(id=3)
    record.new_parent(mock_profile, mock_signup)

    mock_record.assert_called_with(
        mock_profile, 'new parent', triggering=requested, data={'signup-id': 3})



@pytest.mark.parametrize('requested', [True, False])
def test_added_to_village(mock_record, requested):
    mock_profile = mock.Mock(id=2, notify_added_to_village=requested)
    mock_teacher = mock.Mock(id=3)
    mock_student = mock.Mock(id=4)
    record.added_to_village(mock_profile, mock_teacher, mock_student)

    mock_record.assert_called_with(
        mock_profile,
        'added to village',
        triggering=requested,
        data={'teacher-id': 3, 'student-id': 4},
        )



@pytest.mark.parametrize('requested', [True, False])
def test_new_teacher(mock_record, requested):
    mock_profile = mock.Mock(id=2, notify_joined_my_village=requested)
    mock_teacher = mock.Mock(id=3)
    mock_student = mock.Mock(id=4)
    record.new_teacher(mock_profile, mock_teacher, mock_student)

    mock_record.assert_called_with(
        mock_profile,
        'new teacher',
        triggering=requested,
        data={'teacher-id': 3, 'student-id': 4},
        )



@pytest.fixture
def mock_store(request):
    patcher = mock.patch('portfoliyo.notifications.record.store.store')
    mock_store = patcher.start()
    request.addfinalizer(patcher.stop)
    return mock_store



def test_record(mock_store):
    """Passes notification data on to ``store``."""
    mock_profile = mock.Mock(id=2)
    record._record(mock_profile, 'some', triggering=False, data={'foo': 'bar'})

    mock_store.assert_called_with(
        2, 'some', triggering=False, data={'foo': 'bar'})



def test_record_triggering(mock_store):
    """If triggering, triggers send_notification task."""
    mock_profile = mock.Mock(id=2)
    target = 'portfoliyo.notifications.record.tasks.send_notification.delay'
    with mock.patch(target) as mock_task_delay:
        record._record(mock_profile, 'some', triggering=True)

    mock_task_delay.assert_called_with(2)
    mock_store.assert_called_with(
        2, 'some', triggering=True, data=None)
