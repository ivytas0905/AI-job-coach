"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { createAgentClient } from "@/lib/api/agent-client";
import type { RunSummary } from "@/types/agent";
import { RunHistory } from "@/components/run-history/run-history";
import { WorkspaceShell } from "./workspace-shell";
import { ConversationView } from "@/components/conversation/conversation-view";
import { useRunController } from "@/hooks/use-run-controller";
import { ArtifactWorkspace } from "@/components/artifacts/artifact-workspace";

const origin = process.env.NEXT_PUBLIC_AGENT_API_ORIGIN;

export function AgentRouteClient({ runId }: { runId?: string }) {
  const { getToken } = useAuth();
  const router = useRouter();
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const client = useMemo(() => origin ? createAgentClient({ origin, getToken }) : null, [getToken]);
  const controller = useRunController(runId ?? "", runId ? client : null);

  useEffect(() => {
    if (!client) { setError("尚未配置 Agent API 地址。"); setLoading(false); return; }
    client.listRuns().then((result) => { setRuns(result.items); setNextCursor(result.next_cursor); }).catch(() => setError("暂时无法读取对话记录，请稍后重试。")).finally(() => setLoading(false));
  }, [client]);

  async function loadMore() {
    if (!client || !nextCursor) return;
    const result = await client.listRuns(nextCursor);
    setRuns((current) => [...current, ...result.items.filter((item) => !current.some((existing) => existing.id === item.id))]);
    setNextCursor(result.next_cursor);
  }

  async function createRun() {
    if (!client) return;
    setLoading(true);
    setError(undefined);
    try { const snapshot = await client.createRun(); router.push(`/dashboard/resume/agent/${snapshot.run.id}`); }
    catch { setError("新建对话失败，请稍后重试。"); setLoading(false); }
  }

  const history = <RunHistory runs={runs} selectedId={runId} hasMore={Boolean(nextCursor)} onLoadMore={loadMore} />;
  const conversation = runId ? <ConversationView snapshot={controller.snapshot} status={controller.status} onSend={controller.send} /> : (
    <div className="route-empty"><span className="eyebrow">新的优化任务</span><h1>准备好让简历更贴近目标岗位了吗？</h1><p>我会先了解你的真实经历，再逐条提出有依据的修改建议。所有改动都由你确认。</p><button className="button button-primary focus-ring" disabled={loading} onClick={createRun}>{loading ? "正在准备…" : "开始一次对话"}</button>{error && <p role="alert" className="inline-error">{error}</p>}</div>
  );
  const refresh = async <T,>(task: Promise<T>) => { const result = await task; await controller.reload(); return result; };
  const download = async (exportId: string) => {
    if (!client || !runId) return;
    const result = await client.downloadExport(runId, exportId);
    const href = URL.createObjectURL(result.blob);
    const link = document.createElement("a"); link.href = href; link.download = result.filename; link.click(); URL.revokeObjectURL(href);
  };
  const artifacts = runId && client && controller.snapshot ? <ArtifactWorkspace snapshot={controller.snapshot} actions={{
    submitResume: (file) => refresh(client.submitResume(runId, file)).then(() => undefined),
    submitJobDescription: (content) => refresh(client.submitJobDescription(runId, content)).then(() => undefined),
    recordEvidence: (content) => refresh(client.recordEvidence(runId, content)).then(() => undefined),
    decideProposal: (id, decision, revision, intent) => refresh(client.decideProposal(runId, id, decision, revision, { value: intent })).then(() => undefined),
    restoreVersion: (id, intent) => refresh(client.restoreVersion(runId, id, { value: intent })).then(() => undefined),
    createExport: (id, format, intent) => refresh(client.createExport(runId, id, format, { value: intent })).then(() => undefined),
    downloadExport: download,
  }} /> : <div className="artifact-placeholder"><span className="eyebrow">材料与版本</span><h2>简历工作区</h2><p>创建对话后即可上传材料并管理版本。</p></div>;
  return <WorkspaceShell history={history} conversation={conversation} artifacts={artifacts} />;
}
