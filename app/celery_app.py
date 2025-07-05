from logging import INFO

from celery.signals import setup_logging
from celery import Celery

from app.LoggingLogic import create_logger

celery = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1", include=["app.tasks.email"])

celery_logger = create_logger(name="Celery", get_logger="celery", level=INFO)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Moscow",
    enable_utc=True,
)

@setup_logging.connect
def on_setup_logging(**kwargs):
    return None