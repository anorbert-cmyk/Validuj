"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import {
  createCheckout,
  fetchCurrentSubscription,
  fetchSessionUser,
  type BillingPlan,
} from "@/lib/api";

export function PricingClient({ initialPlans }: { initialPlans: BillingPlan[] }) {
  const { data: session } = useQuery({
    queryKey: ["session"],
    queryFn: fetchSessionUser,
    initialData: null,
  });
  const { data: subscription } = useQuery({
    queryKey: ["subscription"],
    queryFn: fetchCurrentSubscription,
    initialData: null,
  });
  const checkoutMutation = useMutation({
    mutationFn: createCheckout,
    onSuccess: (data) => {
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    },
  });

  return (
    <section className="grid gap-6 lg:grid-cols-2 xl:grid-cols-4">
      {initialPlans.map((tier) => {
        const isCurrent = subscription?.plan_name === tier.name;
        const canCheckout = !!session && tier.name !== "free";
        return (
          <article
            key={tier.name}
            className="rounded-[2rem] border border-white/10 bg-slate-900/60 p-8 shadow-lg shadow-slate-950/30"
          >
            <p className="text-sm uppercase tracking-[0.18em] text-cyan-200">{tier.name}</p>
            <h2 className="mt-4 text-4xl font-semibold text-white">${tier.price}</h2>
            <p className="mt-2 text-xs uppercase tracking-[0.18em] text-slate-500">
              {tier.run_limit} runs
            </p>
            <p className="mt-4 text-sm leading-7 text-slate-300">{tier.description}</p>
            <ul className="mt-6 space-y-3 text-sm text-slate-200">
              <li className="flex gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-cyan-300" />
                <span>Six-agent report generation</span>
              </li>
              <li className="flex gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-cyan-300" />
                <span>Live progress and persisted report history</span>
              </li>
              <li className="flex gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-cyan-300" />
                <span>Plan-gated run capacity</span>
              </li>
            </ul>
            <div className="mt-6 flex flex-col gap-3">
              <button
                type="button"
                disabled={!canCheckout || checkoutMutation.isPending || isCurrent}
                onClick={() => checkoutMutation.mutate(tier.name)}
                className="rounded-full bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isCurrent
                  ? "Current plan"
                  : !session
                    ? "Sign in to continue"
                    : checkoutMutation.isPending
                      ? "Preparing checkout..."
                      : tier.name === "free"
                        ? "Included"
                        : "Start checkout"}
              </button>
              {tier.name !== "free" ? (
                <a
                  href="/settings"
                  className="rounded-full border border-white/10 px-5 py-3 text-center text-sm text-slate-200 transition hover:border-white/30 hover:bg-white/5"
                >
                  Manage in settings
                </a>
              ) : null}
            </div>
          </article>
        );
      })}
    </section>
  );
}
