web: newrelic-admin run-program gunicorn portfoliyo.wsgi -b 0.0.0.0:$PORT -w 2
celery: celery -A portfoliyo.tasks worker -B
