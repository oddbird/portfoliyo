from celery import Celery
from celery.utils.log import get_task_logger
from django.conf import settings
from raven.contrib.celery import register_signal
from raven.contrib.django.models import client


logger = get_task_logger(__name__)



# automatic logging of task failures to Sentry
register_signal(client)



if settings.REDIS_URL: # pragma: no cover
    celery = Celery(
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
        )  # pragma: no cover
else:
    celery = Celery()
    celery.conf.update(CELERY_ALWAYS_EAGER=True)
