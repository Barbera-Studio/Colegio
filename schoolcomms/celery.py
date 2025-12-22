from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schoolcomms.settings')

app = Celery("schoolcomms")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "send-daily-summary": {
        "task": "notifications.tasks.send_daily_summary",
        "schedule": crontab(hour=18, minute=0),  # cada día a las 18:00
    },
}

