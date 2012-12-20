"""Celery configuration."""
from __future__ import absolute_import

import threading

from celery import Celery, Task
from django.conf import settings
from django.db import transaction

from portfoliyo import xact


if 'raven.contrib.django' in settings.INSTALLED_APPS:
    from raven.contrib.celery import register_signal
    from raven.contrib.django.models import client
    # automatic logging of task failures to Sentry
    register_signal(client)



_thread_data = threading.local()



def _get_pending_tasks():
    """Return calling thread's pending transactional tasks."""
    return _thread_data.__dict__.setdefault('pending_tasks', [])



class TransactionTask(Task):
    """
    Task that waits for current transaction to complete before recording.

    Makes the task effectively part of the transaction: only when the
    transaction commits successfully is the pending task sent on to the task
    queue. If the transaction fails and is rolled back, pending tasks from that
    transaction will be discarded and never sent into the queue.

    If a task is called when no transaction is in progress, the task will be
    sent to the task queue immediately.

    Waiting until the transaction is committed before sending tasks to the
    queue avoids a possible race condition for tasks whose body requires access
    to database objects. If such a task is sent to the task queue, and picked
    up by a worker, before the database transaction that saves those objects is
    commmitted, it would fail.

    This implementation is inspired by
    https://github.com/chrisdoble/django-celery-transactions

    """
    def original_apply_async(self, *a, **kw):
        """Shortcut to reach original ``apply_async`` method."""
        return super(TransactionTask, self).apply_async(*a, **kw)


    def apply_async(self, *a, **kw):
        """
        If in transaction, push onto pending-tasks instead of sending to queue.

        (This is the method called by ``task.delay(...)``).

        """
        if _in_transaction():
            _get_pending_tasks().append((self, a, kw))
        else:
            # no transaction in progress, send to queue immediately
            return self.original_apply_async(*a, **kw)



def _in_transaction():
    """Return True if currently in a transaction."""
    return transaction.is_managed()



def _discard_tasks(**kw):
    """Transaction is rolled back; discard all pending tasks."""
    _get_pending_tasks()[:] = []

xact.post_rollback.connect(_discard_tasks)



def _send_tasks(**kw):
    """Transaction is committed; send all pending tasks."""
    pending = _get_pending_tasks()
    while pending:
        task, a, kw = pending.pop(0)
        task.original_apply_async(*a, **kw)

xact.post_commit.connect(_send_tasks)


class TransactionCelery(Celery):
    """Celery app class that uses TransactionTask task base by default."""
    def task(self, *a, **kw):
        kw.setdefault('base', TransactionTask)
        return super(TransactionCelery, self).task(*a, **kw)



if settings.REDIS_URL: # pragma: no cover
    celery = TransactionCelery(
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
        )  # pragma: no cover
else:
    celery = TransactionCelery()
    celery.conf.update(CELERY_ALWAYS_EAGER=True)

celery.conf.update(
    CELERY_DISABLE_RATE_LIMITS=True,
    CELERY_TIMEZONE=settings.TIME_ZONE,
    CELERY_STORE_ERRORS_EVEN_IF_IGNORED=True,
    )
