import type { Metadata } from "next";

import { AuthCard } from "@/components/auth-card";
import { DashboardClient } from "@/components/dashboard-client";

export const metadata: Metadata = {
  title: "Dashboard",
  description:
    "Use the product dashboard to create startup validation runs and monitor recent analysis activity.",
};

export default async function DashboardPage() {
  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-6 py-16">
      <AuthCard initialUser={null} />
      <DashboardClient initialProjects={[]} initialRuns={[]} />
    </div>
  );
}
