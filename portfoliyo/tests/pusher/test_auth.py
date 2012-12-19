"""Tests for pusher auth."""
import mock


from portfoliyo.pusher.auth import allow
from portfoliyo.tests import factories



class TestAllow(object):
    def test_all_group_success(self, db):
        """Can join channel for their own all-group."""
        p = factories.ProfileFactory.create()
        assert allow(p, 'private-group_all%s' % p.id)


    def test_all_group_failure(self, db):
        """Cannot join channel for someone else's all-group."""
        p = factories.ProfileFactory.create()
        other = factories.ProfileFactory.create()
        assert not allow(p, 'private-group_all%s' % other.id)


    def test_students_of_success(self, db):
        """Can join channel for their own students."""
        p = factories.ProfileFactory.create()
        assert allow(p, 'private-students_of_%s' % p.id)


    def test_students_of_failure(self, db):
        """Cannot join channel for someone else's students."""
        p = factories.ProfileFactory.create()
        other = factories.ProfileFactory.create()
        assert not allow(p, 'private-students_of_%s' % other.id)


    def test_groups_of_success(self, db):
        """Can join channel for their own students."""
        p = factories.ProfileFactory.create()
        assert allow(p, 'private-groups_of_%s' % p.id)


    def test_groups_of_failure(self, db):
        """Cannot join channel for someone else's students."""
        p = factories.ProfileFactory.create()
        other = factories.ProfileFactory.create()
        assert not allow(p, 'private-groups_of_%s' % other.id)


    def test_student_success(self, db):
        """Can join channel for a student they are elder of."""
        rel = factories.RelationshipFactory.create()
        assert allow(rel.elder, 'private-student_%s' % rel.student.id)


    def test_student_failure(self, db):
        """Cannot join channel for a student they are not elder of."""
        e = factories.ProfileFactory.create()
        s = factories.ProfileFactory.create()
        assert not allow(e, 'private-student_%s' % s.id)


    def test_group_success(self, db):
        """Can join channel for a group they own."""
        g = factories.GroupFactory.create()
        assert allow(g.owner, 'private-group_%s' % g.id)


    def test_group_failure(self, db):
        """Cannot join channel for a group they do not own."""
        p = factories.ProfileFactory.create()
        g = factories.GroupFactory.create()
        assert not allow(p, 'private-group_%s' % g.id)


    def test_not_private(self, db):
        """Non-private channel can be joined by anyone."""
        p = factories.ProfileFactory.create()
        assert allow(p, 'group_1234')


    def test_bad_channel_id(self, db):
        """Last part of channel name must be integer ID."""
        p = factories.ProfileFactory.create()
        assert not allow(p, 'private-group_foo')


    def test_unknown_channel_type(self, db):
        """Unknown channel type is not authorized."""
        p = factories.ProfileFactory.create()
        assert not allow(p, 'private-foo_1')



class TestPusherAuthView(object):
    def test_success(self, client):
        """Returns JSON authorization if successful."""
        profile = factories.ProfileFactory.create()

        with mock.patch('portfoliyo.pusher.auth.allow') as mock_allow:
            with mock.patch('portfoliyo.pusher.auth.get_pusher') as mock_get_p:
                mock_allow.return_value = True
                channel = mock.Mock()
                mock_get_p.return_value = {'channel': channel}
                channel.authenticate.return_value = {'some': 'data'}
                response = client.post(
                    '/pusher/auth',
                    {'channel_name': 'channel', 'socket_id': 'socket-id'},
                    user=profile.user,
                    )

        mock_allow.assert_called_once_with(profile, 'channel')
        channel.authenticate.assert_called_once_with('socket-id')
        assert response.json == {'some': 'data'}



    def test_failed(self, client):
        """Returns 403 if unsuccessful."""
        profile = factories.ProfileFactory.create()

        with mock.patch('portfoliyo.pusher.auth.allow') as mock_allow:
            with mock.patch('portfoliyo.pusher.auth.get_pusher') as mock_get_p:
                mock_allow.return_value = False
                # just needs to be anything other than None
                mock_get_p.return_value = True
                client.post(
                    '/pusher/auth',
                    {'channel_name': 'channel', 'socket_id': 'socket-id'},
                    user=profile.user,
                    status=403,
                    )

        mock_allow.assert_called_once_with(profile, 'channel')


    def test_no_pusher(self, client):
        """Returns 403 if Pusher not configured."""
        profile = factories.ProfileFactory.create()

        with mock.patch('portfoliyo.pusher.auth.allow') as mock_allow:
            with mock.patch('portfoliyo.pusher.auth.get_pusher') as mock_get_p:
                mock_get_p.return_value = None
                client.post(
                    '/pusher/auth',
                    {'channel_name': 'channel', 'socket_id': 'socket-id'},
                    user=profile.user,
                    status=403,
                    )

        assert mock_allow.call_count == 0


    def test_anon_user(self, client):
        """Returns 403 if the user is anonymous."""
        with mock.patch('portfoliyo.pusher.auth.allow') as mock_allow:
            with mock.patch('portfoliyo.pusher.auth.get_pusher') as mock_get_p:
                mock_get_p.return_value = True # anything that isn't None
                client.post(
                    '/pusher/auth',
                    {'channel_name': 'channel', 'socket_id': 'socket-id'},
                    status=403,
                    )

        assert mock_allow.call_count == 0
