"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchAdminOverview, type AdminOverview } from "@/lib/api";

const emptyOverview: AdminOverview = {
  total_runs: 0,
  status_totals: {},
  provider_totals: {},
  recent_failures: [],
};

export function AdminOverviewClient() {
  const { data: overview = emptyOverview, error, isLoading } = useQuery<AdminOverview>({
    queryKey: ["admin-overview"],
    queryFn: fetchAdminOverview,
  });

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-6 py-16">
      <section className="space-y-4">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Admin operations</p>
        <h1 className="text-4xl font-semibold text-white">Platform overview</h1>
        <p className="max-w-3xl text-sm leading-7 text-slate-300">
          This page is the first production-style operations surface on top of the existing backend.
          It exposes run volume, status mix, provider usage, and failure visibility.
        </p>
      </section>

      {error ? (
        <div className="rounded-[2rem] border border-rose-400/20 bg-rose-400/10 p-6 text-sm text-rose-200">
          Admin data is unavailable. Sign in with an admin account to inspect platform operations.
        </div>
      ) : null}

      <section className="grid gap-6 md:grid-cols-4">
        <article className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-6">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Total runs</p>
          <p className="mt-4 text-4xl font-semibold text-white">
            {isLoading ? "…" : overview.total_runs}
          </p>
        </article>
        {Object.entries(overview.status_totals).map(([status, total]) => (
          <article
            key={status}
            className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-6"
          >
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{status}</p>
            <p className="mt-4 text-4xl font-semibold text-white">{total}</p>
          </article>
        ))}
      </section>

      <section className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
        <article className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-6">
          <h2 className="text-2xl font-semibold text-white">Provider usage</h2>
          <div className="mt-6 space-y-4">
            {Object.entries(overview.provider_totals).length === 0 ? (
              <p className="text-sm text-slate-400">No provider usage data yet.</p>
            ) : (
              Object.entries(overview.provider_totals).map(([provider, total]) => (
                <div
                  key={provider}
                  className="flex items-center justify-between rounded-3xl border border-white/10 bg-slate-950/70 px-4 py-3"
                >
                  <span className="text-sm text-slate-200">{provider}</span>
                  <span className="text-sm font-medium text-cyan-200">{total}</span>
                </div>
              ))
            )}
          </div>
        </article>

        <article className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-6">
          <h2 className="text-2xl font-semibold text-white">Recent failures</h2>
          <div className="mt-6 space-y-4">
            {overview.recent_failures.length === 0 ? (
              <div className="rounded-3xl border border-dashed border-white/15 p-5 text-sm text-slate-400">
                No failed runs recorded in the current environment.
              </div>
            ) : (
              overview.recent_failures.map((failure) => (
                <div
                  key={failure.public_id}
                  className="rounded-3xl border border-rose-400/20 bg-rose-400/5 p-5"
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-sm font-medium text-white">{failure.public_id}</span>
                    <span className="text-xs text-slate-500">
                      {new Date(failure.updated_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="mt-3 text-sm leading-7 text-slate-300">{failure.idea_text}</p>
                  <p className="mt-3 text-xs text-rose-200">
                    {failure.failure_message ?? "No failure message provided."}
                  </p>
                </div>
              ))
            )}
          </div>
        </article>
      </section>
    </div>
  );
}
