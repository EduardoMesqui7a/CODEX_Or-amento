"use client";

import { useEffect, useMemo, useState } from "react";
import { Loader2, UploadCloud } from "lucide-react";

import { type SheetInspectResponse } from "@/lib/api";
import { AppShell } from "@/components/app-shell";
import { inspectLocalSheet, getWorkbookSheets } from "@/lib/excel-browser";
import { createJob, downloadJobResult, getJob, type JobResponse, uploadFile } from "@/lib/api";

type MappingRow = {
  base_column: string;
  destino_column: string;
};

const steps = ["Arquivos locais", "Abas e Cabecalhos", "Mapeamento", "Processamento"];

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function getFileKey(file: File | null) {
  return file ? `${file.name}-${file.size}-${file.lastModified}` : "";
}

export default function NewProcessingPage() {
  const [baseFile, setBaseFile] = useState<File | null>(null);
  const [destinoFile, setDestinoFile] = useState<File | null>(null);
  const [baseFileId, setBaseFileId] = useState("");
  const [destinoFileId, setDestinoFileId] = useState("");
  const [baseUploadKey, setBaseUploadKey] = useState("");
  const [destinoUploadKey, setDestinoUploadKey] = useState("");
  const [baseSheets, setBaseSheets] = useState<string[]>([]);
  const [destinoSheets, setDestinoSheets] = useState<string[]>([]);
  const [baseSheet, setBaseSheet] = useState("");
  const [destinoSheet, setDestinoSheet] = useState("");
  const [baseHeaderRow, setBaseHeaderRow] = useState(1);
  const [destinoHeaderRow, setDestinoHeaderRow] = useState(1);
  const [baseInspect, setBaseInspect] = useState<SheetInspectResponse | null>(null);
  const [destinoInspect, setDestinoInspect] = useState<SheetInspectResponse | null>(null);
  const [colunaTextoBase, setColunaTextoBase] = useState("");
  const [colunaBuscaDestino, setColunaBuscaDestino] = useState("");
  const [mappings, setMappings] = useState<MappingRow[]>([{ base_column: "", destino_column: "" }]);
  const [scoreMinimo, setScoreMinimo] = useState(0.35);
  const [topK, setTopK] = useState(30);
  const [job, setJob] = useState<JobResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!job || (job.status !== "queued" && job.status !== "running")) return;
    const interval = setInterval(async () => {
      try {
        const updated = await getJob(job.id);
        setJob(updated);
      } catch {
        // Ignore transient polling errors.
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [job]);

  const mappingValid = useMemo(() => {
    const filtered = mappings.filter((item) => item.base_column && item.destino_column);
    if (filtered.length === 0) return false;
    const destinoSet = new Set(filtered.map((item) => item.destino_column));
    return destinoSet.size === filtered.length;
  }, [mappings]);

  const basePreviewColumns = useMemo(() => baseInspect?.columns.slice(0, 4) ?? [], [baseInspect]);
  const destinoPreviewColumns = useMemo(() => destinoInspect?.columns.slice(0, 4) ?? [], [destinoInspect]);

  function resetWorkflow() {
    setBaseFileId("");
    setDestinoFileId("");
    setBaseUploadKey("");
    setDestinoUploadKey("");
    setBaseSheets([]);
    setDestinoSheets([]);
    setBaseSheet("");
    setDestinoSheet("");
    setBaseInspect(null);
    setDestinoInspect(null);
    setColunaTextoBase("");
    setColunaBuscaDestino("");
    setMappings([{ base_column: "", destino_column: "" }]);
    setJob(null);
    setMessage("");
    setError("");
  }

  function updateSelectedFile(kind: "base" | "destino", file: File | null) {
    resetWorkflow();
    if (kind === "base") {
      setBaseFile(file);
      setDestinoFile((current) => current);
      return;
    }
    setDestinoFile(file);
    setBaseFile((current) => current);
  }

  async function handlePrepareFiles() {
    if (!baseFile || !destinoFile) {
      setError("Selecione os dois arquivos antes de continuar.");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("Lendo arquivos localmente no navegador...");

    try {
      const [baseSheetNames, destinoSheetNames] = await Promise.all([
        getWorkbookSheets(baseFile),
        getWorkbookSheets(destinoFile),
      ]);

      setBaseSheets(baseSheetNames);
      setDestinoSheets(destinoSheetNames);
      setBaseSheet(baseSheetNames[0] || "");
      setDestinoSheet(destinoSheetNames[0] || "");
      setMessage("Arquivos lidos localmente. Agora selecione as abas e carregue as colunas.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao ler os arquivos localmente.");
    } finally {
      setLoading(false);
    }
  }

  async function handleLoadColumns() {
    if (!baseFile || !destinoFile || !baseSheet || !destinoSheet) {
      setError("Selecione os arquivos e as abas para carregar colunas.");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("Montando previas e colunas localmente...");

    try {
      const [baseData, destinoData] = await Promise.all([
        inspectLocalSheet(baseFile, baseSheet, baseHeaderRow),
        inspectLocalSheet(destinoFile, destinoSheet, destinoHeaderRow),
      ]);

      setBaseInspect(baseData);
      setDestinoInspect(destinoData);
      setColunaTextoBase(baseData.columns[0] || "");
      setColunaBuscaDestino(destinoData.columns[0] || "");
      setMappings([
        {
          base_column: baseData.columns[0] || "",
          destino_column: destinoData.columns[0] || "",
        },
      ]);
      setMessage("Colunas carregadas localmente. Revise o mapeamento e clique em Criar job.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar colunas.");
    } finally {
      setLoading(false);
    }
  }

  function updateMapping(index: number, field: keyof MappingRow, value: string) {
    setMappings((prev) => prev.map((item, i) => (i === index ? { ...item, [field]: value } : item)));
  }

  function addMappingRow() {
    setMappings((prev) => [...prev, { base_column: "", destino_column: "" }]);
  }

  function removeMappingRow(index: number) {
    setMappings((prev) => prev.filter((_, i) => i !== index));
  }

  async function ensureRemoteUploads() {
    if (!baseFile || !destinoFile) {
      throw new Error("Arquivos locais nao encontrados.");
    }

    const currentBaseKey = getFileKey(baseFile);
    const currentDestinoKey = getFileKey(destinoFile);

    let resolvedBaseFileId = baseFileId;
    let resolvedDestinoFileId = destinoFileId;

    if (!resolvedBaseFileId || baseUploadKey !== currentBaseKey) {
      const baseRes = await uploadFile("base", baseFile);
      resolvedBaseFileId = baseRes.file_id;
      setBaseFileId(baseRes.file_id);
      setBaseUploadKey(currentBaseKey);
    }

    if (!resolvedDestinoFileId || destinoUploadKey !== currentDestinoKey) {
      const destinoRes = await uploadFile("destino", destinoFile);
      resolvedDestinoFileId = destinoRes.file_id;
      setDestinoFileId(destinoRes.file_id);
      setDestinoUploadKey(currentDestinoKey);
    }

    return { resolvedBaseFileId, resolvedDestinoFileId };
  }

  async function handleCreateJob() {
    if (!baseFile || !destinoFile || !baseInspect || !destinoInspect) {
      setError("Complete a leitura local e a inspecao antes de criar o job.");
      return;
    }

    if (!mappingValid) {
      setError("Mapeamento invalido. Verifique colunas vazias ou repetidas.");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("Enviando arquivos ao servidor...");

    try {
      const { resolvedBaseFileId, resolvedDestinoFileId } = await ensureRemoteUploads();

      setMessage("Criando job e iniciando processamento...");

      const payload = {
        base_file_id: resolvedBaseFileId,
        destino_file_id: resolvedDestinoFileId,
        base_sheet: baseSheet,
        destino_sheet: destinoSheet,
        base_header_row: baseHeaderRow,
        destino_header_row: destinoHeaderRow,
        coluna_busca_destino: colunaBuscaDestino,
        coluna_texto_base: colunaTextoBase,
        mappings: mappings.filter((item) => item.base_column && item.destino_column),
        score_minimo: scoreMinimo,
        top_k_candidatos: topK,
      };

      const created = await createJob(payload);
      setJob(created);
      setMessage("Job criado. Agora o progresso segue em tempo real.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel criar o job.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDownloadResult() {
    if (!job) return;

    setLoading(true);
    setError("");
    try {
      const blob = await downloadJobResult(job.id);
      downloadBlob(blob, `resultado_${job.id}.xlsx`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro no download do resultado.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-semibold">Novo Processamento</h2>
          <p className="mt-1 text-sm text-slate-600">
            O navegador le o Excel localmente para abas, colunas e previas. O upload so acontece quando voce confirma o processamento.
          </p>
        </div>

        <section className="grid gap-3 md:grid-cols-4">
          {steps.map((step, index) => (
            <div key={step} className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Passo {index + 1}</p>
              <p className="mt-2 font-medium">{step}</p>
            </div>
          ))}
        </section>

        <section className="grid gap-4 xl:grid-cols-2">
          <article className="rounded-2xl bg-white p-5">
            <h3 className="font-semibold">1) Leitura local</h3>
            <p className="mt-1 text-sm text-slate-600">Escolha os arquivos. Nada sobe para o servidor nesta etapa.</p>
            <div className="mt-4 grid gap-3">
              <label className="rounded-xl border border-dashed border-slate-300 p-4">
                <span className="mb-2 flex items-center gap-2 text-sm text-slate-500">
                  <UploadCloud size={16} /> Arquivo base
                </span>
                <input
                  type="file"
                  accept=".xlsx,.xlsm,.xls"
                  onChange={(e) => updateSelectedFile("base", e.target.files?.[0] || null)}
                />
              </label>
              <label className="rounded-xl border border-dashed border-slate-300 p-4">
                <span className="mb-2 flex items-center gap-2 text-sm text-slate-500">
                  <UploadCloud size={16} /> Planilha destino
                </span>
                <input
                  type="file"
                  accept=".xlsx,.xlsm,.xls"
                  onChange={(e) => updateSelectedFile("destino", e.target.files?.[0] || null)}
                />
              </label>
              <button
                onClick={handlePrepareFiles}
                disabled={loading}
                className="rounded-xl bg-ink px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
              >
                {loading ? "Lendo..." : "Ler arquivos localmente"}
              </button>
            </div>
          </article>

          <article className="rounded-2xl bg-white p-5">
            <h3 className="font-semibold">2) Abas e cabecalhos</h3>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <div>
                <label className="mb-1 block text-xs uppercase tracking-[0.15em] text-slate-500">Aba base</label>
                <select
                  value={baseSheet}
                  onChange={(e) => setBaseSheet(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 px-3 py-2"
                >
                  {baseSheets.map((sheet) => (
                    <option key={sheet} value={sheet}>
                      {sheet}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-xs uppercase tracking-[0.15em] text-slate-500">Aba destino</label>
                <select
                  value={destinoSheet}
                  onChange={(e) => setDestinoSheet(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 px-3 py-2"
                >
                  {destinoSheets.map((sheet) => (
                    <option key={sheet} value={sheet}>
                      {sheet}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-xs uppercase tracking-[0.15em] text-slate-500">Header base</label>
                <input
                  type="number"
                  min={1}
                  value={baseHeaderRow}
                  onChange={(e) => setBaseHeaderRow(Number(e.target.value || 1))}
                  className="w-full rounded-xl border border-slate-300 px-3 py-2"
                />
              </div>
              <div>
                <label className="mb-1 block text-xs uppercase tracking-[0.15em] text-slate-500">Header destino</label>
                <input
                  type="number"
                  min={1}
                  value={destinoHeaderRow}
                  onChange={(e) => setDestinoHeaderRow(Number(e.target.value || 1))}
                  className="w-full rounded-xl border border-slate-300 px-3 py-2"
                />
              </div>
            </div>
            <button
              onClick={handleLoadColumns}
              disabled={loading || !baseFile || !destinoFile || !baseSheet || !destinoSheet}
              className="mt-4 rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium disabled:opacity-50"
            >
              Carregar colunas
            </button>
          </article>
        </section>

        <section className="rounded-2xl bg-white p-5">
          <h3 className="font-semibold">3) Mapeamento e parametros</h3>
          <div className="mt-4 grid gap-3 lg:grid-cols-4">
            <div>
              <label className="mb-1 block text-xs uppercase tracking-[0.15em] text-slate-500">Coluna texto base</label>
              <select
                value={colunaTextoBase}
                onChange={(e) => setColunaTextoBase(e.target.value)}
                className="w-full rounded-xl border border-slate-300 px-3 py-2"
              >
                {baseInspect?.columns.map((col) => (
                  <option key={col} value={col}>
                    {col}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs uppercase tracking-[0.15em] text-slate-500">Coluna busca destino</label>
              <select
                value={colunaBuscaDestino}
                onChange={(e) => setColunaBuscaDestino(e.target.value)}
                className="w-full rounded-xl border border-slate-300 px-3 py-2"
              >
                {destinoInspect?.columns.map((col) => (
                  <option key={col} value={col}>
                    {col}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs uppercase tracking-[0.15em] text-slate-500">Score minimo</label>
              <input
                type="number"
                step={0.01}
                min={0}
                max={1}
                value={scoreMinimo}
                onChange={(e) => setScoreMinimo(Number(e.target.value || 0.35))}
                className="w-full rounded-xl border border-slate-300 px-3 py-2"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs uppercase tracking-[0.15em] text-slate-500">Top K candidatos</label>
              <input
                type="number"
                min={1}
                max={100}
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value || 30))}
                className="w-full rounded-xl border border-slate-300 px-3 py-2"
              />
            </div>
          </div>

          <div className="mt-4 space-y-2">
            {mappings.map((mapping, idx) => (
              <div key={`${idx}-${mapping.base_column}-${mapping.destino_column}`} className="grid gap-2 md:grid-cols-[1fr_1fr_auto]">
                <select
                  value={mapping.base_column}
                  onChange={(e) => updateMapping(idx, "base_column", e.target.value)}
                  className="rounded-xl border border-slate-300 px-3 py-2"
                >
                  <option value="">Selecione coluna base</option>
                  {baseInspect?.columns.map((col) => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
                <select
                  value={mapping.destino_column}
                  onChange={(e) => updateMapping(idx, "destino_column", e.target.value)}
                  className="rounded-xl border border-slate-300 px-3 py-2"
                >
                  <option value="">Selecione coluna destino</option>
                  {destinoInspect?.columns.map((col) => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
                <button
                  onClick={() => removeMappingRow(idx)}
                  className="rounded-xl border border-red-200 px-3 py-2 text-sm text-red-600"
                >
                  Remover
                </button>
              </div>
            ))}
          </div>

          <div className="mt-3 flex flex-wrap gap-2">
            <button onClick={addMappingRow} className="rounded-xl border border-slate-300 px-3 py-2 text-sm">
              Adicionar mapeamento
            </button>
            <button
              onClick={handleCreateJob}
              disabled={loading || !mappingValid}
              className="rounded-xl bg-ink px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {loading ? "Criando..." : "Criar job"}
            </button>
          </div>
        </section>

        {(baseInspect || destinoInspect) && (
          <section className="grid gap-4 xl:grid-cols-2">
            <article className="rounded-2xl bg-white p-5">
              <h4 className="font-semibold">Previa da base</h4>
              {!baseInspect && <p className="mt-2 text-sm text-slate-500">Sem previa carregada.</p>}
              {baseInspect && (
                <div className="mt-3 overflow-x-auto rounded-xl border border-slate-100">
                  <table className="min-w-full text-left text-xs">
                    <thead className="bg-slate-50">
                      <tr>
                        {basePreviewColumns.map((col) => (
                          <th key={col} className="px-2 py-2 font-medium text-slate-600">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {baseInspect.preview_rows.slice(0, 3).map((row, idx) => (
                        <tr key={idx} className="border-t border-slate-100">
                          {basePreviewColumns.map((col) => (
                            <td key={`${idx}-${col}`} className="max-w-[180px] px-2 py-2 text-slate-600">
                              {String(row[col] ?? "")}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </article>

            <article className="rounded-2xl bg-white p-5">
              <h4 className="font-semibold">Previa da destino</h4>
              {!destinoInspect && <p className="mt-2 text-sm text-slate-500">Sem previa carregada.</p>}
              {destinoInspect && (
                <div className="mt-3 overflow-x-auto rounded-xl border border-slate-100">
                  <table className="min-w-full text-left text-xs">
                    <thead className="bg-slate-50">
                      <tr>
                        {destinoPreviewColumns.map((col) => (
                          <th key={col} className="px-2 py-2 font-medium text-slate-600">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {destinoInspect.preview_rows.slice(0, 3).map((row, idx) => (
                        <tr key={idx} className="border-t border-slate-100">
                          {destinoPreviewColumns.map((col) => (
                            <td key={`${idx}-${col}`} className="max-w-[180px] px-2 py-2 text-slate-600">
                              {String(row[col] ?? "")}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </article>
          </section>
        )}

        <section className="rounded-2xl bg-white p-5">
          <h3 className="font-semibold">4) Status do job</h3>
          {!job && <p className="mt-2 text-sm text-slate-500">Ainda nao ha job criado.</p>}
          {job && (
            <div className="mt-3 space-y-3">
              <p className="text-sm">
                <span className="font-medium">Job:</span> {job.id}
              </p>
              <p className="text-sm">
                <span className="font-medium">Status:</span> {job.status}
              </p>
              <div className="h-3 w-full rounded-full bg-slate-100">
                <div className="h-3 rounded-full bg-ink transition-all" style={{ width: `${job.progress}%` }} />
              </div>
              <p className="text-xs text-slate-500">{job.progress}% concluido</p>
              {job.summary && (
                <p className="text-sm text-slate-600">
                  Total: {job.summary.rows_total} | Itens: {job.summary.rows_item} | Baixa confianca: {job.summary.rows_low_confidence}
                </p>
              )}
              {job.status === "succeeded" && (
                <button onClick={handleDownloadResult} className="rounded-xl bg-emerald-600 px-4 py-2 text-sm text-white">
                  Baixar resultado
                </button>
              )}
              {job.status === "failed" && <p className="text-sm text-red-600">Falha: {job.error_message || "erro interno"}</p>}
            </div>
          )}
        </section>

        {(message || error) && (
          <section className="rounded-2xl bg-white p-4">
            {message && (
              <p className="flex items-center gap-2 text-sm text-slate-700">
                {loading && <Loader2 size={14} className="animate-spin" />} {message}
              </p>
            )}
            {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
          </section>
        )}
      </div>
    </AppShell>
  );
}
