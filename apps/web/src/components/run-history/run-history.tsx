"use client";

import Link from "next/link";
import type { RunSummary } from "@/types/agent";

const states: Record<string, string> = {
  awaiting_resume: "等待简历", awaiting_jd: "等待职位描述", analyzing: "分析中",
  proposal_ready: "建议待确认", applying: "生成版本中", version_ready: "版本已生成",
  exporting: "导出中", completed: "已完成", failed: "需要处理",
};

export function RunHistory({ runs, selectedId, hasMore = false, onLoadMore }: { runs: RunSummary[]; selectedId?: string; hasMore?: boolean; onLoadMore?: () => void }) {
  return (
    <nav className="run-history" aria-label="对话历史">
      <div className="panel-heading"><span className="eyebrow">你的工作台</span><h2>简历对话</h2></div>
      <Link href="/dashboard/resume/agent" className="button button-primary focus-ring new-run">新建对话</Link>
      <div className="run-list">
        {runs.length === 0 ? <p className="empty-copy">还没有对话。创建一次简历优化，记录会保存在这里。</p> : runs.map((run) => (
          <Link key={run.id} href={`/dashboard/resume/agent/${run.id}`} aria-current={run.id === selectedId ? "page" : undefined} className="run-row focus-ring">
            <strong>简历优化</strong>
            <span>{new Intl.DateTimeFormat("zh-CN", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(run.created_at))}</span>
            <span className="run-state">{states[run.state] ?? run.state}</span>
          </Link>
        ))}
      </div>
      {hasMore && <button className="button button-secondary focus-ring load-more" onClick={onLoadMore}>加载更早记录</button>}
    </nav>
  );
}

