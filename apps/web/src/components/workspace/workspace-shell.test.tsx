import { render, screen } from "@testing-library/react";
import { axe } from "jest-axe";
import { WorkspaceShell } from "./workspace-shell";

describe("WorkspaceShell", () => {
  it("exposes three semantic workspace regions and narrow-screen drawer triggers", async () => {
    const { container } = render(<WorkspaceShell history={<p>历史内容</p>} conversation={<h1>对话内容</h1>} artifacts={<p>材料内容</p>} />);
    expect(screen.getByRole("main", { name: "求职教练对话" })).toBeInTheDocument();
    expect(screen.getByRole("complementary", { name: "简历材料工作区" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "历史" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "材料" })).toBeInTheDocument();
    expect((await axe(container)).violations).toEqual([]);
  });
});
