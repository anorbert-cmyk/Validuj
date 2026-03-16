"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";

import {
  API_BASE_URL,
  fetchRun,
  getRunMarkdownDownloadUrl,
  type RunEvent,
  type RunRecord,
} from "@/lib/api";
import { MarkdownReport } from "@/components/markdown-report";

type RunDetailClientProps = {
  runId: string;
  initialRun?: RunRecord | null;
};

export function RunDetailClient({ runId, initialRun = null }: RunDetailClientProps) {
  const { data, refetch, error, isLoading } = useQuery<RunRecord>({
    queryKey: ["run", runId],
    queryFn: () => fetchRun(runId),
    initialData: initialRun ?? undefined,
    retry: false,
  });
  const [run, setRun] = useState<RunRecord | null>(initialRun);
  const currentRun = data ?? run;

  useEffect(() => {
    if (!currentRun) {
      return;
    }
    let isDisposed = false;
    const stream = new EventSource(`${API_BASE_URL}/api/stream/runs/${currentRun.public_id}`, {
      withCredentials: true,
    });

    const syncRun = async () => {
      try {
        const nextRun = await fetchRun(currentRun.public_id);
        if (!isDisposed) {
          setRun(nextRun);
        }
      } catch {
        // keep the previous snapshot if refresh fails
      }
    };

    const appendEvent = (eventType: string, payload: Record<string, unknown>) => {
      setRun((current) => ({
        ...(current ?? currentRun),
        events: [
          ...((current ?? currentRun).events ?? []),
          { event_type: eventType, payload, created_at: new Date().toISOString() } satisfies RunEvent,
        ],
      }));
    };

    const handlers = [
      "stage_started",
      "stage_progress",
      "stage_completed",
      "run_completed",
      "run_failed",
    ] as const;

    handlers.forEach((name) => {
      stream.addEventListener(name, (event) => {
        const payload = JSON.parse(event.data) as Record<string, unknown>;
        appendEvent(name, payload);
        void syncRun();
      });
    });

    stream.addEventListener("heartbeat", () => undefined);

    return () => {
      isDisposed = true;
      stream.close();
    };
  }, [currentRun, refetch]);

  const latestEvent = useMemo(() => currentRun?.events[currentRun.events.length - 1], [currentRun]);

  if (isLoading && !currentRun) {
    return (
      <div className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-8 text-sm text-slate-300">
        Loading run details...
      </div>
    );
  }

  if (error || !currentRun) {
    return (
      <div className="rounded-[2rem] border border-rose-400/20 bg-rose-400/10 p-8 text-sm text-rose-200">
        This run is not available for the current session. Sign in and ensure you own the run before
        trying again.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-8">
        <div className="flex flex-wrap items-center gap-3">
          <span className="rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-1 text-xs uppercase tracking-[0.24em] text-cyan-200">
            {currentRun.status}
          </span>
          <span className="text-xs text-slate-500">Run ID: {currentRun.public_id}</span>
        </div>
        <h1 className="mt-4 text-3xl font-semibold text-white">Live validation run</h1>
        <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-300">{currentRun.idea_text}</p>
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Current stage</p>
            <p className="mt-2 text-sm text-white">{currentRun.current_stage_name ?? "Waiting"}</p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Last update</p>
            <p className="mt-2 text-sm text-white">{new Date(currentRun.updated_at).toLocaleString()}</p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Latest event</p>
            <p className="mt-2 text-sm text-white">{latestEvent?.event_type ?? "run_created"}</p>
          </div>
        </div>
        <div className="mt-6 flex flex-wrap gap-4">
          <a
            href={getRunMarkdownDownloadUrl(currentRun.public_id)}
            className="rounded-full border border-cyan-400/30 px-5 py-2 text-sm font-medium text-cyan-200 transition hover:border-cyan-300 hover:text-white"
          >
            Export markdown
          </a>
          <Link
            href="/dashboard"
            className="rounded-full border border-white/10 px-5 py-2 text-sm font-medium text-slate-200 transition hover:border-white/30 hover:bg-white/5"
          >
            Back to dashboard
          </Link>
        </div>
      </section>

      <section className="grid gap-8 lg:grid-cols-[0.85fr_1.15fr]">
        <aside className="rounded-[2rem] border border-white/10 bg-slate-900/40 p-6">
          <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Event timeline</p>
          <div className="mt-5 space-y-4">
            {currentRun.events.map((event, index) => (
              <div
                key={`${event.event_type}-${index}-${event.created_at}`}
                className="rounded-3xl border border-white/10 bg-slate-950/70 p-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-medium text-white">{event.event_type}</p>
                  <p className="text-[11px] text-slate-500">
                    {new Date(event.created_at).toLocaleTimeString()}
                  </p>
                </div>
                <pre className="mt-3 overflow-x-auto whitespace-pre-wrap text-xs leading-6 text-slate-300">
                  {JSON.stringify(event.payload, null, 2)}
                </pre>
              </div>
            ))}
          </div>
        </aside>

        <div className="space-y-5">
          {currentRun.stages.map((stage) => (
            <article
              key={stage.stage_index}
              className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-6"
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.18em] text-cyan-200">
                    Stage {stage.stage_index}
                  </p>
                  <h2 className="mt-2 text-2xl font-semibold text-white">{stage.stage_name}</h2>
                </div>
                <div className="text-right text-xs text-slate-400">
                  <p>Status: {stage.status}</p>
                  {stage.provider_name ? (
                    <p>
                      {stage.provider_name} / {stage.model_name}
                    </p>
                  ) : null}
                </div>
              </div>
              {stage.summary ? (
                <p className="mt-4 text-sm leading-7 text-slate-300">{stage.summary}</p>
              ) : (
                <p className="mt-4 text-sm text-slate-500">This stage is still preparing its output.</p>
              )}
              {stage.markdown ? (
                <div className="mt-6 rounded-3xl border border-white/10 bg-slate-950/80 p-5">
                  <MarkdownReport content={stage.markdown} />
                </div>
              ) : null}
              {stage.citations?.length ? (
                <div className="mt-6 space-y-3">
                  <p className="text-xs uppercase tracking-[0.18em] text-cyan-200">Evidence</p>
                  <div className="grid gap-3">
                    {stage.citations.map((citation) => (
                      <a
                        key={`${stage.stage_index}-${citation.url}`}
                        href={citation.url}
                        target="_blank"
                        rel="noreferrer"
                        className="rounded-2xl border border-white/10 bg-slate-900/70 p-4 transition hover:border-cyan-400/40"
                      >
                        <p className="text-sm font-medium text-white">{citation.title}</p>
                        {citation.snippet ? (
                          <p className="mt-2 text-xs leading-6 text-slate-400">{citation.snippet}</p>
                        ) : null}
                        <p className="mt-2 text-[11px] uppercase tracking-[0.18em] text-cyan-200">
                          {citation.source}
                        </p>
                      </a>
                    ))}
                  </div>
                </div>
              ) : null}
            </article>
          ))}
        </div>
      </section>

      {currentRun.final_markdown ? (
        <section className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-8">
          <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Compiled report</p>
          <div className="mt-5 rounded-3xl border border-white/10 bg-slate-950/80 p-6">
            <MarkdownReport content={currentRun.final_markdown} />
          </div>
        </section>
      ) : null}
    </div>
  );
}
