export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export type RunSummary = {
  project_public_id: string | null;
  public_id: string;
  idea_text: string;
  status: "queued" | "running" | "completed" | "failed";
  current_stage_name: string | null;
  created_at: string;
  updated_at: string;
};

export type RunEvent = {
  event_type: string;
  payload: Record<string, unknown>;
  created_at: string;
};

export type StageRecord = {
  stage_index: number;
  stage_name: string;
  status: "pending" | "running" | "completed" | "failed";
  provider_name: string | null;
  model_name: string | null;
  summary: string | null;
  markdown: string | null;
};

export type RunRecord = RunSummary & {
  current_stage: number | null;
  final_markdown: string | null;
  failure_message: string | null;
  events: RunEvent[];
  stages: StageRecord[];
};

export type ProjectSummary = {
  public_id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  run_count: number;
};

export type SessionUser = {
  email: string;
  role: "user" | "admin";
};

export type AdminOverview = {
  total_runs: number;
  status_totals: Record<string, number>;
  provider_totals: Record<string, number>;
  recent_failures: Array<{
    public_id: string;
    idea_text: string;
    failure_message: string | null;
    updated_at: string;
  }>;
};

export async function fetchRuns(): Promise<RunSummary[]> {
  const response = await fetch(`${API_BASE_URL}/api/runs`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Failed to load runs");
  }
  return response.json();
}

export async function fetchRun(runId: string): Promise<RunRecord> {
  const response = await fetch(`${API_BASE_URL}/api/runs/${runId}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Failed to load run");
  }
  return response.json();
}

export function getRunMarkdownDownloadUrl(runId: string): string {
  return `${API_BASE_URL}/api/runs/${runId}/markdown`;
}

export async function createRun(
  ideaText: string,
  projectPublicId?: string,
): Promise<{ run_id: string }> {
  const response = await fetch(`${API_BASE_URL}/api/runs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      idea_text: ideaText,
      project_public_id: projectPublicId ?? null,
    }),
  });
  if (!response.ok) {
    throw new Error("Failed to create run");
  }
  return response.json();
}

export async function fetchAdminOverview(): Promise<AdminOverview> {
  const response = await fetch(`${API_BASE_URL}/api/admin/overview`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Failed to load admin overview");
  }
  return response.json();
}

export async function fetchProjects(): Promise<ProjectSummary[]> {
  const response = await fetch(`${API_BASE_URL}/api/projects`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Failed to load projects");
  }
  return response.json();
}

export async function createProject(payload: {
  name: string;
  description?: string;
}): Promise<{ project_id: string }> {
  const response = await fetch(`${API_BASE_URL}/api/projects`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to create project");
  }
  return response.json();
}

export async function registerUser(payload: {
  email: string;
  password: string;
}): Promise<SessionUser> {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to register user");
  }
  return response.json();
}

export async function loginUser(payload: {
  email: string;
  password: string;
}): Promise<SessionUser> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to log in");
  }
  return response.json();
}

export async function fetchSessionUser(): Promise<SessionUser | null> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    cache: "no-store",
    credentials: "include",
  });
  if (response.status === 401) {
    return null;
  }
  if (!response.ok) {
    throw new Error("Failed to load session");
  }
  return response.json();
}
