import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Why Validuj is different",
  description:
    "See how Validuj differs from AI startup validation competitors with stronger multi-agent flow, evidence traceability, and operational depth.",
};

const comparisons = [
  {
    area: "AI workflow",
    competitors: "Mostly black-box report generation with limited stage transparency.",
    validuj:
      "Six explicit specialist stages with visible handoff logic, progress, and stage-level outputs.",
  },
  {
    area: "Evidence handling",
    competitors: "Market and competitor insights are often summarized without strong report traceability.",
    validuj:
      "Evidence is attached to stages and can be surfaced directly inside the report experience.",
  },
  {
    area: "Operational depth",
    competitors: "Focus mainly on general startup advice, market sizing, and summary recommendations.",
    validuj:
      "Includes product design, edge-case review, operational safeguards, and risk-focused synthesis.",
  },
  {
    area: "Product surface",
    competitors: "Many tools stop at user-only report generation.",
    validuj:
      "Adds dashboard, workspace model, admin visibility, export flow, billing shell, and production-minded UX.",
  },
];

export default function ComparePage() {
  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-10 px-6 py-16">
      <section className="space-y-5">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Competitive differentiation</p>
        <h1 className="max-w-4xl text-5xl font-semibold tracking-tight text-white">
          Better than generic startup idea analyzers.
        </h1>
        <p className="max-w-3xl text-base leading-8 text-slate-300">
          Validuj is being shaped to outperform typical validation competitors by combining
          structured multi-agent reasoning, evidence-driven reporting, and a more serious product
          surface for teams who want more than a one-shot AI summary.
        </p>
      </section>

      <section className="overflow-hidden rounded-[2rem] border border-white/10 bg-slate-900/60">
        <div className="grid grid-cols-[0.9fr_1fr_1fr] border-b border-white/10 bg-slate-950/70 px-6 py-4 text-sm font-semibold text-slate-200">
          <div>Area</div>
          <div>Typical competitor</div>
          <div>Validuj direction</div>
        </div>
        {comparisons.map((row) => (
          <div
            key={row.area}
            className="grid grid-cols-[0.9fr_1fr_1fr] gap-6 border-b border-white/10 px-6 py-6 text-sm leading-7 last:border-b-0"
          >
            <div className="font-semibold text-white">{row.area}</div>
            <div className="text-slate-400">{row.competitors}</div>
            <div className="text-cyan-100">{row.validuj}</div>
          </div>
        ))}
      </section>
    </div>
  );
}
