import type { Metadata } from "next";

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
  return <SettingsClient />;
}
