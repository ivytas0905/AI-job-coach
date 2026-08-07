import { render, screen } from "@testing-library/react";
import type { RunSummary } from "@/types/agent";
import { RunHistory } from "./run-history";

const run = (id: string, state: RunSummary["state"]): RunSummary => ({ id, state, revision: 1, provider: "test", model: "test", current_version_id: null, created_at: "2026-08-07T08:00:00Z" });

describe("RunHistory", () => {
  it("labels untitled runs with time and workflow state", () => {
    render(<RunHistory runs={[run("one", "proposal_ready"), run("two", "completed")]} selectedId="one" />);
    expect(screen.getByRole("link", { name: /简历优化.*建议待确认/ })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: /简历优化.*已完成/ })).toHaveAttribute("href", "/dashboard/resume/agent/two");
  });

  it("shows a useful empty state", () => {
    render(<RunHistory runs={[]} />);
    expect(screen.getByText(/还没有对话/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "新建对话" })).toBeInTheDocument();
  });
});
