"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { fetchSessionUser, loginUser, registerUser, type SessionUser } from "@/lib/api";

type AuthCardProps = {
  initialUser: SessionUser | null;
};

export function AuthCard({ initialUser }: AuthCardProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"login" | "register">("register");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const queryClient = useQueryClient();
  const { data: user = initialUser } = useQuery<SessionUser | null>({
    queryKey: ["session"],
    queryFn: fetchSessionUser,
    initialData: initialUser,
  });

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      setError(null);
      setIsSubmitting(true);
      const payload = { email: email.trim(), password };
      const nextUser =
        mode === "register" ? await registerUser(payload) : await loginUser(payload);
      queryClient.setQueryData(["session"], nextUser);
      queryClient.invalidateQueries();
      setEmail("");
      setPassword("");
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "Unable to complete authentication.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-6">
      <div className="space-y-2">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Authentication foundation</p>
        <h2 className="text-2xl font-semibold text-white">Account access</h2>
      </div>

      {user ? (
        <div className="mt-6 rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-5">
          <p className="text-sm text-emerald-100">Signed in as {user.email}</p>
          <p className="mt-2 text-xs uppercase tracking-[0.18em] text-emerald-200">{user.role}</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => setMode("register")}
              className={`rounded-full px-4 py-2 text-sm transition ${
                mode === "register"
                  ? "bg-cyan-400 text-slate-950"
                  : "border border-white/10 text-slate-300"
              }`}
            >
              Register
            </button>
            <button
              type="button"
              onClick={() => setMode("login")}
              className={`rounded-full px-4 py-2 text-sm transition ${
                mode === "login"
                  ? "bg-cyan-400 text-slate-950"
                  : "border border-white/10 text-slate-300"
              }`}
            >
              Login
            </button>
          </div>
          <label className="block space-y-2">
            <span className="text-sm font-medium text-slate-200">Email</span>
            <input
              className="w-full rounded-3xl border border-white/10 bg-slate-950/80 px-5 py-4 text-sm text-slate-100 outline-none transition focus:border-cyan-400/50 focus:ring-2 focus:ring-cyan-400/20"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="founder@example.com"
              type="email"
            />
          </label>
          <label className="block space-y-2">
            <span className="text-sm font-medium text-slate-200">Password</span>
            <input
              className="w-full rounded-3xl border border-white/10 bg-slate-950/80 px-5 py-4 text-sm text-slate-100 outline-none transition focus:border-cyan-400/50 focus:ring-2 focus:ring-cyan-400/20"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="At least 8 characters"
              type="password"
            />
          </label>
          {error ? <p className="text-sm text-rose-300">{error}</p> : null}
          <button
            type="submit"
            disabled={isSubmitting}
            className="rounded-full bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting
              ? mode === "register"
                ? "Creating account..."
                : "Logging in..."
              : mode === "register"
                ? "Create account"
                : "Log in"}
          </button>
        </form>
      )}
    </section>
  );
}
