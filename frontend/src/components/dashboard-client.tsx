"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import {
  createProject,
  createRun,
  fetchProjects,
  fetchRuns,
  type ProjectSummary,
  type RunSummary,
} from "@/lib/api";

type DashboardClientProps = {
  initialProjects: ProjectSummary[];
  initialRuns: RunSummary[];
};

export function DashboardClient({ initialProjects, initialRuns }: DashboardClientProps) {
  const [ideaText, setIdeaText] = useState("");
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCreatingProject, setIsCreatingProject] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: projects = initialProjects } = useQuery<ProjectSummary[]>({
    queryKey: ["projects"],
    queryFn: fetchProjects,
    initialData: initialProjects,
  });

  const { data: runs = initialRuns } = useQuery<RunSummary[]>({
    queryKey: ["runs"],
    queryFn: fetchRuns,
    initialData: initialRuns,
  });

  const recentRuns = useMemo(() => runs.slice(0, 8), [runs]);
  const starterIdeas = [
    "AI operations copilot for boutique physiotherapy clinics that drafts claim-ready notes and patient follow-up plans.",
    "AI compliance assistant for solo rehab practitioners that turns messy session notes into insurer-ready documentation.",
    "Vertical SaaS for private physiotherapy studios that predicts dropout risk and automates follow-up outreach.",
  ];

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (ideaText.trim().length < 20) {
      setError("Please add a more specific business idea.");
      return;
    }
    try {
      setError(null);
      setIsSubmitting(true);
      const result = await createRun(ideaText.trim(), selectedProjectId || undefined);
      await queryClient.invalidateQueries({ queryKey: ["runs"] });
      await queryClient.invalidateQueries({ queryKey: ["projects"] });
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

  async function handleCreateProject(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (projectName.trim().length < 2) {
      setError("Project name should be at least 2 characters.");
      return;
    }
    try {
      setError(null);
      setIsCreatingProject(true);
      const result = await createProject({
        name: projectName.trim(),
        description: projectDescription.trim(),
      });
      const newProject: ProjectSummary = {
        public_id: result.project_id,
        name: projectName.trim(),
        description: projectDescription.trim() || null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        run_count: 0,
      };
      queryClient.setQueryData<ProjectSummary[]>(["projects"], (current) =>
        current ? [newProject, ...current] : [newProject],
      );
      setSelectedProjectId(result.project_id);
      setProjectName("");
      setProjectDescription("");
    } catch (projectError) {
      setError(
        projectError instanceof Error
          ? projectError.message
          : "Unable to create project right now.",
      );
    } finally {
      setIsCreatingProject(false);
    }
  }

  return (
    <div className="grid gap-8 xl:grid-cols-[0.9fr_0.9fr_0.8fr]">
      <section className="rounded-[2rem] border border-white/10 bg-slate-900/65 p-8 shadow-2xl shadow-slate-950/40">
        <div className="space-y-3">
          <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Project workspace</p>
          <h2 className="text-3xl font-semibold text-white">Create a project container</h2>
          <p className="max-w-2xl text-sm leading-7 text-slate-300">
            Projects are the next product-layer abstraction on top of individual validation runs.
          </p>
        </div>

        <form onSubmit={handleCreateProject} className="mt-8 space-y-4">
          <label className="block space-y-2">
            <span className="text-sm font-medium text-slate-200">Project name</span>
            <input
              className="w-full rounded-3xl border border-white/10 bg-slate-950/80 px-5 py-4 text-sm text-slate-100 outline-none transition focus:border-cyan-400/50 focus:ring-2 focus:ring-cyan-400/20"
              placeholder="Recovery operations platform"
              value={projectName}
              onChange={(event) => setProjectName(event.target.value)}
            />
          </label>
          <label className="block space-y-2">
            <span className="text-sm font-medium text-slate-200">Description</span>
            <textarea
              className="min-h-32 w-full rounded-3xl border border-white/10 bg-slate-950/80 px-5 py-4 text-sm leading-7 text-slate-100 outline-none transition focus:border-cyan-400/50 focus:ring-2 focus:ring-cyan-400/20"
              placeholder="Internal description for the initiative or venture."
              value={projectDescription}
              onChange={(event) => setProjectDescription(event.target.value)}
            />
          </label>
          <button
            type="submit"
            disabled={isCreatingProject}
            className="rounded-full border border-white/10 px-6 py-3 text-sm font-semibold text-white transition hover:border-cyan-400/40 hover:bg-white/5 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isCreatingProject ? "Creating project..." : "Create project"}
          </button>
        </form>
      </section>

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
            <span className="text-sm font-medium text-slate-200">Attach to project</span>
            <select
              className="w-full rounded-3xl border border-white/10 bg-slate-950/80 px-5 py-4 text-sm text-slate-100 outline-none transition focus:border-cyan-400/50 focus:ring-2 focus:ring-cyan-400/20"
              value={selectedProjectId}
              onChange={(event) => setSelectedProjectId(event.target.value)}
            >
              <option value="">No project</option>
              {projects.map((project) => (
                <option key={project.public_id} value={project.public_id}>
                  {project.name}
                </option>
              ))}
            </select>
          </label>
          <label className="block space-y-2">
            <span className="text-sm font-medium text-slate-200">Business idea</span>
            <textarea
              className="min-h-56 w-full rounded-3xl border border-white/10 bg-slate-950/80 px-5 py-4 text-sm leading-7 text-slate-100 outline-none transition focus:border-cyan-400/50 focus:ring-2 focus:ring-cyan-400/20"
              placeholder="Example: A subscription platform for boutique physiotherapy clinics that turns session notes into claim-ready documentation and tailored patient follow-up plans."
              value={ideaText}
              onChange={(event) => setIdeaText(event.target.value)}
            />
          </label>
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Starter prompts</p>
            <div className="flex flex-wrap gap-2">
              {starterIdeas.map((idea) => (
                <button
                  key={idea}
                  type="button"
                  onClick={() => setIdeaText(idea)}
                  className="rounded-full border border-white/10 px-3 py-2 text-xs text-slate-300 transition hover:border-cyan-400/40 hover:text-white"
                >
                  Use example
                </button>
              ))}
            </div>
          </div>
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
          <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Workspace activity</p>
          <h2 className="text-2xl font-semibold text-white">Projects and recent runs</h2>
        </div>
        <div className="mt-6 space-y-4">
          {projects.length === 0 ? (
            <div className="rounded-3xl border border-dashed border-white/15 p-5 text-sm text-slate-400">
              No projects yet. Create one to start organizing validation work.
            </div>
          ) : (
            projects.slice(0, 4).map((project) => (
              <div
                key={project.public_id}
                className="rounded-3xl border border-white/10 bg-slate-950/70 p-5"
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="text-sm font-medium text-white">{project.name}</span>
                  <span className="text-xs text-cyan-200">{project.run_count} runs</span>
                </div>
                <p className="mt-2 text-xs leading-6 text-slate-400">
                  {project.description ?? "No description yet."}
                </p>
              </div>
            ))
          )}
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
                <p className="mt-2 text-[11px] text-slate-500">
                  {run.project_public_id ? `Project: ${run.project_public_id}` : "Unassigned run"}
                </p>
              </Link>
            ))
          )}
        </div>
      </aside>
    </div>
  );
}
