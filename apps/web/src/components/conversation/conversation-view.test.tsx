import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { RunSnapshot } from "@/types/agent";
import { ConversationView } from "./conversation-view";

const snapshot: RunSnapshot = {
  run: { id: "run", state: "analyzing", revision: 1, provider: "deepseek", model: "chat", current_version_id: null, created_at: "2026-08-12T00:00:00Z" },
  resume: null, job_description: null, proposals: [], decisions: [], versions: [], exports: [], latest_event_sequence: 1,
  messages: [{ id: "m1", sequence: 1, role: "assistant", content: "First", created_at: "2026-08-12T00:00:00Z" }],
};

describe("ConversationView", () => {
  it("shows a localized processing state and conflict recovery notice", () => {
    render(<ConversationView snapshot={snapshot} status="conflict" onSend={vi.fn()} />);
    expect(screen.getByRole("status")).toHaveTextContent("已同步最新内容");
    expect(screen.queryByText("analyzing")).not.toBeInTheDocument();
  });

  it("offers sign-in recovery without discarding the composer", () => {
    render(<ConversationView snapshot={snapshot} status="auth-expired" onSend={vi.fn()} signInHref="/sign-in?redirect_url=%2Fagent%2Frun" />);
    expect(screen.getByRole("link", { name: "重新登录" })).toHaveAttribute("href", "/sign-in?redirect_url=%2Fagent%2Frun");
  });

  it("shows jump to latest when the reader is away from the end", async () => {
    const user = userEvent.setup();
    render(<ConversationView snapshot={{ ...snapshot, messages: [...snapshot.messages, { id: "m2", sequence: 2, role: "user", content: "Latest", created_at: "2026-08-12T00:01:00Z" }] }} status="ready" onSend={vi.fn()} />);
    const scroller = screen.getByTestId("message-scroll");
    Object.defineProperties(scroller, { scrollHeight: { value: 1000 }, clientHeight: { value: 300 }, scrollTop: { value: 0, writable: true } });
    fireEvent.scroll(scroller);
    await user.click(screen.getByRole("button", { name: "跳到最新消息" }));
    expect(scroller.scrollTop).toBe(1000);
  });
});
