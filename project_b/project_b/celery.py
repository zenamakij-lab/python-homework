import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_b.settings")

app = Celery("project_b")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
