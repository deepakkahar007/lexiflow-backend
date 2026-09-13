from celery import Celery

from config.settings import config

celery_client = Celery(
    "fastapi_app", broker=config.REDIS_TRANSPORTER, backend=config.REDIS_RESULTS
)
