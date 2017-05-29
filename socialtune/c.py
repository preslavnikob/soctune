from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
CELERY_IMPORTS=("socialtune.task_1")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialtune.settings')

app = Celery('socialtune',include=['socialtune.tasks'])

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
