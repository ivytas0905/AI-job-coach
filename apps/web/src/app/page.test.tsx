import { render, screen } from "@testing-library/react";
import HomePage from "./page";

vi.mock("next/link", () => ({ default: ({ children, href, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement>) => <a href={String(href)} {...props}>{children}</a> }));

test("offers the conversational resume workspace as the primary action", () => {
  render(<HomePage />);
  expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("求职经历");
  expect(screen.getByRole("link", { name: "开始对话" })).toHaveAttribute("href", "/dashboard/resume/agent");
});
