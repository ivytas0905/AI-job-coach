"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { RunSnapshot } from "@/types/agent";
import { AgentApiError } from "@/lib/api/errors";

const activeStates = new Set(["analyzing", "applying", "exporting"]);
export type RunControllerStatus = "loading" | "ready" | "reconnecting" | "error" | "auth-expired" | "conflict";

export interface RunApi {
  getRun(id: string): Promise<RunSnapshot>;
  sendMessage(id: string, content: string): Promise<RunSnapshot>;
  events(id: string, after: number, onEvent: () => void, signal?: AbortSignal): Promise<number>;
}

export function useRunController(runId: string, client: RunApi | null) {
  const [snapshot, setSnapshot] = useState<RunSnapshot>();
  const [status, setStatus] = useState<RunControllerStatus>("loading");
  const reloadInFlight = useRef<Promise<void> | null>(null);
  const snapshotRef = useRef<RunSnapshot | undefined>(undefined);
  const reloadTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const applySnapshot = useCallback((next: RunSnapshot) => { snapshotRef.current = next; setSnapshot(next); setStatus("ready"); }, []);

  const reload = useCallback(() => {
    if (!client) return Promise.resolve();
    if (reloadInFlight.current) return reloadInFlight.current;
    const task = client.getRun(runId).then(applySnapshot).catch((error) => {
      setStatus(error instanceof AgentApiError && error.code === "auth_expired" ? "auth-expired" : "error");
    }).finally(() => { reloadInFlight.current = null; });
    reloadInFlight.current = task;
    return task;
  }, [applySnapshot, client, runId]);

  useEffect(() => { setStatus("loading"); void reload(); }, [reload]);
  const workflowState = snapshot?.run.state;
  useEffect(() => {
    if (!client || !workflowState || !activeStates.has(workflowState)) return;
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    const connect = async () => {
      try {
        await client.events(runId, snapshotRef.current?.latest_event_sequence ?? 0, () => {
          if (reloadTimer.current) clearTimeout(reloadTimer.current);
          reloadTimer.current = setTimeout(() => void reload(), 100);
        }, controller.signal);
        if (!controller.signal.aborted) { setStatus("reconnecting"); timer = setTimeout(connect, 1500); }
      } catch (error) {
        if (controller.signal.aborted) return;
        if (error instanceof AgentApiError && error.code === "auth_expired") setStatus("auth-expired");
        else { setStatus("reconnecting"); timer = setTimeout(connect, 3000); }
      }
    };
    void connect();
    return () => { controller.abort(); if (timer) clearTimeout(timer); if (reloadTimer.current) clearTimeout(reloadTimer.current); };
  }, [client, reload, runId, workflowState]);

  const send = async (content: string) => {
    if (!client) return;
    try { applySnapshot(await client.sendMessage(runId, content)); }
    catch (error) { if (error instanceof AgentApiError && error.code === "conflict") { await reload(); setStatus("conflict"); } throw error; }
  };
  return { snapshot, status, reload, applySnapshot, send };
}
