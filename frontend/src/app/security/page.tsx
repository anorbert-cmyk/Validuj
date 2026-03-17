import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Security",
  description:
    "Review the trust and security posture planned for the production-ready expansion of Validuj.",
};

export default function SecurityPage() {
  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-10 px-6 py-16">
      <section className="space-y-5">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Trust and security</p>
        <h1 className="text-5xl font-semibold tracking-tight text-white">Security is part of the product, not a footer note.</h1>
        <p className="max-w-3xl text-base leading-8 text-slate-300">
          The current platform already enforces basic route separation and private-run noindex behavior.
          The production plan expands that foundation with authenticated workspaces, billing controls,
          audit trails, operational visibility, and clearer admin tooling.
        </p>
      </section>

      <section className="grid gap-5 md:grid-cols-2">
        {[
          "Private run pages remain excluded from search indexing.",
          "The orchestration engine is preserved as the core domain service instead of being rewritten blindly.",
          "Future production scope includes auth, billing controls, role-aware access, and admin audit visibility.",
          "Provider and model behavior is being moved toward more observable production-grade operations.",
        ].map((item) => (
          <div key={item} className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-6 text-sm leading-7 text-slate-200">
            {item}
          </div>
        ))}
      </section>
    </div>
  );
}
