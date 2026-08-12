import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "jest-axe";
import type { RunSnapshot } from "@/types/agent";
import { ArtifactWorkspace, type ArtifactActions } from "./artifact-workspace";

const snapshot: RunSnapshot = {
  run: { id: "run-1", state: "proposal_ready", revision: 3, provider: "deepseek", model: "chat", current_version_id: "version-1", created_at: "2026-08-12T08:00:00Z" },
  resume: { id: "resume-1", filename: "resume.pdf", parsed_data: { name: "Lin", skills: ["React", "Python"] } },
  job_description: { id: "jd-1", raw_text: "Senior frontend engineer role", analysis: { keywords: ["React"] } },
  messages: [], decisions: [], latest_event_sequence: 4,
  proposals: [{ id: "proposal-1", revision: 2, status: "pending", affected_content: "Built a product", suggested_replacement: "Built a product used by 5 teams", jd_reason: "Shows measurable impact", source_evidence: { source: "resume", line: 4 }, evidence_request: "Please confirm the team count", created_at: "2026-08-12T08:01:00Z" }],
  versions: [{ id: "version-1", version_number: 1, version_name: "Frontend version", parent_version_id: null, content: { summary: "Frontend engineer", experience: [{ company: "Acme", bullets: ["Built a product"] }] }, created_at: "2026-08-12T08:02:00Z" }],
  exports: [],
};

function actions(overrides: Partial<ArtifactActions> = {}): ArtifactActions {
  return {
    submitResume: vi.fn(), submitJobDescription: vi.fn(),
    decideProposal: vi.fn(), restoreVersion: vi.fn(), createExport: vi.fn(), downloadExport: vi.fn(),
    ...overrides,
  };
}

describe("ArtifactWorkspace", () => {
  it("renders source material and validates uploads before sending", async () => {
    const api = actions();
    const user = userEvent.setup();
    render(<ArtifactWorkspace snapshot={snapshot} actions={api} />);
    await user.click(screen.getByRole("tab", { name: "材料" }));
    expect(screen.getByText("resume.pdf")).toBeInTheDocument();
    const input = screen.getByLabelText("上传简历文件");
    fireEvent.change(input, { target: { files: [new File(["text"], "resume.txt", { type: "text/plain" })] } });
    expect(screen.getByRole("alert")).toHaveTextContent("PDF 或 DOCX");
    expect(api.submitResume).not.toHaveBeenCalled();
  });

  it("shows grounded proposal details and sends one guarded decision", async () => {
    const decideProposal = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(<ArtifactWorkspace snapshot={snapshot} actions={actions({ decideProposal })} />);
    await user.click(screen.getByRole("tab", { name: /修改建议/ }));
    expect(screen.getByText("Built a product")).toBeInTheDocument();
    expect(screen.getByText("Built a product used by 5 teams")).toBeInTheDocument();
    expect(screen.getByText("Shows measurable impact")).toBeInTheDocument();
    expect(screen.getByText(/confirm the team count/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "接受这条建议" }));
    expect(decideProposal).toHaveBeenCalledWith("proposal-1", "accepted", 2, expect.any(String));
  });

  it("renders structured preview as inert text and exposes restore and export", async () => {
    const restoreVersion = vi.fn().mockResolvedValue(undefined);
    const createExport = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();
    const unsafe = { ...snapshot, run: { ...snapshot.run, current_version_id: null }, versions: [{ ...snapshot.versions[0], content: { summary: "<script>alert(1)</script>" } }] };
    const { container } = render(<ArtifactWorkspace snapshot={unsafe} actions={actions({ restoreVersion, createExport })} />);
    await user.click(screen.getByRole("tab", { name: /预览/ }));
    expect(screen.getByText("<script>alert(1)</script>")).toBeInTheDocument();
    expect(container.querySelector("script")).toBeNull();
    await user.click(screen.getByRole("tab", { name: /版本与导出/ }));
    await user.click(screen.getByRole("button", { name: /恢复 Frontend version/ }));
    expect(restoreVersion).toHaveBeenCalledWith("version-1", expect.any(String));
    await user.click(screen.getByRole("button", { name: "导出 PDF" }));
    expect(createExport).toHaveBeenCalledWith("version-1", "pdf", expect.any(String));
    expect((await axe(container)).violations).toEqual([]);
  });
});
