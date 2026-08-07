"use client";

import { WorkspaceDrawer } from "@/components/shell/workspace-drawer";

export function WorkspaceShell({ history, conversation, artifacts }: { history: React.ReactNode; conversation: React.ReactNode; artifacts: React.ReactNode }) {
  return (
    <div className="agent-page">
      <header className="agent-mobile-bar">
        <WorkspaceDrawer title="对话历史" triggerLabel="历史" side="left"><div className="drawer-scroll">{history}</div></WorkspaceDrawer>
        <span className="mobile-brand">AI Job Coach</span>
        <WorkspaceDrawer title="简历工作区" triggerLabel="材料" side="right"><div className="drawer-scroll">{artifacts}</div></WorkspaceDrawer>
      </header>
      <aside className="history-column">{history}</aside>
      <main className="conversation-column" aria-label="求职教练对话">{conversation}</main>
      <aside className="artifact-column" aria-label="简历材料工作区">{artifacts}</aside>
    </div>
  );
}
