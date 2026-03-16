import type { Metadata } from "next";

import { fetchBillingPlans } from "@/lib/api";

export const metadata: Metadata = {
  title: "Pricing",
  description:
    "Explore the planned production pricing model for Validuj, from founder discovery to advanced validation workflows.",
};

export default async function PricingPage() {
  const plans = await fetchBillingPlans().catch(() => []);

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-10 px-6 py-16">
      <section className="space-y-5">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Pricing</p>
        <h1 className="max-w-4xl text-5xl font-semibold tracking-tight text-white">
          Pricing designed around serious validation work.
        </h1>
        <p className="max-w-3xl text-base leading-8 text-slate-300">
          The pricing surface now reads from the live billing foundation in the backend. It is still a
          local product shell rather than a real payment gateway integration, but plan names, prices,
          and run limits are already enforced through the protected API layer.
        </p>
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        {plans.map((tier) => (
          <article
            key={tier.name}
            className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-8 shadow-lg shadow-slate-950/30"
          >
            <p className="text-sm uppercase tracking-[0.18em] text-cyan-200">{tier.name}</p>
            <h2 className="mt-4 text-4xl font-semibold text-white">
              ${tier.price}
            </h2>
            <p className="mt-2 text-xs uppercase tracking-[0.18em] text-slate-500">
              {tier.run_limit} runs
            </p>
            <p className="mt-4 text-sm leading-7 text-slate-300">{tier.description}</p>
            <ul className="mt-6 space-y-3 text-sm text-slate-200">
              <li className="flex gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-cyan-300" />
                <span>Six-agent report generation</span>
              </li>
              <li className="flex gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-cyan-300" />
                <span>Live progress and persisted report history</span>
              </li>
              <li className="flex gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-cyan-300" />
                <span>Plan-gated run capacity</span>
              </li>
            </ul>
          </article>
        ))}
      </section>
    </div>
  );
}
