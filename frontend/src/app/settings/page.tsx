import type { Metadata } from "next";
import { Suspense } from "react";

import { SettingsClient } from "@/components/settings-client";

export const metadata: Metadata = {
  title: "Settings",
  description: "Manage account and billing settings for the Validuj product shell.",
  robots: {
    index: false,
    follow: false,
  },
};

export default function SettingsPage() {
  return (
    <Suspense
      fallback={
        <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-6 py-16 text-sm text-slate-300">
          Loading settings...
        </div>
      }
    >
      <SettingsClient />
    </Suspense>
  );
}
