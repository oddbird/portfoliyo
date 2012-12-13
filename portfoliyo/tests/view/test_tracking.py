import mock

from portfoliyo.view import tracking


class MockSession(dict):
    pass



def test_track():
    """track() function records event data in session."""
    request = mock.Mock()
    request.session = MockSession()
    tracking.track(request, 'some event', foo='bar')

    assert request.session['tracking'] == [('some event', {'foo': 'bar'})]
    assert request.session.modified



class TestEventList(object):
    def test_json(self):
        """json method outputs tracking data as JSON, clears from session."""
        request = mock.Mock()
        request.session = {'tracking': [('some event', {'foo': 'bar'})]}
        events = tracking.EventList(request)

        assert events.json() == '[["some event", {"foo": "bar"}]]'
        assert request.session['tracking'] == []

        # the JSON is cached for future accesses on same list
        assert events.json() == '[["some event", {"foo": "bar"}]]'
