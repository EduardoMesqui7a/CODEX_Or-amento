import { AppShell } from "@/components/app-shell";

const plans = [
  { name: "Free", price: "R$0", description: "Para validar o fluxo", cta: "Plano atual" },
  { name: "Pro", price: "R$149", description: "Mais jobs e prioridade", cta: "Em breve" },
  { name: "Business", price: "Sob consulta", description: "Volume e governança", cta: "Falar com vendas" }
];

export default function PlansPage() {
  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-semibold">Planos</h2>
          <p className="mt-1 text-sm text-slate-600">Arquitetura pronta para Stripe, com ativação comercial futura.</p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {plans.map((plan) => (
            <article key={plan.name} className="rounded-2xl bg-white p-5">
              <p className="text-sm text-slate-500">{plan.name}</p>
              <p className="mt-2 text-3xl font-semibold">{plan.price}</p>
              <p className="mt-2 text-sm text-slate-600">{plan.description}</p>
              <button className="mt-5 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm">{plan.cta}</button>
            </article>
          ))}
        </div>
      </div>
    </AppShell>
  );
}

