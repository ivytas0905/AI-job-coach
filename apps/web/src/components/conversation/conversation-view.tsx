"use client";

import { useEffect, useRef, useState } from "react";
import type { MessageRecord, RunSnapshot, WorkflowState } from "@/types/agent";
import { Composer } from "./composer";

function Message({ message }: { message: MessageRecord }) {
  return <article className={`message message-${message.role}`}><div className="message-label">{message.role === "user" ? "你" : "求职教练"}</div><p>{message.content}</p></article>;
}

const workflowLabels: Record<WorkflowState, string> = { awaiting_resume: "等待上传简历", awaiting_jd: "等待职位描述", analyzing: "正在分析材料", proposal_ready: "修改建议待确认", applying: "正在生成版本", version_ready: "新版本已生成", exporting: "正在导出", completed: "已完成", failed: "需要处理" };

export function ConversationView({ snapshot, status, onSend, signInHref = "/sign-in" }: { snapshot?: RunSnapshot; status: string; onSend: (content: string) => Promise<void>; signInHref?: string }) {
  const scroller = useRef<HTMLDivElement>(null);
  const [nearEnd, setNearEnd] = useState(true);
  useEffect(() => { if (nearEnd && scroller.current) scroller.current.scrollTop = scroller.current.scrollHeight; }, [nearEnd, snapshot?.messages.length]);
  if (!snapshot) return <div className="conversation-status" role="status">{status === "error" ? "暂时无法读取这次对话。" : status === "auth-expired" ? "登录已过期，工作已安全保存。" : "正在载入对话…"}</div>;
  const connection = status === "reconnecting" ? "正在恢复连接…" : status === "conflict" ? "已同步最新内容；刚才的命令没有自动重试。" : status === "auth-expired" ? "登录已过期，工作已安全保存。" : workflowLabels[snapshot.run.state];
  return (
    <div className="conversation-view">
      <header className="conversation-header"><div><span className="eyebrow">专属求职教练</span><h1>简历优化对话</h1></div><span className="connection-state" role="status">{connection}</span></header>
      <div className="message-scroll" data-testid="message-scroll" ref={scroller} onScroll={(event) => { const node = event.currentTarget; setNearEnd(node.scrollHeight - node.scrollTop - node.clientHeight < 96); }}>
        <div className="message-list">{snapshot.messages.length ? snapshot.messages.map((message) => <Message key={message.id} message={message} />) : <div className="conversation-welcome"><h2>先从你的目标开始</h2><p>告诉我你想申请什么岗位，或者先上传简历和职位描述。</p></div>}</div>
      </div>
      {!nearEnd && <button className="button button-secondary jump-latest" onClick={() => { if (scroller.current) scroller.current.scrollTop = scroller.current.scrollHeight; setNearEnd(true); }}>跳到最新消息</button>}
      {status === "auth-expired" && <div className="auth-recovery" role="alert">登录已过期，但草稿和已保存工作不会丢失。<a href={signInHref}>重新登录</a></div>}
      <Composer onSend={onSend} disabled={status === "auth-expired"} />
    </div>
  );
}
