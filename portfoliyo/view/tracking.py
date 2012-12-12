"""
Tracking user actions for analytics.

Record (on server side) actions the user completes successfully, and render
that data out to the client in HTML. A given event should only be rendered out
once, much like user messages.

Currently doesn't handle Ajax/JSON responses; really only intended for user
actions that follow the POST-redirect pattern.

"""
import json


def track(request, event_name, **kwargs):
    """Record that user accomplished ``event_name``, perhaps w/ extra data."""
    events = request.session.setdefault('tracking', [])
    # modifying the list that is already in the session doesn't set modified
    # True, so data isn't saved unless we explicitly set it to True
    request.session.modified = True
    events.append((event_name, kwargs))



def context_processor(request):
    return {'events': EventList(request)}



class EventList(object):
    """
    Can render event list to JSON.

    If accessed, clears events from the session.

    """
    def __init__(self, request):
        self.request = request
        self._events = None


    @property
    def events(self):
        if self._events is None:
            self._events = self.request.session.get('tracking', [])
            self.request.session['tracking'] = []
        return self._events


    def json(self):
        """
        Render events to JSON (as list of tuples).

        First item in each tuple is event name, second is dictionary of
        properties.

        """
        return json.dumps(self.events)
