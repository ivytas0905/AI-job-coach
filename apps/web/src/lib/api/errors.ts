export type AgentErrorCode =
  | "bad_request" | "auth_expired" | "not_found" | "conflict"
  | "too_large" | "validation" | "server" | "network" | "aborted";

export class AgentApiError extends Error {
  constructor(public readonly code: AgentErrorCode, public readonly status?: number) {
    super(code);
    this.name = "AgentApiError";
  }
}

const statusCodes: Record<number, AgentErrorCode> = {
  400: "bad_request", 401: "auth_expired", 403: "auth_expired", 404: "not_found",
  409: "conflict", 413: "too_large", 422: "validation",
};

export function normalizeHttpError(status: number): AgentApiError {
  return new AgentApiError(statusCodes[status] ?? "server", status);
}

export function normalizeRequestError(error: unknown): AgentApiError {
  if (error instanceof AgentApiError) return error;
  if (error instanceof DOMException && error.name === "AbortError") return new AgentApiError("aborted");
  return new AgentApiError("network");
}

