import { AgentApiError } from "./errors";
import { consumeAgentEvents } from "./sse";

function streamResponse(chunks: string[], status = 200) {
  const encoder = new TextEncoder();
  return new Response(new ReadableStream({ start(controller) { chunks.forEach((chunk) => controller.enqueue(encoder.encode(chunk))); controller.close(); } }), { status, headers: { "Content-Type": "text/event-stream" } });
}

describe("SSE", () => {
  it("parses split and multiple frames while ignoring comments and malformed data", async () => {
    const events: unknown[] = [];
    const fetcher = vi.fn<typeof fetch>(async () => streamResponse([
      ": ready\n\nid: 2\nevent: snap", "shot\ndata: {\"sequence\":2}\n\n",
      "id: 3\nevent: snapshot\ndata: nope\n\nid: 4\ndata: {\"sequence\":4}\n\n",
    ]));
    const cursor = await consumeAgentEvents({ url: "https://agent.test/events?after=1", token: "secret", after: 1, onEvent: (event) => events.push(event), fetcher });
    expect(cursor).toBe(4);
    expect(events).toHaveLength(2);
    expect(events).toMatchObject([{ id: 2 }, { id: 4 }]);
    const [url, init] = fetcher.mock.calls[0];
    expect(url).not.toContain("secret");
    expect(new Headers(init?.headers).get("Authorization")).toBe("Bearer secret");
  });

  it("never moves the cursor backward or emits duplicates", async () => {
    const seen: number[] = [];
    const response = streamResponse(["id: 8\ndata: {}\n\nid: 7\ndata: {}\n\nid: 8\ndata: {}\n\nid: 9\ndata: {}\n\n"]);
    const cursor = await consumeAgentEvents({ url: "x", token: "t", after: 7, onEvent: (event) => seen.push(event.id), fetcher: async () => response });
    expect(seen).toEqual([8, 9]);
    expect(cursor).toBe(9);
  });

  it("normalizes expired auth and aborts", async () => {
    const auth = await consumeAgentEvents({ url: "x", token: "t", after: 0, onEvent: vi.fn(), fetcher: async () => new Response(null, { status: 401 }) }).catch((error) => error);
    expect(auth).toMatchObject({ code: "auth_expired" });
    const aborted = new DOMException("stop", "AbortError");
    const error = await consumeAgentEvents({ url: "x", token: "t", after: 0, onEvent: vi.fn(), fetcher: async () => { throw aborted; } }).catch((value) => value);
    expect(error).toBeInstanceOf(AgentApiError);
    expect(error).toMatchObject({ code: "aborted" });
  });
});
