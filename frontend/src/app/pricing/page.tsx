import type { Metadata } from "next";

import { PricingClient } from "@/components/pricing-client";
import { fetchBillingPlans } from "@/lib/api";

export const metadata: Metadata = {
  title: "Pricing",
  description:
    "Explore the planned production pricing model for Validuj, from founder discovery to advanced validation workflows.",
};

export default async function PricingPage() {
  const plans = await fetchBillingPlans().catch(() => []);

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-10 px-6 py-16">
      <section className="space-y-5">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-200">Pricing</p>
        <h1 className="max-w-4xl text-5xl font-semibold tracking-tight text-white">
          Pricing designed around serious validation work.
        </h1>
        <p className="max-w-3xl text-base leading-8 text-slate-300">
          The pricing surface now reads from the live billing foundation in the backend. It is still a
          local product shell rather than a real payment gateway integration, but plan names, prices,
          and run limits are already enforced through the protected API layer.
        </p>
      </section>

      <PricingClient initialPlans={plans} />
    </div>
  );
}
