import { AgentRouteClient } from "@/components/workspace/agent-route-client";

export default async function RunPage({ params }: { params: Promise<{ runId: string }> }) {
  const { runId } = await params;
  return <AgentRouteClient runId={runId} />;
}
