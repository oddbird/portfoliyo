"""Test recording of notifications."""
import mock
import pytest

from portfoliyo.notifications import record

from portfoliyo.tests import factories



def test_village_additions_calls_added_to_village(db):
    """Calls added_to_village for all student/teacher combos."""
    added_by = factories.ProfileFactory.create()
    teacher1 = factories.ProfileFactory.create()
    teacher2 = factories.ProfileFactory.create()
    student1 = factories.ProfileFactory.create()
    student2 = factories.ProfileFactory.create()

    added_to_village_target = 'portfoliyo.notifications.record.added_to_village'
    with mock.patch(added_to_village_target) as mock_added_to_village:
        record.village_additions(
            added_by,
            [added_by, teacher1, teacher2],
            [student1, student2],
            )

    assert mock_added_to_village.call_count == 4
    mock_added_to_village.assert_any_call(teacher1, added_by, student1)
    mock_added_to_village.assert_any_call(teacher1, added_by, student2)
    mock_added_to_village.assert_any_call(teacher2, added_by, student1)
    mock_added_to_village.assert_any_call(teacher2, added_by, student2)



def test_village_additions_calls_new_teacher(db):
    """Calls new_teacher for each existing teacher in each village."""
    added_by = factories.ProfileFactory.create()
    teacher1 = factories.ProfileFactory.create()
    student1 = factories.ProfileFactory.create()
    student2 = factories.ProfileFactory.create()
    rel1 = factories.RelationshipFactory.create(
        to_profile=student1, from_profile__school_staff=True)
    factories.RelationshipFactory.create(
        to_profile=student1, from_profile__school_staff=False)

    new_teacher_target = 'portfoliyo.notifications.record.new_teacher'
    with mock.patch(new_teacher_target) as mock_new_teacher:
        record.village_additions(
            added_by,
            [added_by, teacher1],
            [student1, student2],
            )

    mock_new_teacher.assert_called_once_with(rel1.elder, teacher1, student1)



@pytest.fixture
def mock_record(request):
    patcher = mock.patch('portfoliyo.notifications.record._record')
    mock_record = patcher.start()
    request.addfinalizer(patcher.stop)
    return mock_record



@pytest.mark.parametrize('requested', [True, False])
@pytest.mark.parametrize('from_teacher', [True, False])
def test_post(mock_record, requested, from_teacher):
    pref = 'notify_%s' % ('teacher_post' if from_teacher else 'parent_text')
    mock_profile = mock.Mock(id=2, **{pref: requested})
    mock_post = mock.Mock(id=3, author=mock.Mock(school_staff=from_teacher))
    record.post(mock_profile, mock_post)

    mock_record.assert_called_with(
        mock_profile, 'post', triggering=requested, data={'post-id': 3})



@pytest.mark.parametrize('requested', [True, False])
def test_bulk_post(mock_record, requested):
    mock_profile = mock.Mock(id=2, notify_teacher_post=requested)
    mock_post = mock.Mock(id=3, author=mock.Mock(school_staff=True))
    record.bulk_post(mock_profile, mock_post)

    mock_record.assert_called_with(
        mock_profile,
        'bulk post',
        triggering=requested,
        data={'bulk-post-id': 3},
        )



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
        data={'added-by-id': 3, 'student-id': 4},
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
    record._record(
        _profile(id=2), 'some', triggering=False, data={'foo': 'bar'})

    mock_store.assert_called_with(
        2, 'some', triggering=False, data={'foo': 'bar'})



def test_record_triggering(mock_store):
    """If triggering, triggers send_notification task."""
    tgt = 'portfoliyo.notifications.record.tasks.send_notification_email.delay'
    with mock.patch(tgt) as mock_task_delay:
        record._record(_profile(id=2), 'some', triggering=True)

    mock_task_delay.assert_called_with(2)
    mock_store.assert_called_with(
        2, 'some', triggering=True, data=None)



def test_record_triggering_disabled(mock_store):
    """If NOTIFICATION_EMAILS setting is ``False``, no email sent."""
    settings_tgt = 'portfoliyo.notifications.record.settings'
    tgt = 'portfoliyo.notifications.record.tasks.send_notification_email.delay'
    with mock.patch(settings_tgt) as mock_settings:
        with mock.patch(tgt) as mock_task_delay:
            mock_settings.NOTIFICATION_EMAILS = False
            record._record(_profile(id=2), 'some', triggering=True)

    assert mock_task_delay.call_count == 0



def test_record_doesnt_store_if_user_inactive(mock_store):
    """Doesn't store notifications for inactive users."""
    record._record(_profile(id=2, is_active=False), 'some')

    assert not mock_store.call_count



def test_record_doesnt_store_if_no_email(mock_store):
    """Doesn't store notifications for users without email addresses."""
    record._record(_profile(id=2, email=None), 'some')

    assert not mock_store.call_count



def _profile(id, email="foo@example.com", is_active=True, **kwargs):
    return mock.Mock(
        id=id, user=mock.Mock(email=email, is_active=is_active), **kwargs)
