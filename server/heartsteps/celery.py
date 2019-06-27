from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heartsteps.settings')

app = Celery('heartsteps')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'nightly-data-download': {
        'task': 'heartsteps_data_download.tasks.download_data',
        'schedule': crontab(hour='11')
    },
    'send-adherence-message': {
        'task': 'dashboard.tasks.send_adherence_messages',
        'schedule': crontab(hour='18', minute='30')
    }
}
# 2am UTC = 7pm PDT

app.conf.task_default_queue = 'default'
app.conf.task_routes = {
    'heartsteps_data_download.tasks.*': {
        'queue': 'export'
    },
    'anti_sedentary.tasks.*': {
        'queue': 'messages'
    },
    'fitbit_activities.tasks.*': {
        'queue': 'fitbit'
    },
    'morning_messages.tasks.*': {
        'queue': 'messages'
    },
    'push_messages.tasks.*': {
        'queue': 'messages'
    },
    'walking_suggestions.tasks.*': {
        'queue': 'messages'
    },
    'weekly_reflection.tasks.*': {
        'queue': 'messages'
    }
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
