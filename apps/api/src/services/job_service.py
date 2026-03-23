from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from core.excel_io import aplicar_resultado_no_excel_original, carregar_excel, obter_nome_coluna_referencia
from core.pipeline import processar_preenchimento

from ..models import JobStatus, ProcessingJob, StoredFile
from .file_service import FileService


@dataclass
class JobRunResult:
    summary: dict
    result_file_id: str


class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.file_service = FileService(db)

    def create_job(self, user_id: str, payload: dict) -> ProcessingJob:
        self.file_service.get_file(payload["base_file_id"], user_id)
        self.file_service.get_file(payload["destino_file_id"], user_id)
        if not payload.get("mappings"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mapeamento de colunas é obrigatório.")
        destino_cols = [item["destino_column"] for item in payload["mappings"]]
        if len(set(destino_cols)) != len(destino_cols):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Colunas de destino não podem ser repetidas no mapeamento.",
            )

        job = ProcessingJob(
            id=str(uuid4()),
            user_id=user_id,
            base_file_id=payload["base_file_id"],
            destino_file_id=payload["destino_file_id"],
            status=JobStatus.QUEUED,
            progress=0,
            mapping_payload=payload,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def list_jobs(self, user_id: str, limit: int = 20, offset: int = 0):
        query = select(ProcessingJob).where(ProcessingJob.user_id == user_id).order_by(ProcessingJob.created_at.desc())
        items = self.db.execute(query.limit(limit).offset(offset)).scalars().all()
        total = self.db.execute(
            select(func.count()).select_from(ProcessingJob).where(ProcessingJob.user_id == user_id)
        ).scalar_one()
        return items, total

    def get_job(self, user_id: str, job_id: str) -> ProcessingJob:
        job = self.db.get(ProcessingJob, job_id)
        if not job or job.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job não encontrado.")
        return job

    def run_job(self, job_id: str):
        job = self.db.get(ProcessingJob, job_id)
        if not job:
            return

        payload = job.mapping_payload
        job.status = JobStatus.RUNNING
        job.progress = 1
        self.db.commit()

        try:
            base_file = self.db.get(StoredFile, payload["base_file_id"])
            destino_file = self.db.get(StoredFile, payload["destino_file_id"])
            if not base_file or not destino_file:
                raise FileNotFoundError("Arquivo base ou destino não encontrado para execução.")

            base_stream = BytesIO(Path(base_file.storage_path).read_bytes())
            destino_stream = BytesIO(Path(destino_file.storage_path).read_bytes())

            df_base = carregar_excel(base_stream, payload["base_sheet"], payload["base_header_row"] - 1)
            df_destino = carregar_excel(destino_stream, payload["destino_sheet"], payload["destino_header_row"] - 1)

            colunas_base = [item["base_column"] for item in payload["mappings"]]
            colunas_destino = [item["destino_column"] for item in payload["mappings"]]

            def update_progress(progress: float, _message: str):
                job.progress = int(progress * 100)
                self.db.commit()

            resultado = processar_preenchimento(
                df_base=df_base,
                df_destino=df_destino,
                coluna_busca_destino=payload["coluna_busca_destino"],
                colunas_base_retorno=colunas_base,
                colunas_destino_preencher=colunas_destino,
                coluna_texto_base=payload["coluna_texto_base"],
                score_minimo=payload["score_minimo"],
                top_k_candidatos=payload["top_k_candidatos"],
                progress_callback=update_progress,
            )

            destino_original_stream = BytesIO(Path(destino_file.storage_path).read_bytes())
            excel_bytes = aplicar_resultado_no_excel_original(
                uploaded_file=destino_original_stream,
                nome_aba=payload["destino_sheet"],
                header_index=payload["destino_header_row"] - 1,
                df_original=df_destino,
                df_resultado=resultado,
                colunas_destino_preencher=colunas_destino,
                nome_coluna_referencia=obter_nome_coluna_referencia(payload["coluna_texto_base"]),
            )

            result_file = self.file_service.save_result(
                user_id=job.user_id,
                original_name=f"resultado_{job.id}.xlsx",
                content=excel_bytes,
            )

            summary = self.build_summary(resultado)
            job.status = JobStatus.SUCCEEDED
            job.progress = 100
            job.summary = summary
            job.result_file_id = result_file.id
            job.error_message = None
            self.db.commit()
        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            self.db.commit()

    @staticmethod
    def build_summary(df_resultado: pd.DataFrame) -> dict:
        tipo_col = "IA_TIPO_LINHA"
        counts = df_resultado[tipo_col].fillna("").value_counts().to_dict() if tipo_col in df_resultado.columns else {}
        return {
            "rows_total": int(len(df_resultado)),
            "rows_item": int(counts.get("Item", 0)),
            "rows_low_confidence": int(counts.get("Item, confiança baixa", 0)),
            "rows_no_match": int(counts.get("Sem correspondência", 0)),
            "rows_title": int(counts.get("Título/Subtítulo", 0)),
            "rows_empty": int(counts.get("Vazia", 0)),
        }
