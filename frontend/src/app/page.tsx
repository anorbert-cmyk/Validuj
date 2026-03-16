import Link from "next/link";

export default function Home() {
  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-16 px-6 py-16">
      <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
        <div className="space-y-8">
          <div className="inline-flex rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-1 text-sm text-cyan-200">
            Production-ready validation platform
          </div>
          <div className="space-y-6">
            <h1 className="max-w-4xl text-5xl font-semibold tracking-tight text-white sm:text-6xl">
              Build, validate, and operationalize startup ideas with a six-agent research engine.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-slate-300">
              Validuj combines market research, competitor mapping, strategy, product design,
              operational edge-case analysis, and risk review into one production-ready SaaS
              workflow for founders and innovation teams.
            </p>
          </div>
          <div className="flex flex-wrap gap-4">
            <Link
              href="/dashboard"
              className="rounded-full bg-cyan-400 px-6 py-3 font-medium text-slate-950 transition hover:bg-cyan-300"
            >
              Launch dashboard
            </Link>
            <Link
              href="/pricing"
              className="rounded-full border border-white/15 px-6 py-3 font-medium text-white transition hover:border-white/35 hover:bg-white/5"
            >
              View pricing
            </Link>
          </div>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-cyan-950/30">
          <div className="space-y-4">
            <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Live workflow</p>
            <div className="space-y-3">
              {[
                "Market Scout",
                "Competitor Analyst",
                "Strategy Architect",
                "Product Designer",
                "Edge-Case Reviewer",
                "Risk & Decision Analyst",
              ].map((stage, index) => (
                <div
                  key={stage}
                  className="flex items-center justify-between rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3"
                >
                  <span className="text-sm text-slate-300">
                    {index + 1}. {stage}
                  </span>
                  <span className="rounded-full bg-emerald-400/15 px-3 py-1 text-xs text-emerald-200">
                    handoff-ready
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 md:grid-cols-3">
        {[
          {
            title: "Research-heavy intelligence",
            body: "Early stages enrich analysis with live search evidence so the product is grounded in real market signals instead of generic model memory.",
          },
          {
            title: "Structured handoff",
            body: "Each stage passes compact state to the next one, preserving signal while avoiding bloated prompt histories and weak continuity.",
          },
          {
            title: "Production visibility",
            body: "Live progress, persisted runs, API access, and SEO-ready public pages let the validation engine work as a real product surface.",
          },
        ].map((item) => (
          <article
            key={item.title}
            className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-lg shadow-slate-950/20"
          >
            <h2 className="text-xl font-semibold text-white">{item.title}</h2>
            <p className="mt-4 text-sm leading-7 text-slate-300">{item.body}</p>
          </article>
        ))}
      </section>

      <section className="grid gap-8 rounded-[2rem] border border-white/10 bg-gradient-to-br from-slate-900 to-slate-950 p-8 lg:grid-cols-[1fr_1fr]">
        <div className="space-y-4">
          <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">For product teams</p>
          <h2 className="text-3xl font-semibold text-white">
            From founder discovery to operational reporting in one product surface.
          </h2>
        </div>
        <div className="grid gap-4 text-sm leading-7 text-slate-300">
          <p>
            The current platform already ships the AI core. The next production layer adds a polished
            frontend, richer dashboards, billing, admin operations, and stronger trust pages without
            discarding the validated backend engine.
          </p>
          <p>
            Explore the methodology, demo report, and dashboard shell to see how the product is being
            expanded toward a full production-ready SaaS.
          </p>
        </div>
      </section>
    </div>
  );
}
