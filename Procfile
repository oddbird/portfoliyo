web: newrelic-admin run-program gunicorn portfoliyo.wsgi -b 0.0.0.0:$PORT -w 5
celery: newrelic-admin run-program celery -A portfoliyo.tasks worker -B
