from celery import Celery
from django.conf import settings


if settings.REDIS_URL: # pragma: no cover
    celery = Celery(
        'tasks',
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
        )  # pragma: no cover
else:
    celery = Celery('tasks')
    celery.conf.update(CELERY_ALWAYS_EAGER=True)
