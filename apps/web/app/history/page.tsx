"use client";

import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { downloadJobResult, listJobs, type JobResponse } from "@/lib/api";

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export default function HistoryPage() {
  const [items, setItems] = useState<JobResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    try {
      const response = await listJobs();
      setItems(response.items);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar histórico.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 2500);
    return () => clearInterval(interval);
  }, []);

  async function handleDownload(jobId: string) {
    try {
      const blob = await downloadJobResult(jobId);
      downloadBlob(blob, `resultado_${jobId}.xlsx`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro no download.");
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-semibold">Histórico</h2>
          <p className="mt-1 text-sm text-slate-600">Jobs com status em tempo real e acesso ao arquivo final.</p>
        </div>

        {error && <div className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

        <div className="overflow-x-auto rounded-2xl bg-white">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3">Job</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Progresso</th>
                <th className="px-4 py-3">Criado em</th>
                <th className="px-4 py-3">Ação</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr className="border-t border-slate-100">
                  <td className="px-4 py-4 text-slate-500" colSpan={5}>
                    Carregando histórico...
                  </td>
                </tr>
              )}
              {!loading && items.length === 0 && (
                <tr className="border-t border-slate-100">
                  <td className="px-4 py-4 text-slate-500" colSpan={5}>
                    Sem jobs ainda. Inicie um novo processamento.
                  </td>
                </tr>
              )}
              {items.map((job) => (
                <tr key={job.id} className="border-t border-slate-100">
                  <td className="px-4 py-4 font-mono text-xs">{job.id}</td>
                  <td className="px-4 py-4">{job.status}</td>
                  <td className="px-4 py-4">
                    <div className="h-2 w-28 rounded-full bg-slate-100">
                      <div className="h-2 rounded-full bg-ink" style={{ width: `${job.progress}%` }} />
                    </div>
                    <span className="mt-1 block text-xs text-slate-500">{job.progress}%</span>
                  </td>
                  <td className="px-4 py-4">{new Date(job.created_at).toLocaleString("pt-BR")}</td>
                  <td className="px-4 py-4">
                    <button
                      disabled={job.status !== "succeeded"}
                      onClick={() => handleDownload(job.id)}
                      className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      Baixar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AppShell>
  );
}

