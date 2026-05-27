"""Celery app instance configured for AMQPS broker, no result backend."""
from celery import Celery

from celery_app import config

app = Celery("notifications")

app.conf.broker_url = config.build_broker_url()
app.conf.broker_use_ssl = config.build_broker_use_ssl()

app.conf.task_default_queue = "notification"
app.conf.task_acks_late = True
app.conf.worker_prefetch_multiplier = 1

app.autodiscover_tasks(["celery_app"])
