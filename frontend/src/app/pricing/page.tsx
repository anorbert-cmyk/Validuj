import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Pricing",
  description:
    "Explore the planned production pricing model for Validuj, from founder discovery to advanced validation workflows.",
};

const tiers = [
  {
    name: "Explorer",
    price: "$49",
    description: "Single-run starter package for fast validation signals.",
    features: [
      "One guided validation run",
      "Full six-stage report",
      "Live progress tracking",
      "Report history in dashboard",
    ],
  },
  {
    name: "Builder",
    price: "$149",
    description: "For founders who need repeated validation and richer comparison work.",
    features: [
      "Multiple active runs",
      "Priority processing",
      "Enhanced report retention",
      "Richer export and comparison tooling",
    ],
  },
  {
    name: "Studio",
    price: "Custom",
    description: "For innovation teams and internal venture studios.",
    features: [
      "Shared workspace patterns",
      "Admin oversight",
      "Custom model routing controls",
      "Operational support and onboarding",
    ],
  },
];

export default function PricingPage() {
  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-10 px-6 py-16">
      <section className="space-y-5">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Pricing</p>
        <h1 className="max-w-4xl text-5xl font-semibold tracking-tight text-white">
          Pricing designed around serious validation work.
        </h1>
        <p className="max-w-3xl text-base leading-8 text-slate-300">
          The current codebase is expanding toward a full product, so pricing is represented as a
          production-ready structure rather than a live billing flow yet. The next execution phase adds
          authentication, Stripe billing, and usage enforcement around these tiers.
        </p>
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        {tiers.map((tier) => (
          <article
            key={tier.name}
            className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-8 shadow-lg shadow-slate-950/30"
          >
            <p className="text-sm uppercase tracking-[0.18em] text-cyan-200">{tier.name}</p>
            <h2 className="mt-4 text-4xl font-semibold text-white">{tier.price}</h2>
            <p className="mt-4 text-sm leading-7 text-slate-300">{tier.description}</p>
            <ul className="mt-6 space-y-3 text-sm text-slate-200">
              {tier.features.map((feature) => (
                <li key={feature} className="flex gap-3">
                  <span className="mt-1 h-2.5 w-2.5 rounded-full bg-cyan-300" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </article>
        ))}
      </section>
    </div>
  );
}
