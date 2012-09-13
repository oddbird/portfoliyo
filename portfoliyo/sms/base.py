"""Base interface for an SMS backend."""
class SMSBackend(object):
    def send(self, to, from_, body):
        """Send an SMS message."""
        raise NotImplementedError
