import * as XLSX from "xlsx";

type CellValue = string | number | null;

export type BrowserSheetPreview = {
  sheet_name: string;
  columns: string[];
  preview_rows: Record<string, CellValue>[];
};

const workbookCache = new WeakMap<File, XLSX.WorkBook>();

function toDisplayValue(value: unknown): CellValue {
  if (value === undefined || value === null || value === "") return "";
  if (typeof value === "number") return value;
  return String(value);
}

function normalizeColumns(headerValues: unknown[]): string[] {
  const seen = new Map<string, number>();

  return headerValues.map((value, index) => {
    const base = String(value ?? "").trim() || `Unnamed: ${index}`;
    const count = seen.get(base) ?? 0;
    seen.set(base, count + 1);
    return count === 0 ? base : `${base}.${count}`;
  });
}

async function getWorkbook(file: File): Promise<XLSX.WorkBook> {
  const cached = workbookCache.get(file);
  if (cached) return cached;

  const buffer = await file.arrayBuffer();
  const workbook = XLSX.read(buffer, {
    type: "array",
    dense: true,
    cellDates: false,
  });
  workbookCache.set(file, workbook);
  return workbook;
}

export async function getWorkbookSheets(file: File): Promise<string[]> {
  const workbook = await getWorkbook(file);
  return workbook.SheetNames;
}

export async function inspectLocalSheet(
  file: File,
  sheetName: string,
  headerRow: number,
  previewLimit = 5,
): Promise<BrowserSheetPreview> {
  const workbook = await getWorkbook(file);
  const resolvedSheetName = workbook.SheetNames.includes(sheetName) ? sheetName : workbook.SheetNames[0];
  const sheet = workbook.Sheets[resolvedSheetName];
  const rows = XLSX.utils.sheet_to_json<unknown[]>(sheet, {
    header: 1,
    raw: false,
    defval: "",
    blankrows: false,
  });

  const headerIndex = Math.max(0, headerRow - 1);
  const headerValues = rows[headerIndex] ?? [];
  const columns = normalizeColumns(Array.isArray(headerValues) ? headerValues : []);

  const previewRows = rows.slice(headerIndex + 1, headerIndex + 1 + previewLimit).map((rowValues) => {
    const rowArray = Array.isArray(rowValues) ? rowValues : [];
    return columns.reduce<Record<string, CellValue>>((acc, column, index) => {
      acc[column] = toDisplayValue(rowArray[index]);
      return acc;
    }, {});
  });

  return {
    sheet_name: resolvedSheetName,
    columns,
    preview_rows: previewRows,
  };
}
