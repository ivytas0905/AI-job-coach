import { AgentApiError } from "./errors";
import { createAgentClient, safeFilename } from "./agent-client";

const snapshot = { run: { id: "run-1" }, messages: [] };

describe("agent client", () => {
  it("authenticates JSON and never places the token in the URL", async () => {
    const fetcher = vi.fn<typeof fetch>(async () => new Response(JSON.stringify(snapshot), { status: 200 }));
    const client = createAgentClient({ origin: "https://agent.test/", getToken: async () => "secret-token", fetcher });
    await client.sendMessage("run 1", "hello");
    const [url, init] = fetcher.mock.calls[0];
    expect(url).toBe("https://agent.test/api/v1/agent/runs/run%201/messages");
    expect(url).not.toContain("secret-token");
    expect(new Headers(init?.headers).get("Authorization")).toBe("Bearer secret-token");
    expect(JSON.parse(String(init?.body))).toEqual({ content: "hello" });
  });

  it("authenticates multipart without overriding its content type", async () => {
    const fetcher = vi.fn<typeof fetch>(async () => new Response(JSON.stringify(snapshot), { status: 200 }));
    const client = createAgentClient({ origin: "https://agent.test", getToken: async () => "token", fetcher });
    await client.submitResume("run", new File(["resume"], "resume.pdf", { type: "application/pdf" }));
    const init = fetcher.mock.calls[0][1];
    expect(init?.body).toBeInstanceOf(FormData);
    expect(new Headers(init?.headers).has("Content-Type")).toBe(false);
    expect(new Headers(init?.headers).get("Authorization")).toBe("Bearer token");
  });

  it.each([
    [400, "bad_request"], [401, "auth_expired"], [404, "not_found"], [409, "conflict"],
    [413, "too_large"], [422, "validation"], [500, "server"],
  ])("normalizes HTTP %i without exposing backend text", async (status, code) => {
    const client = createAgentClient({ origin: "https://agent.test", getToken: async () => "token", fetcher: async () => new Response("private resume text", { status }) });
    const error = await client.getRun("run").catch((value) => value);
    expect(error).toBeInstanceOf(AgentApiError);
    expect(error).toMatchObject({ code, status });
    expect(error.message).not.toContain("private resume text");
  });

  it("authenticates downloads and sanitizes the response filename", async () => {
    const fetcher = vi.fn<typeof fetch>(async () => new Response("pdf", { headers: { "Content-Type": "application/pdf", "Content-Disposition": 'attachment; filename="../bad\\resume.pdf"' } }));
    const client = createAgentClient({ origin: "https://agent.test", getToken: async () => "token", fetcher });
    const result = await client.downloadExport("run", "export");
    expect(result.filename).toBe("badresume.pdf");
    const [url, init] = fetcher.mock.calls[0];
    expect(url).not.toContain("token");
    expect(new Headers(init?.headers).get("Authorization")).toBe("Bearer token");
  });

  it("falls back for unsafe or empty filenames", () => {
    expect(safeFilename('attachment; filename="../../"', "resume.pdf")).toBe("resume.pdf");
    expect(safeFilename("attachment; filename*=UTF-8''my%20resume.pdf", "fallback")).toBe("my resume.pdf");
  });
});
