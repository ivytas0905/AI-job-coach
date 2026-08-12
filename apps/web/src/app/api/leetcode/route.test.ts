import { POST } from "./route";

describe("LeetCode route", () => {
  it("rejects invalid preferences without calling upstream", async () => {
    const fetcher = vi.spyOn(globalThis, "fetch");
    const response = await POST(new Request("http://local/api/leetcode", { method: "POST", body: JSON.stringify({ difficulty: "Impossible", count: 100 }) }));
    expect(response.status).toBe(400);
    expect(fetcher).not.toHaveBeenCalled();
  });

  it("returns a bounded normalized problem list", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({ data: { problemsetQuestionList: { questions: [
      { questionFrontendId: "1", title: "Two Sum", titleSlug: "two-sum", difficulty: "Easy" },
      { questionFrontendId: "2", title: "Add Two", titleSlug: "add-two", difficulty: "Easy" },
    ] } } }), { status: 200 }));
    const response = await POST(new Request("http://local/api/leetcode", { method: "POST", body: JSON.stringify({ difficulty: "easy", count: 1 }) }));
    const data = await response.json();
    expect(data).toHaveLength(1);
    expect(data[0]).toEqual(expect.objectContaining({ questionId: expect.any(String), titleSlug: expect.any(String) }));
  });
});
