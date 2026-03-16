"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";

import {
  createCheckout,
  fetchBillingPlans,
  fetchCurrentSubscription,
  fetchSessionUser,
  selectSubscription,
} from "@/lib/api";

export function SettingsClient() {
  const queryClient = useQueryClient();
  const searchParams = useSearchParams();
  const { data: user } = useQuery({
    queryKey: ["session"],
    queryFn: fetchSessionUser,
  });
  const { data: plans = [] } = useQuery({
    queryKey: ["billing-plans"],
    queryFn: fetchBillingPlans,
  });
  const { data: subscription } = useQuery({
    queryKey: ["subscription"],
    queryFn: fetchCurrentSubscription,
  });

  const mutation = useMutation({
    mutationFn: selectSubscription,
    onSuccess: (data) => {
      queryClient.setQueryData(["subscription"], data);
    },
  });

  const checkoutMutation = useMutation({
    mutationFn: createCheckout,
    onSuccess: (data) => {
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    },
  });
  const checkoutMode = searchParams.get("checkout");
  const checkoutPlan = searchParams.get("plan");

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-6 py-16">
      <section className="space-y-4">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Account and billing</p>
        <h1 className="text-4xl font-semibold text-white">Settings</h1>
        <p className="max-w-3xl text-sm leading-7 text-slate-300">
          This settings surface is the first billing-aware shell around the validation product. It
          uses the backend billing foundation and current session state.
        </p>
      </section>

      {checkoutMode ? (
        <section className="rounded-[2rem] border border-cyan-400/20 bg-cyan-400/10 p-6 text-sm text-cyan-100">
          {checkoutMode === "mock" ? (
            <div className="space-y-3">
              <p>
                Mock checkout completed for the <strong>{checkoutPlan}</strong> plan. In development
                mode you can activate the subscription below without a real card processor.
              </p>
              {checkoutPlan ? (
                <button
                  type="button"
                  onClick={() => mutation.mutate(checkoutPlan)}
                  className="rounded-full border border-cyan-300/30 px-4 py-2 text-sm font-medium text-cyan-100 transition hover:border-cyan-200 hover:bg-white/5"
                >
                  Activate {checkoutPlan} plan
                </button>
              ) : null}
            </div>
          ) : checkoutMode === "success" ? (
            <p>Checkout completed successfully. Refresh the subscription panel if the plan is still updating.</p>
          ) : (
            <p>Checkout was cancelled before confirmation.</p>
          )}
        </section>
      ) : null}

      <section className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr]">
        <article className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-6">
          <h2 className="text-2xl font-semibold text-white">Account</h2>
          <div className="mt-6 space-y-3 text-sm text-slate-300">
            <p>
              <span className="text-slate-500">Email:</span>{" "}
              {user?.email ?? "Sign in to view account details"}
            </p>
            <p>
              <span className="text-slate-500">Role:</span> {user?.role ?? "guest"}
            </p>
            <p>
              <span className="text-slate-500">Current plan:</span>{" "}
              {subscription?.plan_name ?? "free"}
            </p>
            <p>
              <span className="text-slate-500">Plan status:</span>{" "}
              {subscription?.status ?? "inactive"}
            </p>
            <p>
              <span className="text-slate-500">Run limit:</span>{" "}
              {subscription?.run_limit ?? 1}
            </p>
          </div>
        </article>

        <article className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-6">
          <h2 className="text-2xl font-semibold text-white">Billing plans</h2>
          <div className="mt-6 grid gap-4 md:grid-cols-3">
            {plans.map((plan) => (
              <div
                key={plan.name}
                className="rounded-3xl border border-white/10 bg-slate-950/70 p-5"
              >
                <p className="text-xs uppercase tracking-[0.18em] text-cyan-200">{plan.name}</p>
                <p className="mt-3 text-3xl font-semibold text-white">
                  ${plan.price}
                </p>
                <p className="mt-2 text-xs uppercase tracking-[0.18em] text-slate-500">
                  {plan.run_limit} runs
                </p>
                <p className="mt-3 text-sm leading-7 text-slate-300">{plan.description}</p>
                <button
                  type="button"
                  onClick={() => mutation.mutate(plan.name)}
                  disabled={!user || mutation.isPending}
                  className="mt-5 rounded-full border border-cyan-400/30 px-4 py-2 text-sm font-medium text-cyan-200 transition hover:border-cyan-300 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {subscription?.plan_name === plan.name ? "Current plan" : "Select plan"}
                </button>
                {plan.name !== "free" ? (
                  <button
                    type="button"
                    onClick={() => checkoutMutation.mutate(plan.name)}
                    disabled={!user || checkoutMutation.isPending}
                    className="mt-3 rounded-full border border-white/10 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-white/30 hover:bg-white/5 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {checkoutMutation.isPending ? "Preparing checkout..." : "Start checkout"}
                  </button>
                ) : null}
              </div>
            ))}
          </div>
        </article>
      </section>
    </div>
  );
}
