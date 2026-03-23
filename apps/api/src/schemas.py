from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from .models import JobStatus


class UploadResponse(BaseModel):
    file_id: str
    original_name: str
    kind: Literal["base", "destino"]
    size_bytes: int
    created_at: datetime


class SheetPreview(BaseModel):
    sheet_name: str
    columns: List[str]
    preview_rows: List[dict]


class FileInspectResponse(BaseModel):
    file_id: str
    sheets: List[str]
    previews: List[SheetPreview]


class SheetInspectResponse(BaseModel):
    sheet_name: str
    columns: List[str]
    preview_rows: List[dict]


class ColumnMapping(BaseModel):
    base_column: str
    destino_column: str


class JobCreatePayload(BaseModel):
    base_file_id: str
    destino_file_id: str
    base_sheet: str
    destino_sheet: str
    base_header_row: int = Field(1, ge=1)
    destino_header_row: int = Field(1, ge=1)
    coluna_busca_destino: str
    coluna_texto_base: str
    mappings: List[ColumnMapping]
    score_minimo: float = Field(0.35, ge=0, le=1)
    top_k_candidatos: int = Field(30, ge=1, le=100)


class JobSummary(BaseModel):
    rows_total: int
    rows_item: int
    rows_low_confidence: int
    rows_no_match: int
    rows_title: int
    rows_empty: int


class JobResponse(BaseModel):
    id: str
    status: JobStatus
    progress: int
    created_at: datetime
    updated_at: datetime
    summary: Optional[JobSummary] = None
    error_message: Optional[str] = None
    result_file_id: Optional[str] = None


class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int


class SessionVerifyResponse(BaseModel):
    user_id: str
    email: str
    authenticated: bool
