from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class FileKind(str, Enum):
    BASE = "base"
    DESTINO = "destino"
    RESULTADO = "resultado"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class StoredFile(Base):
    __tablename__ = "stored_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    kind: Mapped[FileKind] = mapped_column(SAEnum(FileKind))
    original_name: Mapped[str] = mapped_column(String(255))
    storage_path: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(128), default="application/octet-stream")
    size_bytes: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    base_file_id: Mapped[str] = mapped_column(ForeignKey("stored_files.id"), index=True)
    destino_file_id: Mapped[str] = mapped_column(ForeignKey("stored_files.id"), index=True)
    result_file_id: Mapped[str | None] = mapped_column(ForeignKey("stored_files.id"), nullable=True)
    status: Mapped[JobStatus] = mapped_column(SAEnum(JobStatus), default=JobStatus.QUEUED, index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    mapping_payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(64))
    max_file_mb: Mapped[int] = mapped_column(Integer, default=30)
    max_jobs_month: Mapped[int] = mapped_column(Integer, default=50)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    plan_code: Mapped[str] = mapped_column(String(32), default="free")
    provider: Mapped[str] = mapped_column(String(32), default="stripe")
    provider_customer_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provider_subscription_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="inactive")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

