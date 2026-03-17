import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Demo report",
  description:
    "See the structure of a production-style Validuj report, from market context through risk recommendation.",
};

const reportSections = [
  "Market context and demand",
  "Competitive landscape",
  "Strategy and roadmap",
  "Product and UX concept",
  "Edge cases and operational safeguards",
  "Risk assessment and recommendation",
];

export default function DemoReportPage() {
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-6 py-16">
      <section className="space-y-5">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Demo report</p>
        <h1 className="max-w-4xl text-5xl font-semibold tracking-tight text-white">
          Product-grade report rendering starts with readable structure.
        </h1>
        <p className="max-w-3xl text-base leading-8 text-slate-300">
          The backend already produces the full report. This page previews how a richer frontend
          report-reading experience can frame the report as a premium product surface.
        </p>
      </section>

      <section className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-8">
        <div className="grid gap-5 md:grid-cols-2">
          {reportSections.map((section, index) => (
            <article
              key={section}
              className="rounded-3xl border border-white/10 bg-slate-950/75 p-5"
            >
              <p className="text-xs uppercase tracking-[0.18em] text-cyan-200">Section {index + 1}</p>
              <h2 className="mt-3 text-xl font-semibold text-white">{section}</h2>
              <p className="mt-4 text-sm leading-7 text-slate-300">
                This page previews the layout for a future polished report reader with citations,
                summaries, stage navigation, and export-aware formatting.
              </p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
