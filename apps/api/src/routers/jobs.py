from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..db import get_db
from ..schemas import JobCreatePayload, JobListResponse, JobResponse
from ..services.job_service import JobService
from ..workers.tasks import run_processing_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreatePayload, user=Depends(get_current_user), db: Session = Depends(get_db)):
    service = JobService(db)
    job = service.create_job(user_id=user["user_id"], payload=payload.model_dump())
    run_processing_job.delay(job.id)
    return JobResponse(
        id=job.id,
        status=job.status,
        progress=job.progress,
        created_at=job.created_at,
        updated_at=job.updated_at,
        summary=job.summary,
        error_message=job.error_message,
        result_file_id=job.result_file_id,
    )


@router.get("", response_model=JobListResponse)
def list_jobs(limit: int = 20, offset: int = 0, user=Depends(get_current_user), db: Session = Depends(get_db)):
    service = JobService(db)
    items, total = service.list_jobs(user_id=user["user_id"], limit=limit, offset=offset)
    return JobListResponse(
        items=[
            JobResponse(
                id=item.id,
                status=item.status,
                progress=item.progress,
                created_at=item.created_at,
                updated_at=item.updated_at,
                summary=item.summary,
                error_message=item.error_message,
                result_file_id=item.result_file_id,
            )
            for item in items
        ],
        total=total,
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    service = JobService(db)
    job = service.get_job(user_id=user["user_id"], job_id=job_id)
    return JobResponse(
        id=job.id,
        status=job.status,
        progress=job.progress,
        created_at=job.created_at,
        updated_at=job.updated_at,
        summary=job.summary,
        error_message=job.error_message,
        result_file_id=job.result_file_id,
    )


@router.get("/{job_id}/result")
def get_job_result(job_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    service = JobService(db)
    job = service.get_job(user_id=user["user_id"], job_id=job_id)
    if not job.result_file_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resultado ainda não disponível.")
    file_obj = service.file_service.get_file(job.result_file_id, user["user_id"])
    return {"file_id": file_obj.id, "original_name": file_obj.original_name, "download_path": file_obj.storage_path}


@router.get("/{job_id}/result/download")
def download_job_result(job_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    service = JobService(db)
    job = service.get_job(user_id=user["user_id"], job_id=job_id)
    if not job.result_file_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resultado ainda não disponível.")
    file_obj = service.file_service.get_file(job.result_file_id, user["user_id"])
    return FileResponse(
        path=file_obj.storage_path,
        filename=file_obj.original_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
