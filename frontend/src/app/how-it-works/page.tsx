import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "How it works",
  description:
    "Understand the six-agent startup validation workflow that powers Validuj, from market research to risk analysis.",
};

const stages = [
  {
    name: "Market Scout",
    body: "Clarifies the problem, target customer, pain point urgency, and live market evidence.",
  },
  {
    name: "Competitor Analyst",
    body: "Maps existing tools and alternatives so the product can position around whitespace instead of generic automation.",
  },
  {
    name: "Strategy Architect",
    body: "Turns research into a beachhead segment, rollout logic, and milestone-driven product strategy.",
  },
  {
    name: "Product Designer",
    body: "Translates strategy into MVP scope, trust-aware UX, and reportable workflow design.",
  },
  {
    name: "Edge-Case Reviewer",
    body: "Stress-tests failure modes, compliance exposure, ambiguous inputs, and review-state safeguards.",
  },
  {
    name: "Risk & Decision Analyst",
    body: "Combines the previous handoff into final risks, experiments, and a practical go / no-go recommendation.",
  },
];

export default function HowItWorksPage() {
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-10 px-6 py-16">
      <section className="space-y-5">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Methodology</p>
        <h1 className="max-w-4xl text-5xl font-semibold tracking-tight text-white">
          The workflow is sequential on purpose.
        </h1>
        <p className="max-w-3xl text-base leading-8 text-slate-300">
          Validuj does not throw one giant prompt at one model. It chains six specialists, each one
          receiving a compact structured handoff from the previous stage so the system stays coherent,
          auditable, and useful for real product decisions.
        </p>
      </section>

      <section className="grid gap-5 md:grid-cols-2">
        {stages.map((stage, index) => (
          <article
            key={stage.name}
            className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-6"
          >
            <p className="text-xs uppercase tracking-[0.18em] text-cyan-200">Stage {index + 1}</p>
            <h2 className="mt-3 text-2xl font-semibold text-white">{stage.name}</h2>
            <p className="mt-4 text-sm leading-7 text-slate-300">{stage.body}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
