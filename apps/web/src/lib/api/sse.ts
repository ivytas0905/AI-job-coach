import { AgentApiError, normalizeHttpError, normalizeRequestError } from "./errors";

export interface AgentEvent { id: number; event: string; data: unknown }

export interface EventStreamOptions {
  url: string; token: string; after: number; signal?: AbortSignal;
  onEvent: (event: AgentEvent) => void;
  fetcher?: typeof fetch;
}

function parseFrame(frame: string): AgentEvent | null {
  let id: number | undefined;
  let event = "message";
  const data: string[] = [];
  for (const line of frame.split(/\r?\n/)) {
    if (!line || line.startsWith(":")) continue;
    const separator = line.indexOf(":");
    const field = separator < 0 ? line : line.slice(0, separator);
    const value = separator < 0 ? "" : line.slice(separator + 1).replace(/^ /, "");
    if (field === "id" && /^\d+$/.test(value)) id = Number(value);
    if (field === "event") event = value;
    if (field === "data") data.push(value);
  }
  if (id === undefined || data.length === 0) return null;
  try { return { id, event, data: JSON.parse(data.join("\n")) }; }
  catch { return null; }
}

export async function consumeAgentEvents(options: EventStreamOptions): Promise<number> {
  const fetcher = options.fetcher ?? fetch;
  let cursor = options.after;
  try {
    const response = await fetcher(options.url, {
      headers: { Accept: "text/event-stream", Authorization: `Bearer ${options.token}` },
      cache: "no-store", signal: options.signal,
    });
    if (!response.ok) throw normalizeHttpError(response.status);
    if (!response.body) throw new AgentApiError("network");
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { done, value } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });
      const frames = buffer.split(/\r?\n\r?\n/);
      buffer = frames.pop() ?? "";
      for (const frame of frames) {
        const parsed = parseFrame(frame);
        if (parsed && parsed.id > cursor) {
          cursor = parsed.id;
          options.onEvent(parsed);
        }
      }
      if (done) break;
    }
    return cursor;
  } catch (error) {
    throw normalizeRequestError(error);
  }
}

