"""Celery configuration."""
from __future__ import absolute_import

from collections import Sequence
import logging
import threading

from celery import Celery, Task
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction, models
from django.db.models import loading

from portfoliyo import xact


if 'raven.contrib.django' in settings.INSTALLED_APPS: # pragma: no cover
    from raven.contrib.celery import register_signal
    from raven.contrib.django.models import client
    # automatic logging of task failures to Sentry
    register_signal(client)



logger = logging.getLogger(__name__)



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


    def apply_async(self, *args, **kw):
        """
        If in transaction, push onto pending-tasks instead of sending to queue.

        (This is the method called by ``task.delay(...)``).

        """
        if _in_transaction():
            _get_pending_tasks().append((self, args, kw))
        else:
            # no transaction in progress, send to queue immediately
            return self.original_apply_async(*args, **kw)



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



def is_sequence(val):
    """Return ``True`` if ``val`` is a ``Sequence`` but not a string."""
    return isinstance(val, Sequence) and not isinstance(val, basestring)



class ModelReference(object):
    def __init__(self, app_label, model_name, pk):
        self.app_label = app_label
        self.model_name = model_name
        self.pk = pk


    def as_tuple(self):
        return (self.app_label, self.model_name, self.pk)


    @classmethod
    def from_instance(cls, instance):
        """
        Create and return a ``ModelReference`` from a model instance.

        If the ``instance`` argument is not a model instance, return the
        argument itself unmodified.

        If the argument is a sequence, attempt to create a reference of each
        item in the sequence.

        """
        if is_sequence(instance):
            return type(instance)(cls.from_instance(v) for v in instance)

        if not isinstance(instance, models.Model):
            return instance

        ret = cls(
            instance._meta.app_label, instance._meta.module_name, instance.pk)

        logger.debug("ModelTask created %r" % ret)

        return ret


    @classmethod
    def dereference(cls, val, cache=None):
        """
        Return model instance referred to by ``val``, if a ``ModelReference``.

        If ``val`` is a sequence, attempt to dereference each item in the
        sequence.

        If ``val`` is not a ``ModelReference``, return ``val`` unmodified.

        May raise ``DereferenceFailed`` if ``val`` is a ``ModelReference`` but
        cannot be de-referenced (e.g. has been deleted).

        """
        if is_sequence(val):
            return type(val)(cls.dereference(v, cache) for v in val)
        if isinstance(val, cls):
            return val._dereference(cache)
        return val


    def _dereference(self, cache):
        """Return referenced model instance, or raise ``DereferenceFailed``."""
        t = self.as_tuple()
        if cache and t in cache:
            logger.debug("ModelTask found %r in cache" % self)
            return cache[t]

        logger.debug("ModelTask dereferencing %r" % self)
        model_class = loading.cache.get_model(self.app_label, self.model_name)
        if model_class is None:
            raise DereferenceFailed(
                "Model class %s.%s not found." % (
                    self.app_label, self.model_name)
                )
        try:
            instance = model_class._default_manager.get(pk=self.pk)
        except model_class.DoesNotExist:
            raise DereferenceFailed("Instance of %s with pk %s not found." % (
                    model_class, self.pk))

        if cache is not None:
            cache[t] = instance

        return instance


    def __repr__(self):
        return "ModelReference(%r, %r, %r)" % (
            self.app_label, self.model_name, self.pk)



class DereferenceFailed(ValueError):
    pass



class ModelTask(TransactionTask):
    """
    Celery task class that transparently dehydrates/rehydrates model arguments.

    Automatically detects task arguments that are model instances (or sequences
    of model instances) and transforms them into a ``ModelReference`` object
    (or sequence of ``ModelReference`` objects) for pickling.

    At execution time, the ``ModelReference`` is re-hydrated into an actual
    model object, which is passed to the task function. If any model arguments
    cannot be re-hydrated (i.e. the row has disappeared from the database), the
    task is not executed.

    """
    def apply_async(self, args=None, kwargs=None, **kw):
        """Dehydrate any model arguments to ``ModelReference`` instances."""
        args = [ModelReference.from_instance(a) for a in args]
        kwargs = dict(
            (k, ModelReference.from_instance(v)) for k, v in kwargs.items())
        return super(ModelTask, self).apply_async(args, kwargs, **kw)


    def __call__(self, *args, **kw):
        """
        Re-hydrate any ``ModelReference``s before executing task.

        If not all ``ModelReference``s can be dereferenced successfully, skip
        task execution and return ``None``.

        """
        cache = {}
        try:
            args = [ModelReference.dereference(a, cache) for a in args]
            kw = dict(
                (k, ModelReference.dereference(v, cache))
                for k, v in kw.items()
                )
        except DereferenceFailed as e:
            logger.warning("ModelTask dereference failed: %s" % e)
            return None
        return super(ModelTask, self).__call__(*args, **kw)



if not settings.CELERY_ALWAYS_EAGER: # pragma: no cover
    if not settings.REDIS_URL:
        raise ImproperlyConfigured(
            "Must set REDIS_URL in order to turn CELERY_ALWAYS_EAGER off.")
    celery = TransactionCelery(
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
        )
else:
    celery = TransactionCelery()
    celery.conf.update(CELERY_ALWAYS_EAGER=True)

celery.conf.update(
    CELERY_DISABLE_RATE_LIMITS=True,
    CELERY_TIMEZONE=settings.TIME_ZONE,
    CELERY_STORE_ERRORS_EVEN_IF_IGNORED=True,
    )
