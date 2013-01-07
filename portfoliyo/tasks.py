"""Celery tasks."""
from __future__ import absolute_import

from celery.utils.log import get_task_logger

from portfoliyo.celery import celery


logger = get_task_logger(__name__)


# set ignore_result=True for tasks where we don't care about the return value
# set acks_late=True for tasks that are better executed twice than not at all

@celery.task(ignore_result=True, acks_late=True)
def send_sms(phone, body):
    """Send an SMS message."""
    from portfoliyo import sms
    sms.send(phone, body)



@celery.task(ignore_result=True)
def push_event(name, *args, **kw):
    """Send a Pusher event."""
    from portfoliyo.model import events
    event_function = getattr(events, name)
    event_function(*args, **kw)