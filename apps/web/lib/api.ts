const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

type ApiOptions = RequestInit & {
  userId?: string;
  userEmail?: string;
  isFormData?: boolean;
};

export type UploadResponse = {
  file_id: string;
  original_name: string;
  kind: "base" | "destino";
  size_bytes: number;
  created_at: string;
};

export type SheetPreview = {
  sheet_name: string;
  columns: string[];
  preview_rows: Record<string, string | number | null>[];
};

export type FileInspectResponse = {
  file_id: string;
  sheets: string[];
  previews: SheetPreview[];
};

export type SheetInspectResponse = {
  sheet_name: string;
  columns: string[];
  preview_rows: Record<string, string | number | null>[];
};

export type FileSheetsResponse = {
  file_id: string;
  sheets: string[];
};

export type JobResponse = {
  id: string;
  status: "queued" | "running" | "succeeded" | "failed";
  progress: number;
  created_at: string;
  updated_at: string;
  summary?: {
    rows_total: number;
    rows_item: number;
    rows_low_confidence: number;
    rows_no_match: number;
    rows_title: number;
    rows_empty: number;
  };
  error_message?: string | null;
  result_file_id?: string | null;
};

type JobListResponse = {
  items: JobResponse[];
  total: number;
};

function buildHeaders(options: ApiOptions): Headers {
  const headers = new Headers(options.headers || {});
  headers.set("x-user-id", options.userId || "demo-user");
  headers.set("x-user-email", options.userEmail || "demo@local.test");
  if (!options.isFormData && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  return headers;
}

async function apiFetch<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: buildHeaders(options)
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `API error ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function uploadFile(kind: "base" | "destino", file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("upload", file);
  return apiFetch<UploadResponse>(`/files/upload?kind=${kind}`, {
    method: "POST",
    body: formData,
    isFormData: true
  });
}

export async function inspectFile(fileId: string, headerRow: number): Promise<FileInspectResponse> {
  return apiFetch<FileInspectResponse>(`/files/${fileId}/inspect?header_row=${headerRow}`);
}

export async function getFileSheets(fileId: string): Promise<FileSheetsResponse> {
  return apiFetch<FileSheetsResponse>(`/files/${fileId}/sheets`);
}

export async function inspectSheet(
  fileId: string,
  sheetName: string,
  headerRow: number
): Promise<SheetInspectResponse> {
  return apiFetch<SheetInspectResponse>(
    `/files/${fileId}/sheet?sheet_name=${encodeURIComponent(sheetName)}&header_row=${headerRow}`
  );
}

export async function createJob(payload: unknown): Promise<JobResponse> {
  return apiFetch<JobResponse>("/jobs", { method: "POST", body: JSON.stringify(payload) });
}

export async function getJob(jobId: string): Promise<JobResponse> {
  return apiFetch<JobResponse>(`/jobs/${jobId}`);
}

export async function listJobs(): Promise<JobListResponse> {
  return apiFetch<JobListResponse>("/jobs");
}

export function buildResultDownloadUrl(jobId: string): string {
  return `${API_BASE_URL}/jobs/${jobId}/result/download`;
}

export async function downloadJobResult(jobId: string): Promise<Blob> {
  const response = await fetch(buildResultDownloadUrl(jobId), {
    headers: buildHeaders({})
  });
  if (!response.ok) {
    throw new Error(`Erro ao baixar resultado (${response.status})`);
  }
  return await response.blob();
}
