from celery import Celery

from ..config import get_settings

settings = get_settings()

celery_app = Celery("orcamento_ia", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_always_eager=settings.celery_task_always_eager,
)

