"use client";

import type { MessageRecord, RunSnapshot } from "@/types/agent";
import { Composer } from "./composer";

function Message({ message }: { message: MessageRecord }) {
  return <article className={`message message-${message.role}`}><div className="message-label">{message.role === "user" ? "你" : "求职教练"}</div><p>{message.content}</p></article>;
}

export function ConversationView({ snapshot, status, onSend }: { snapshot?: RunSnapshot; status: string; onSend: (content: string) => Promise<void> }) {
  if (!snapshot) return <div className="conversation-status" role="status">{status === "error" ? "暂时无法读取这次对话。" : "正在载入对话…"}</div>;
  return (
    <div className="conversation-view">
      <header className="conversation-header"><div><span className="eyebrow">专属求职教练</span><h1>简历优化对话</h1></div><span className="connection-state" role="status">{status === "reconnecting" ? "正在恢复连接…" : snapshot.run.state.replaceAll("_", " ")}</span></header>
      <div className="message-scroll">
        <div className="message-list">{snapshot.messages.length ? snapshot.messages.map((message) => <Message key={message.id} message={message} />) : <div className="conversation-welcome"><h2>先从你的目标开始</h2><p>告诉我你想申请什么岗位，或者先上传简历和职位描述。</p></div>}</div>
      </div>
      <Composer onSend={onSend} disabled={status === "auth-expired"} />
    </div>
  );
}

