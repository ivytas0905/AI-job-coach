"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { RunSnapshot } from "@/types/agent";
import { AgentApiError } from "@/lib/api/errors";

const activeStates = new Set(["analyzing", "applying", "exporting"]);

export interface RunApi {
  getRun(id: string): Promise<RunSnapshot>;
  sendMessage(id: string, content: string): Promise<RunSnapshot>;
  events(id: string, after: number, onEvent: () => void, signal?: AbortSignal): Promise<number>;
}

export function useRunController(runId: string, client: RunApi | null) {
  const [snapshot, setSnapshot] = useState<RunSnapshot>();
  const [status, setStatus] = useState<"loading" | "ready" | "reconnecting" | "error" | "auth-expired">("loading");
  const reloadInFlight = useRef<Promise<void> | null>(null);

  const reload = useCallback(() => {
    if (!client) return Promise.resolve();
    if (reloadInFlight.current) return reloadInFlight.current;
    const task = client.getRun(runId).then((next) => { setSnapshot(next); setStatus("ready"); }).catch((error) => {
      setStatus(error instanceof AgentApiError && error.code === "auth_expired" ? "auth-expired" : "error");
    }).finally(() => { reloadInFlight.current = null; });
    reloadInFlight.current = task;
    return task;
  }, [client, runId]);

  useEffect(() => { setStatus("loading"); void reload(); }, [reload]);
  useEffect(() => {
    if (!client || !snapshot || !activeStates.has(snapshot.run.state)) return;
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    const connect = async () => {
      try {
        await client.events(runId, snapshot.latest_event_sequence, () => { void reload(); }, controller.signal);
        if (!controller.signal.aborted) { setStatus("reconnecting"); timer = setTimeout(connect, 1500); }
      } catch (error) {
        if (controller.signal.aborted) return;
        if (error instanceof AgentApiError && error.code === "auth_expired") setStatus("auth-expired");
        else { setStatus("reconnecting"); timer = setTimeout(connect, 3000); }
      }
    };
    void connect();
    return () => { controller.abort(); if (timer) clearTimeout(timer); };
  }, [client, reload, runId, snapshot]);

  const send = async (content: string) => {
    if (!client) return;
    try { setSnapshot(await client.sendMessage(runId, content)); setStatus("ready"); }
    catch (error) { if (error instanceof AgentApiError && error.code === "conflict") await reload(); throw error; }
  };
  return { snapshot, status, reload, send };
}

