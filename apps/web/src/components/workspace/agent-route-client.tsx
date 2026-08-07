"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { createAgentClient } from "@/lib/api/agent-client";
import type { RunSummary } from "@/types/agent";
import { RunHistory } from "@/components/run-history/run-history";
import { WorkspaceShell } from "./workspace-shell";

const origin = process.env.NEXT_PUBLIC_AGENT_API_ORIGIN;

export function AgentRouteClient({ runId }: { runId?: string }) {
  const { getToken } = useAuth();
  const router = useRouter();
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const client = useMemo(() => origin ? createAgentClient({ origin, getToken }) : null, [getToken]);

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
  const conversation = runId ? (
    <div className="route-placeholder"><span className="eyebrow">专属求职教练</span><h1>我们从你的经历出发</h1><p>对话内容正在准备中。你可以先在右侧查看简历和职位材料。</p></div>
  ) : (
    <div className="route-empty"><span className="eyebrow">新的优化任务</span><h1>准备好让简历更贴近目标岗位了吗？</h1><p>我会先了解你的真实经历，再逐条提出有依据的修改建议。所有改动都由你确认。</p><button className="button button-primary focus-ring" disabled={loading} onClick={createRun}>{loading ? "正在准备…" : "开始一次对话"}</button>{error && <p role="alert" className="inline-error">{error}</p>}</div>
  );
  const artifacts = <div className="artifact-placeholder"><span className="eyebrow">材料与版本</span><h2>简历工作区</h2><p>上传简历、职位描述、修改建议和导出版本会集中显示在这里。</p></div>;
  return <WorkspaceShell history={history} conversation={conversation} artifacts={artifacts} />;
}
