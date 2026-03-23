import Link from "next/link";
import { ArrowRight, ShieldCheck, Sparkles, WandSparkles } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen px-5 py-8 md:px-12 md:py-10">
      <header className="mx-auto flex max-w-6xl items-center justify-between rounded-2xl border border-white/60 bg-white/70 px-5 py-3">
        <div className="text-lg font-semibold">Orcamento IA</div>
        <nav className="flex items-center gap-4 text-sm text-slate-600">
          <Link href="/plans">Planos</Link>
          <Link href="/dashboard" className="rounded-lg bg-ink px-3 py-2 text-white">
            Entrar
          </Link>
        </nav>
      </header>

      <section className="mx-auto mt-10 grid max-w-6xl gap-6 md:grid-cols-[1.2fr_1fr]">
        <div className="rounded-3xl bg-ink p-8 text-white shadow-premium">
          <p className="text-xs uppercase tracking-[0.2em] text-cyanGlow">SaaS para engenharia</p>
          <h1 className="mt-4 text-3xl font-semibold md:text-5xl">
            Orçamentos preenchidos com IA, sem perder o controle do Excel.
          </h1>
          <p className="mt-4 max-w-xl text-slate-300">
            Faça upload da base e da planilha destino, mapeie colunas e receba o arquivo final com rastreabilidade.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/processing/new" className="inline-flex items-center gap-2 rounded-xl bg-cyanGlow px-4 py-2 font-medium text-ink">
              Testar agora <ArrowRight size={16} />
            </Link>
            <Link href="/dashboard" className="inline-flex items-center rounded-xl border border-white/30 px-4 py-2">
              Ver dashboard
            </Link>
          </div>
        </div>

        <div className="grid gap-4">
          <div className="rounded-2xl bg-white p-5 shadow-premium">
            <WandSparkles size={18} />
            <h3 className="mt-3 text-lg font-semibold">Matching híbrido</h3>
            <p className="mt-1 text-sm text-slate-600">Semântico + fuzzy + regras de negócio preservadas.</p>
          </div>
          <div className="rounded-2xl bg-white p-5 shadow-premium">
            <ShieldCheck size={18} />
            <h3 className="mt-3 text-lg font-semibold">Pronto para produção</h3>
            <p className="mt-1 text-sm text-slate-600">Arquitetura desacoplada, auth e fila assíncrona.</p>
          </div>
          <div className="rounded-2xl bg-white p-5 shadow-premium">
            <Sparkles size={18} />
            <h3 className="mt-3 text-lg font-semibold">UX de produto SaaS</h3>
            <p className="mt-1 text-sm text-slate-600">Experiência responsiva para desktop e mobile.</p>
          </div>
        </div>
      </section>
    </div>
  );
}

