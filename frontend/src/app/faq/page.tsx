import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "FAQ",
  description: "Answers to common questions about Validuj, its six-agent workflow, and the production-ready platform direction.",
};

const faqs = [
  {
    question: "Is the six-agent workflow already real?",
    answer:
      "Yes. The backend already runs a real six-stage workflow with stored handoff state, event persistence, and live streaming.",
  },
  {
    question: "What makes the next phase production-ready?",
    answer:
      "The next phase adds a polished frontend, stronger backend platform features, auth, billing, admin operations, and production infrastructure.",
  },
  {
    question: "Will the existing FastAPI engine be replaced?",
    answer:
      "No. It remains the domain core and will be expanded rather than discarded.",
  },
];

export default function FaqPage() {
  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-6 py-16">
      <section className="space-y-5">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">FAQ</p>
        <h1 className="text-5xl font-semibold tracking-tight text-white">Frequently asked questions</h1>
      </section>

      <section className="space-y-4">
        {faqs.map((item) => (
          <article key={item.question} className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-6">
            <h2 className="text-xl font-semibold text-white">{item.question}</h2>
            <p className="mt-3 text-sm leading-7 text-slate-300">{item.answer}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
