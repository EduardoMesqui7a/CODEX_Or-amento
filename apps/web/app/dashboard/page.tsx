"use client";

import { useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { listJobs, type JobResponse } from "@/lib/api";

export default function DashboardPage() {
  const [jobs, setJobs] = useState<JobResponse[]>([]);

  useEffect(() => {
    let active = true;
    listJobs()
      .then((response) => {
        if (active) setJobs(response.items);
      })
      .catch(() => undefined);
    return () => {
      active = false;
    };
  }, []);

  const stats = useMemo(() => {
    const processed = jobs.length;
    const completed = jobs.filter((job) => job.status === "succeeded");
    const totalRows = completed.reduce((sum, job) => sum + (job.summary?.rows_total || 0), 0);
    const totalItemRows = completed.reduce((sum, job) => sum + (job.summary?.rows_item || 0), 0);
    const highConfidenceRate = totalRows ? Math.round((totalItemRows / totalRows) * 100) : 0;
    const avgProgress = processed ? Math.round(jobs.reduce((sum, job) => sum + job.progress, 0) / processed) : 0;
    return { processed, avgProgress, highConfidenceRate };
  }, [jobs]);

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-semibold">Dashboard</h2>
          <p className="mt-1 text-sm text-slate-600">Indicadores do processamento de planilhas em tempo quase real.</p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <article className="rounded-2xl bg-white p-5">
            <p className="text-sm text-slate-500">Jobs processados</p>
            <p className="mt-2 text-3xl font-semibold">{stats.processed}</p>
          </article>
          <article className="rounded-2xl bg-white p-5">
            <p className="text-sm text-slate-500">Progresso médio</p>
            <p className="mt-2 text-3xl font-semibold">{stats.avgProgress}%</p>
          </article>
          <article className="rounded-2xl bg-white p-5">
            <p className="text-sm text-slate-500">Taxa de itens preenchidos</p>
            <p className="mt-2 text-3xl font-semibold">{stats.highConfidenceRate}%</p>
          </article>
        </div>

        <article className="rounded-2xl bg-white p-6">
          <h3 className="text-lg font-semibold">Últimos jobs</h3>
          <ul className="mt-4 space-y-2">
            {jobs.slice(0, 5).map((job) => (
              <li key={job.id} className="rounded-xl border border-slate-100 px-3 py-2 text-sm">
                <span className="font-mono text-xs">{job.id}</span> · {job.status} · {job.progress}%
              </li>
            ))}
            {jobs.length === 0 && <li className="text-sm text-slate-500">Nenhum job encontrado.</li>}
          </ul>
        </article>
      </div>
    </AppShell>
  );
}

