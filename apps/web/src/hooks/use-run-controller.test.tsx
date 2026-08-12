import { act, renderHook, waitFor } from "@testing-library/react";
import type { RunSnapshot } from "@/types/agent";
import { AgentApiError } from "@/lib/api/errors";
import { useRunController } from "./use-run-controller";

const snap = (id: string): RunSnapshot => ({ run: { id, state: "completed", revision: 1, provider: "p", model: "m", current_version_id: null, created_at: "2026-08-12T00:00:00Z" }, resume: null, job_description: null, messages: [], proposals: [], decisions: [], versions: [], exports: [], latest_event_sequence: 0 });
const deferred = <T,>() => { let resolve!: (value: T) => void; const promise = new Promise<T>((done) => { resolve = done; }); return { promise, resolve }; };

describe("useRunController", () => {
  it("discards a late snapshot after the run changes", async () => {
    const old = deferred<RunSnapshot>();
    const client = { getRun: vi.fn((id: string) => id === "a" ? old.promise : Promise.resolve(snap("b"))), sendMessage: vi.fn(), events: vi.fn() };
    const { result, rerender } = renderHook(({ id }) => useRunController(id, client), { initialProps: { id: "a" } });
    rerender({ id: "b" });
    await waitFor(() => expect(result.current.snapshot?.run.id).toBe("b"));
    await act(async () => old.resolve(snap("a")));
    expect(result.current.snapshot?.run.id).toBe("b");
  });

  it("reloads and announces a guarded mutation conflict without replay", async () => {
    const client = { getRun: vi.fn().mockResolvedValue(snap("a")), sendMessage: vi.fn(), events: vi.fn() };
    const { result } = renderHook(() => useRunController("a", client));
    await waitFor(() => expect(result.current.status).toBe("ready"));
    await act(async () => { await expect(result.current.guardMutation(Promise.reject(new AgentApiError("conflict", 409)))).rejects.toMatchObject({ code: "conflict" }); });
    expect(client.getRun).toHaveBeenCalledTimes(2);
    await waitFor(() => expect(result.current.status).toBe("conflict"));
  });
});
