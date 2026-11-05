from celery import Celery
from celery.schedules import crontab

from src.config import settings

celery_instance = Celery(
    "tasks", broker=settings.REDIS_URL, include=["src.tasks.tasks"]
)

celery_instance.conf.timezone = "Europe/Moscow"

celery_instance.conf.beat_schedule = {
    "send_email": {
        "task": "booking_today_chekin",
        "schedule": crontab(hour=9, minute=15),
    }
}
