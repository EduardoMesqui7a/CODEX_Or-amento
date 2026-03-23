from ..db import SessionLocal
from ..services.job_service import JobService
from .celery_app import celery_app


@celery_app.task(name="jobs.run_processing_job", autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def run_processing_job(job_id: str):
    db = SessionLocal()
    try:
        service = JobService(db)
        service.run_job(job_id)
    finally:
        db.close()

