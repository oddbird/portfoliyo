class SMSBackend(object):
    """Base interface for an SMS backend."""
    def send(self, to, from_, body):
        """Send an SMS message."""
        raise NotImplementedError
