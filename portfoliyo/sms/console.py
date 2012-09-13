"""Fake console SMS backend for local dev."""
import sys
import threading

from . import base


class ConsoleSMSBackend(base.SMSBackend):
    def __init__(self, *args, **kwargs):
        self.stream = kwargs.pop('stream', sys.stdout)
        self._lock = threading.RLock()


    def send(self, to, from_, body):
        """Write SMS to the stream in a thread-safe way."""
        self._lock.acquire()
        try:
            self.stream.write('-'*79)
            self.stream.write('\n')
            self.stream.write('Text from %s to %s: %s' % (from_, to, body))
            self.stream.write('\n')
            self.stream.write('-'*79)
            self.stream.write('\n')
            self.stream.flush()
        finally:
            self._lock.release()
        return None
