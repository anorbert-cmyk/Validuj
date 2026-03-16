"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { createRun, type RunSummary } from "@/lib/api";

type DashboardClientProps = {
  initialRuns: RunSummary[];
};

export function DashboardClient({ initialRuns }: DashboardClientProps) {
  const [ideaText, setIdeaText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const recentRuns = useMemo(() => initialRuns.slice(0, 8), [initialRuns]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (ideaText.trim().length < 20) {
      setError("Please add a more specific business idea.");
      return;
    }
    try {
      setError(null);
      setIsSubmitting(true);
      const result = await createRun(ideaText.trim());
      router.push(`/runs/${result.run_id}`);
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "Something went wrong while creating the run.",
      );
      setIsSubmitting(false);
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
      <section className="rounded-[2rem] border border-white/10 bg-slate-900/65 p-8 shadow-2xl shadow-slate-950/40">
        <div className="space-y-3">
          <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">New validation run</p>
          <h1 className="text-3xl font-semibold text-white">Create a production-style validation report</h1>
          <p className="max-w-2xl text-sm leading-7 text-slate-300">
            Submit a concrete business idea. The backend will immediately start the six-agent workflow and
            push live progress to the detail page.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <label className="block space-y-2">
            <span className="text-sm font-medium text-slate-200">Business idea</span>
            <textarea
              className="min-h-56 w-full rounded-3xl border border-white/10 bg-slate-950/80 px-5 py-4 text-sm leading-7 text-slate-100 outline-none transition focus:border-cyan-400/50 focus:ring-2 focus:ring-cyan-400/20"
              placeholder="Example: A subscription platform for boutique physiotherapy clinics that turns session notes into claim-ready documentation and tailored patient follow-up plans."
              value={ideaText}
              onChange={(event) => setIdeaText(event.target.value)}
            />
          </label>
          {error ? <p className="text-sm text-rose-300">{error}</p> : null}
          <div className="flex flex-wrap items-center gap-4">
            <button
              type="submit"
              disabled={isSubmitting}
              className="rounded-full bg-cyan-400 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSubmitting ? "Creating run..." : "Launch analysis"}
            </button>
            <span className="text-sm text-slate-400">
              Uses the FastAPI orchestration backend and current six-agent runtime.
            </span>
          </div>
        </form>
      </section>

      <aside className="rounded-[2rem] border border-white/10 bg-slate-900/40 p-6">
        <div className="space-y-2">
          <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Recent runs</p>
          <h2 className="text-2xl font-semibold text-white">Activity snapshot</h2>
        </div>
        <div className="mt-6 space-y-4">
          {recentRuns.length === 0 ? (
            <div className="rounded-3xl border border-dashed border-white/15 p-5 text-sm text-slate-400">
              No runs yet. Create your first validation run from the panel on the left.
            </div>
          ) : (
            recentRuns.map((run) => (
              <Link
                key={run.public_id}
                href={`/runs/${run.public_id}`}
                className="block rounded-3xl border border-white/10 bg-slate-950/70 p-5 transition hover:border-cyan-400/40 hover:bg-slate-950"
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="text-xs uppercase tracking-[0.18em] text-slate-400">{run.status}</span>
                  <span className="text-xs text-slate-500">
                    {new Date(run.updated_at).toLocaleString()}
                  </span>
                </div>
                <p className="mt-3 line-clamp-3 text-sm leading-7 text-slate-200">{run.idea_text}</p>
                <p className="mt-3 text-xs text-cyan-200">
                  {run.current_stage_name ? `Current stage: ${run.current_stage_name}` : "Queued"}
                </p>
              </Link>
            ))
          )}
        </div>
      </aside>
    </div>
  );
}
