from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default settings for celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stratahq.settings')

app = Celery('stratahq')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
