"use client";

import * as Tabs from "@radix-ui/react-tabs";
import { useRef, useState } from "react";
import { createIntentKey } from "@/lib/api/idempotency";
import type { ExportFormat, ProposalDecision, RunSnapshot } from "@/types/agent";

export interface ArtifactActions {
  submitResume(file: File): Promise<void>;
  submitJobDescription(content: string): Promise<void>;
  recordEvidence(content: string): Promise<void>;
  decideProposal(id: string, decision: ProposalDecision, revision: number, intent: string): Promise<void>;
  restoreVersion(id: string, intent: string): Promise<void>;
  createExport(id: string, format: ExportFormat, intent: string): Promise<void>;
  downloadExport(id: string): Promise<void>;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024;
const fileTypes = new Set(["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]);

function StructuredValue({ value }: { value: unknown }) {
  if (value === null || value === undefined) return <span className="empty-copy">暂无内容</span>;
  if (Array.isArray(value)) return <ul>{value.map((item, index) => <li key={index}><StructuredValue value={item} /></li>)}</ul>;
  if (typeof value === "object") return <dl className="structured-data">{Object.entries(value as Record<string, unknown>).map(([key, item]) => <div key={key}><dt>{key}</dt><dd><StructuredValue value={item} /></dd></div>)}</dl>;
  return <span>{String(value)}</span>;
}

export function ArtifactWorkspace({ snapshot, actions }: { snapshot: RunSnapshot; actions: ArtifactActions }) {
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState("");
  const [jd, setJd] = useState(snapshot.job_description?.raw_text ?? "");
  const intents = useRef(new Map<string, string>());
  const intentFor = (key: string) => {
    if (!intents.current.has(key)) intents.current.set(key, createIntentKey().value);
    return intents.current.get(key)!;
  };
  async function run(key: string, task: () => Promise<void>, success: string) {
    if (pending) return;
    setPending(key); setError(""); setNotice("");
    try { await task(); intents.current.delete(key); setNotice(success); }
    catch { setError("操作未完成，内容已保留，请重试。"); }
    finally { setPending(""); }
  }
  async function upload(file?: File) {
    if (!file || !fileTypes.has(file.type) || !/\.(pdf|docx)$/i.test(file.name)) { setError("请选择 PDF 或 DOCX 简历文件。"); return; }
    if (!file.size || file.size > MAX_FILE_SIZE) { setError("文件不能为空且不能超过 10 MB。"); return; }
    await run("resume", () => actions.submitResume(file), "简历已上传。");
  }
  const selectedVersion = snapshot.versions.find((version) => version.id === snapshot.run.current_version_id) ?? snapshot.versions.at(-1);

  return <section className="artifact-workspace" aria-label="简历工作区">
    <header className="artifact-heading"><span className="eyebrow">材料与版本</span><h2>简历工作区</h2></header>
    <Tabs.Root defaultValue={snapshot.run.state === "proposal_ready" ? "proposals" : "source"}>
      <Tabs.List className="artifact-tabs" aria-label="简历工作区内容">
        <Tabs.Trigger value="source">材料</Tabs.Trigger>
        <Tabs.Trigger value="proposals">修改建议{snapshot.proposals.some((p) => p.status === "pending") ? " · 待处理" : ""}</Tabs.Trigger>
        <Tabs.Trigger value="preview">预览</Tabs.Trigger>
        <Tabs.Trigger value="history">版本与导出</Tabs.Trigger>
      </Tabs.List>
      <div className="artifact-content">
        <Tabs.Content value="source">
          <h3>源简历</h3><p>{snapshot.resume?.filename ?? "尚未上传"}</p>
          <label className="file-control">上传简历文件<input aria-label="上传简历文件" type="file" accept=".pdf,.docx" disabled={Boolean(pending)} onChange={(event) => void upload(event.target.files?.[0])} /></label>
          <h3>职位描述</h3><textarea aria-label="职位描述" value={jd} onChange={(event) => setJd(event.target.value)} rows={8} />
          <button className="button button-primary" disabled={Boolean(pending) || jd.trim().length < 50} onClick={() => void run("jd", () => actions.submitJobDescription(jd.trim()), "职位描述已提交。")}>提交职位描述</button>
        </Tabs.Content>
        <Tabs.Content value="proposals">
          {snapshot.proposals.length === 0 ? <p className="empty-copy">分析完成后，修改建议会显示在这里。</p> : snapshot.proposals.map((proposal) => <article className="proposal-card" key={proposal.id}>
            <header><strong>建议 #{proposal.revision}</strong><span>{proposal.status}</span></header>
            <div className="diff-block diff-original"><small>原文</small><p>{proposal.affected_content}</p></div>
            <div className="diff-block diff-suggested"><small>建议</small><p>{proposal.suggested_replacement}</p></div>
            <p><strong>匹配理由：</strong>{proposal.jd_reason}</p>
            <div className="evidence"><strong>来源依据</strong><StructuredValue value={proposal.source_evidence} /></div>
            {proposal.evidence_request && <p className="evidence-request">需要补充：{proposal.evidence_request}</p>}
            <div className="proposal-actions">{([['accepted','接受这条建议'],['rejected','拒绝这条建议'],['revision_requested','要求修改建议']] as const).map(([decision, label]) => <button key={decision} className="button button-secondary" disabled={Boolean(pending) || proposal.status !== "pending"} onClick={() => void run(`${proposal.id}:${decision}`, () => actions.decideProposal(proposal.id, decision, proposal.revision, intentFor(`${proposal.id}:${decision}`)), "决定已保存。")}>{label}</button>)}</div>
          </article>)}
        </Tabs.Content>
        <Tabs.Content value="preview"><h3>{selectedVersion?.version_name ?? "简历预览"}</h3><div className="resume-preview"><StructuredValue value={selectedVersion?.content ?? snapshot.resume?.parsed_data} /></div></Tabs.Content>
        <Tabs.Content value="history">
          {snapshot.versions.length === 0 ? <p className="empty-copy">接受建议后会生成可恢复的版本。</p> : snapshot.versions.map((version) => <article className="version-row" key={version.id}><div><strong>{version.version_name}</strong><span>版本 {version.version_number}</span></div><button className="button button-secondary" disabled={Boolean(pending) || version.id === snapshot.run.current_version_id} onClick={() => void run(`restore:${version.id}`, () => actions.restoreVersion(version.id, intentFor(`restore:${version.id}`)), "版本已恢复。")}>恢复 {version.version_name}</button></article>)}
          {selectedVersion && <div className="export-actions">{(["pdf", "docx"] as const).map((format) => <button key={format} className="button button-primary" disabled={Boolean(pending)} onClick={() => void run(`export:${selectedVersion.id}:${format}`, () => actions.createExport(selectedVersion.id, format, intentFor(`export:${selectedVersion.id}:${format}`)), `${format.toUpperCase()} 已生成。`)}>导出 {format.toUpperCase()}</button>)}</div>}
          {snapshot.exports.map((item) => <button key={item.id} className="button button-secondary export-download" onClick={() => void actions.downloadExport(item.id)}>下载 {item.content_type.includes("pdf") ? "PDF" : "DOCX"}</button>)}
        </Tabs.Content>
      </div>
    </Tabs.Root>
    <div className="artifact-announcement" aria-live="polite">{notice}</div>{error && <p className="inline-error" role="alert">{error}</p>}
  </section>;
}
