import Link from "next/link";
import { FileText, Gauge, Layers3, Sparkles } from "lucide-react";
import { ReactNode } from "react";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: Gauge },
  { href: "/processing/new", label: "Novo Processamento", icon: Sparkles },
  { href: "/history", label: "Histórico", icon: FileText },
  { href: "/plans", label: "Planos", icon: Layers3 }
];

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen p-4 md:p-6">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-4 md:grid-cols-[260px_1fr]">
        <aside className="glass rounded-3xl p-4 shadow-premium">
          <div className="mb-6 rounded-2xl bg-ink p-4 text-mist">
            <p className="text-xs uppercase tracking-[0.2em] text-cyanGlow">Orcamento IA</p>
            <h1 className="mt-2 text-xl font-semibold">Workspace</h1>
          </div>
          <nav className="space-y-2">
            {nav.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
                >
                  <Icon size={16} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </aside>
        <main className="glass rounded-3xl p-4 shadow-premium md:p-6">{children}</main>
      </div>
    </div>
  );
}

