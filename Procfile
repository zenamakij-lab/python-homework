web: gunicorn --config gunicorn.conf.py bookstore.wsgi:application
worker: celery -A bookstore worker -l info
beat: celery -A bookstore beat -l info
