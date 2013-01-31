"""Tests for NewParentCollector and Signup."""
import mock
import pytest

from portfoliyo.tests import factories

from portfoliyo.notifications.render.collectors import new_parent


class TestSignup(object):
    def test_no_relationship(self, db):
        """If TextSignup parent/student relationship is gone, use role."""
        ts = factories.TextSignupFactory.create(family__role='Foo')
        signup = new_parent.Signup.from_textsignup(ts)

        assert signup.role == 'Foo'



class TestNewParentCollector(object):
    def test_no_student(self, db):
        """Signups without students are not valid for notification."""
        ts = factories.TextSignupFactory.create()
        npc = new_parent.NewParentCollector(mock.Mock())
        with pytest.raises(new_parent.base.RehydrationFailed):
            npc.hydrate({'signup-id': ts.id})
