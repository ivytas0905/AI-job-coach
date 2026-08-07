import { act, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Composer } from "./composer";

describe("Composer", () => {
  it("sends trimmed content with Enter and keeps Shift+Enter as a newline", async () => {
    const send = vi.fn(async () => undefined);
    render(<Composer onSend={send} />);
    const input = screen.getByRole("textbox", { name: "给求职教练发送消息" });
    await userEvent.type(input, "第一行{shift>}{enter}{/shift}第二行");
    expect(send).not.toHaveBeenCalled();
    await userEvent.keyboard("{Enter}");
    expect(send).toHaveBeenCalledWith("第一行\n第二行");
    expect(input).toHaveValue("");
  });

  it("does not submit blank, composing, or duplicate in-flight messages", async () => {
    let resolve!: () => void;
    const send = vi.fn(() => new Promise<void>((done) => { resolve = done; }));
    render(<Composer onSend={send} />);
    const input = screen.getByRole("textbox");
    fireEvent.keyDown(input, { key: "Enter" });
    expect(send).not.toHaveBeenCalled();
    await userEvent.type(input, "内容");
    fireEvent.keyDown(input, { key: "Enter", isComposing: true });
    expect(send).not.toHaveBeenCalled();
    fireEvent.keyDown(input, { key: "Enter" });
    fireEvent.keyDown(input, { key: "Enter" });
    expect(send).toHaveBeenCalledTimes(1);
    await act(async () => resolve());
  });
});
