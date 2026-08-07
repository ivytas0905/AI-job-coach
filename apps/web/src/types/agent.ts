export type WorkflowState =
  | "awaiting_resume"
  | "awaiting_jd"
  | "analyzing"
  | "proposal_ready"
  | "applying"
  | "version_ready"
  | "exporting"
  | "completed"
  | "failed";

export interface RunSummary {
  id: string;
  state: WorkflowState;
  revision: number;
  provider: string;
  model: string;
  current_version_id: string | null;
  created_at: string;
}

export interface ResourceRecord { id: string; created_at: string }
export interface MessageRecord extends ResourceRecord { sequence: number; role: string; content: string }
export interface ProposalRecord extends ResourceRecord {
  revision: number; status: string; affected_content: string;
  suggested_replacement: string; jd_reason: string;
  source_evidence: Record<string, unknown>; evidence_request: string | null;
}
export interface DecisionRecord extends ResourceRecord {
  proposal_id: string; proposal_revision: number; decision: string; version_id: string | null;
}
export interface VersionRecord extends ResourceRecord {
  version_number: number; version_name: string; parent_version_id: string | null;
  content: Record<string, unknown>;
}
export interface ExportRecord extends ResourceRecord {
  version_id: string; content_type: string; size_bytes: number;
}
export interface ResumeSource { id: string; filename: string; parsed_data: Record<string, unknown> }
export interface JobDescriptionSource { id: string; raw_text: string; analysis: Record<string, unknown> }
export interface RunSnapshot {
  run: RunSummary; resume: ResumeSource | null; job_description: JobDescriptionSource | null;
  messages: MessageRecord[]; proposals: ProposalRecord[]; decisions: DecisionRecord[];
  versions: VersionRecord[]; exports: ExportRecord[]; latest_event_sequence: number;
}
export interface RunList { items: RunSummary[]; next_cursor: string | null }
export type ProposalDecision = "accepted" | "rejected" | "revision_requested";
export type ExportFormat = "pdf" | "docx";

