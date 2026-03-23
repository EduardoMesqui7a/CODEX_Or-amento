import pandas as pd

from core.excel_io import carregar_excel

from .file_service import FileService


class WorkbookInspectService:
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def inspect(self, file_id: str, user_id: str, header_row: int = 1):
        db_file = self.file_service.get_file(file_id, user_id)
        stream = self.file_service.open_as_bytesio(db_file)
        excel = pd.ExcelFile(stream)

        previews = []
        for sheet_name in excel.sheet_names[:3]:
            try:
                stream.seek(0)
                df = carregar_excel(stream, sheet_name, header_row - 1)
                previews.append(
                    {
                        "sheet_name": sheet_name,
                        "columns": [str(c) for c in df.columns.tolist()],
                        "preview_rows": df.head(5).fillna("").to_dict("records"),
                    }
                )
            except Exception:
                continue

        return {"file_id": file_id, "sheets": excel.sheet_names, "previews": previews}

    def inspect_sheet(self, file_id: str, user_id: str, sheet_name: str, header_row: int = 1):
        db_file = self.file_service.get_file(file_id, user_id)
        stream = self.file_service.open_as_bytesio(db_file)
        df = carregar_excel(stream, sheet_name, header_row - 1)
        return {
            "sheet_name": sheet_name,
            "columns": [str(c) for c in df.columns.tolist()],
            "preview_rows": df.head(10).fillna("").to_dict("records"),
        }
