"use client";

import { Send } from "lucide-react";
import { useState } from "react";

export function Composer({ onSend, disabled = false }: { onSend: (content: string) => Promise<void>; disabled?: boolean }) {
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string>();
  async function submit() {
    const content = draft.trim();
    if (!content || sending || disabled) return;
    setSending(true); setError(undefined);
    try { await onSend(content); setDraft(""); }
    catch { setError("消息未发送。内容已保留，请重试。"); }
    finally { setSending(false); }
  }
  return (
    <div className="composer-wrap">
      <div className="composer-box">
        <textarea className="composer-input focus-ring" aria-label="给求职教练发送消息" placeholder="描述你的目标、疑问或补充真实经历…" value={draft} rows={1} disabled={disabled} onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); void submit(); } }} />
        <button className="composer-send focus-ring" aria-label="发送消息" disabled={!draft.trim() || sending || disabled} onClick={() => void submit()}><Send size={19} /></button>
      </div>
      {error && <p className="composer-error" role="alert">{error}</p>}
      <p className="composer-note">AI 可能出错，重要内容请核实。你的每项修改都需要确认。</p>
    </div>
  );
}

