from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import FileKind, StoredFile


class FileService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.storage_dir = Path(self.settings.storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(self, user_id: str, upload: UploadFile, kind: FileKind) -> StoredFile:
        ext = Path(upload.filename or "").suffix.lower()
        if ext not in {".xlsx", ".xlsm", ".xls"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de arquivo não suportado.")

        max_bytes = self.settings.max_upload_size_mb * 1024 * 1024
        file_id = str(uuid4())
        user_dir = self.storage_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        file_path = user_dir / f"{file_id}{ext}"

        size_bytes = 0
        upload.file.seek(0)
        with file_path.open("wb") as destination:
            while True:
                chunk = upload.file.read(1024 * 1024)
                if not chunk:
                    break
                size_bytes += len(chunk)
                if size_bytes > max_bytes:
                    destination.close()
                    file_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Arquivo excede {self.settings.max_upload_size_mb}MB.",
                    )
                destination.write(chunk)

        db_file = StoredFile(
            id=file_id,
            user_id=user_id,
            kind=kind,
            original_name=upload.filename or f"arquivo{ext}",
            storage_path=str(file_path),
            content_type=upload.content_type or "application/octet-stream",
            size_bytes=size_bytes,
        )
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        return db_file

    def get_file(self, file_id: str, user_id: str) -> StoredFile:
        db_file = self.db.get(StoredFile, file_id)
        if not db_file or db_file.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado.")
        return db_file

    def open_as_bytesio(self, db_file: StoredFile) -> BytesIO:
        data = Path(db_file.storage_path).read_bytes()
        stream = BytesIO(data)
        stream.seek(0)
        return stream

    def save_result(self, user_id: str, original_name: str, content: bytes) -> StoredFile:
        file_id = str(uuid4())
        user_dir = self.storage_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        file_path = user_dir / f"{file_id}.xlsx"
        file_path.write_bytes(content)

        db_file = StoredFile(
            id=file_id,
            user_id=user_id,
            kind=FileKind.RESULTADO,
            original_name=original_name,
            storage_path=str(file_path),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            size_bytes=len(content),
        )
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        return db_file
