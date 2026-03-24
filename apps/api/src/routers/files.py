from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..db import get_db
from ..models import FileKind
from ..schemas import FileInspectResponse, SheetInspectResponse, UploadResponse
from ..services.file_service import FileService
from ..services.workbook_service import WorkbookInspectService

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=UploadResponse)
def upload_file(
    kind: FileKind,
    upload: UploadFile = File(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FileService(db)
    stored = service.save_upload(user_id=user["user_id"], upload=upload, kind=kind)
    return UploadResponse(
        file_id=stored.id,
        original_name=stored.original_name,
        kind=stored.kind.value,
        size_bytes=stored.size_bytes,
        created_at=stored.created_at,
    )


@router.get("/{file_id}/inspect", response_model=FileInspectResponse)
def inspect_file(file_id: str, header_row: int = 1, user=Depends(get_current_user), db: Session = Depends(get_db)):
    file_service = FileService(db)
    service = WorkbookInspectService(file_service)
    return service.inspect(file_id=file_id, user_id=user["user_id"], header_row=header_row)


@router.get("/{file_id}/sheets")
def list_sheets(file_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    file_service = FileService(db)
    service = WorkbookInspectService(file_service)
    return service.list_sheet_names(file_id=file_id, user_id=user["user_id"])


@router.get("/{file_id}/sheet", response_model=SheetInspectResponse)
def inspect_sheet(
    file_id: str,
    sheet_name: str,
    header_row: int = 1,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_service = FileService(db)
    service = WorkbookInspectService(file_service)
    return service.inspect_sheet(file_id=file_id, user_id=user["user_id"], sheet_name=sheet_name, header_row=header_row)
