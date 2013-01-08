"""Integration tests for email-sending."""
from django.core import mail
import pytest

from portfoliyo.notifications import record
from portfoliyo.notifications.render import base
from portfoliyo.tests import factories



@pytest.fixture
def recip(request, db):
    """A user who can receive notifications."""
    # Turn all notification triggers off; we want to trigger sending manually
    return factories.ProfileFactory.create(
        user__email='foo@example.com',
        user__is_active=True,
        notify_new_parent=False,
        notify_parent_text=False,
        notify_added_to_village=False,
        notify_joined_my_village=False,
        notify_teacher_post=False,
        )



class TestSend(object):
    def test_send_only_if_email(self, db):
        """If user has no email, notifications not queried or sent."""
        p = factories.ProfileFactory.create(user__email=None)
        assert not base.send(p.id)


    def test_send_only_if_active(self, db):
        """If user is inactive, notifications not queried or sent."""
        p = factories.ProfileFactory.create(
            user__email='foo@example.com', user__is_active=False)
        assert not base.send(p.id)


    def test_send_only_if_notifications(self, db, redis):
        """If there are no notifications, don't try to send an email."""
        p = factories.ProfileFactory.create(
            user__email='foo@example.com', user__is_active=True)
        assert not base.send(p.id)


    def test_generic_subject_single_student(self, recip):
        """Generic subject if multiple notification types, single student."""
        rel = factories.RelationshipFactory.create(
            from_profile=recip, to_profile__name='A Student')
        other_rel = factories.RelationshipFactory.create(
            to_profile=rel.student)

        record.added_to_village(recip, other_rel.elder, rel.student)
        record.new_teacher(recip, other_rel.elder, rel.student)

        assert base.send(recip.id)
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "New activity in A Student's village."


    def test_generic_subject_multiple_students(self, recip):
        """Generic subject if multiple notification types, multiple students."""
        rel = factories.RelationshipFactory.create(from_profile=recip)
        other_rel = factories.RelationshipFactory.create()
        factories.RelationshipFactory.create(
            from_profile=recip, to_profile=other_rel.student)

        record.added_to_village(recip, other_rel.elder, other_rel.student)
        record.new_teacher(recip, other_rel.elder, rel.student)

        assert base.send(recip.id)
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "New activity in two of your villages."


    @pytest.mark.parametrize('village_count', [1, 2])
    def test_only_added_to_village_subject(self, village_count, recip):
        """Specific subject if all notifications are added-to-village."""
        for i in range(village_count):
            rel = factories.RelationshipFactory.create(
                from_profile=recip, to_profile__name='S%s' % i)
            other_rel = factories.RelationshipFactory.create(
                from_profile__name='E%s' % i, to_profile=rel.student)
            record.added_to_village(recip, other_rel.elder, rel.student)

        if village_count == 1:
            exp = "E0 added you to S0's village."
        else:
            exp = "You have been added to two villages."

        assert base.send(recip.id)
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == exp


    @pytest.mark.parametrize('params', [
            (["StudentX"], ["Teacher1"], "Teacher1 joined StudentX's village."),
            (
                ["StudentX", "StudentY"], ["Teacher1"],
                "Teacher1 joined two of your villages."
                ),
            (
                ["StudentX"], ["Teacher1", "Teacher2"],
                "Two teachers joined StudentX's village."
                ),
            (
                ["StudentX", "StudentY"], ["Teacher1", "Teacher2"],
                "Two teachers joined two of your villages."
                ),
            ])
    def test_only_new_teachers_subject(self, params, recip):
        """Specific subject if all notifications are new-teacher."""
        student_names, teacher_names, expected = params
        teacher_profiles = []
        for teacher_name in teacher_names:
            teacher_profiles.append(
                factories.ProfileFactory.create(name=teacher_name))
        for student_name in student_names:
            rel = factories.RelationshipFactory.create(
                from_profile=recip, to_profile__name=student_name)
            for teacher in teacher_profiles:
                factories.RelationshipFactory.create(
                    from_profile=teacher, to_profile=rel.student)
                record.new_teacher(recip, teacher, rel.student)

        assert base.send(recip.id)
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == expected
