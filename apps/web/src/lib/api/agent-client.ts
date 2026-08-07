import type { ExportFormat, ExportRecord, ProposalDecision, RunList, RunSnapshot, VersionRecord } from "@/types/agent";
import type { IntentKey } from "./idempotency";
import { normalizeHttpError, normalizeRequestError } from "./errors";
import { consumeAgentEvents, type AgentEvent } from "./sse";

export interface DownloadResult { blob: Blob; filename: string; contentType: string }
export interface AgentClientOptions { origin: string; getToken: () => Promise<string | null>; fetcher?: typeof fetch }

function safeFilename(header: string | null, fallback: string): string {
  const encoded = header?.match(/filename\*=UTF-8''([^;]+)/i)?.[1];
  const quoted = header?.match(/filename="([^"]+)"/i)?.[1];
  let candidate = encoded ? (() => { try { return decodeURIComponent(encoded); } catch { return ""; } })() : quoted ?? "";
  candidate = candidate.replace(/[\\/\u0000-\u001f\u007f]/g, "").replace(/^\.+/, "").trim();
  return candidate || fallback;
}

export function createAgentClient(options: AgentClientOptions) {
  const origin = options.origin.replace(/\/$/, "");
  const fetcher = options.fetcher ?? fetch;
  const url = (path: string) => `${origin}/api/v1/agent${path}`;

  async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
    try {
      const token = await options.getToken();
      if (!token) throw normalizeHttpError(401);
      const headers = new Headers(init.headers);
      headers.set("Authorization", `Bearer ${token}`);
      headers.set("Accept", "application/json");
      if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
      const response = await fetcher(url(path), { ...init, headers, cache: "no-store" });
      if (!response.ok) throw normalizeHttpError(response.status);
      return await response.json() as T;
    } catch (error) { throw normalizeRequestError(error); }
  }

  const post = <T>(path: string, body?: unknown) => request<T>(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) });
  return {
    listRuns: (before?: string, limit = 20) => request<RunList>(`/runs?limit=${limit}${before ? `&before=${encodeURIComponent(before)}` : ""}`),
    createRun: () => post<RunSnapshot>("/runs"),
    getRun: (runId: string) => request<RunSnapshot>(`/runs/${encodeURIComponent(runId)}`),
    submitResume: (runId: string, file: File) => { const body = new FormData(); body.set("file", file); return request<RunSnapshot>(`/runs/${encodeURIComponent(runId)}/resume`, { method: "POST", body }); },
    submitJobDescription: (runId: string, content: string) => post<RunSnapshot>(`/runs/${encodeURIComponent(runId)}/job-description`, { content }),
    sendMessage: (runId: string, content: string) => post<RunSnapshot>(`/runs/${encodeURIComponent(runId)}/messages`, { content }),
    recordEvidence: (runId: string, content: string) => post<RunSnapshot>(`/runs/${encodeURIComponent(runId)}/evidence`, { content }),
    decideProposal: (runId: string, proposalId: string, decision: ProposalDecision, expectedRevision: number, intent: IntentKey, versionName?: string) => post<RunSnapshot>(`/runs/${encodeURIComponent(runId)}/proposals/${encodeURIComponent(proposalId)}/decisions`, { decision, expected_revision: expectedRevision, idempotency_key: intent.value, version_name: versionName }),
    getVersion: (runId: string, versionId: string) => request<VersionRecord>(`/runs/${encodeURIComponent(runId)}/versions/${encodeURIComponent(versionId)}`),
    restoreVersion: (runId: string, versionId: string, intent: IntentKey) => post<RunSnapshot>(`/runs/${encodeURIComponent(runId)}/versions/${encodeURIComponent(versionId)}/restore`, { idempotency_key: intent.value }),
    createExport: (runId: string, versionId: string, format: ExportFormat, intent: IntentKey) => post<ExportRecord>(`/runs/${encodeURIComponent(runId)}/versions/${encodeURIComponent(versionId)}/exports`, { format, idempotency_key: intent.value }),
    async downloadExport(runId: string, exportId: string): Promise<DownloadResult> {
      try {
        const token = await options.getToken();
        if (!token) throw normalizeHttpError(401);
        const response = await fetcher(url(`/runs/${encodeURIComponent(runId)}/exports/${encodeURIComponent(exportId)}/download`), { headers: { Authorization: `Bearer ${token}` }, cache: "no-store" });
        if (!response.ok) throw normalizeHttpError(response.status);
        return { blob: await response.blob(), filename: safeFilename(response.headers.get("Content-Disposition"), `resume-${exportId}`), contentType: response.headers.get("Content-Type") ?? "application/octet-stream" };
      } catch (error) { throw normalizeRequestError(error); }
    },
    async events(runId: string, after: number, onEvent: (event: AgentEvent) => void, signal?: AbortSignal) {
      const token = await options.getToken();
      if (!token) throw normalizeHttpError(401);
      return consumeAgentEvents({ url: url(`/runs/${encodeURIComponent(runId)}/events?after=${after}`), token, after, onEvent, signal, fetcher });
    },
  };
}

export { safeFilename };
