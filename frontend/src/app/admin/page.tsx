import type { Metadata } from "next";

import { AdminOverviewClient } from "@/components/admin-overview-client";

export const metadata: Metadata = {
  title: "Admin overview",
  description:
    "Inspect production-oriented run status totals, provider usage, and recent failures for the Validuj platform.",
  robots: {
    index: false,
    follow: false,
  },
};

export default async function AdminPage() {
  return <AdminOverviewClient />;
}
