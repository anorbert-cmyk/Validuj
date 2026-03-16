import type { Metadata } from "next";

import { DashboardClient } from "@/components/dashboard-client";
import { fetchRuns } from "@/lib/api";

export const metadata: Metadata = {
  title: "Dashboard",
  description:
    "Use the product dashboard to create startup validation runs and monitor recent analysis activity.",
};

export default async function DashboardPage() {
  const runs = await fetchRuns().catch(() => []);

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-6 py-16">
      <DashboardClient initialRuns={runs} />
    </div>
  );
}
