import type { Metadata } from "next";

import { RunDetailClient } from "@/components/run-detail-client";
import { fetchRun } from "@/lib/api";

type RunDetailPageProps = {
  params: Promise<{ runId: string }>;
};

export async function generateMetadata({ params }: RunDetailPageProps): Promise<Metadata> {
  const { runId } = await params;
  return {
    title: `Run ${runId}`,
    description: "Private live run detail page for a Validuj analysis.",
    robots: {
      index: false,
      follow: false,
    },
  };
}

export default async function RunDetailPage({ params }: RunDetailPageProps) {
  const { runId } = await params;
  const run = await fetchRun(runId);

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-6 py-16">
      <RunDetailClient initialRun={run} />
    </div>
  );
}
