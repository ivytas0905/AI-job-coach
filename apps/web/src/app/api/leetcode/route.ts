const query = `query problemsetQuestionList($limit: Int, $filters: QuestionListFilterInput) {
  problemsetQuestionList(categorySlug: "", limit: $limit, skip: 0, filters: $filters) {
    questions: data { questionFrontendId title titleSlug difficulty }
  }
}`;

const allowed = new Set(["EASY", "MEDIUM", "HARD"]);

export async function POST(request: Request) {
  let body: unknown;
  try { body = await request.json(); } catch { return Response.json({ error: "Invalid request" }, { status: 400 }); }
  const input = body as { difficulty?: unknown; count?: unknown };
  const difficulty = typeof input.difficulty === "string" ? input.difficulty.toUpperCase() : "";
  const count = typeof input.count === "number" ? input.count : Number.NaN;
  if (!allowed.has(difficulty) || !Number.isInteger(count) || count < 1 || count > 5) return Response.json({ error: "Difficulty or count is invalid" }, { status: 400 });
  try {
    const response = await fetch("https://leetcode.com/graphql/", { method: "POST", headers: { "Content-Type": "application/json", "User-Agent": "AI-Job-Coach/1.0" }, body: JSON.stringify({ query, variables: { limit: 50, filters: { difficulty } } }), signal: AbortSignal.timeout(8000) });
    if (!response.ok) throw new Error("Upstream failed");
    const payload = await response.json() as { data?: { problemsetQuestionList?: { questions?: Array<Record<string, unknown>> } } };
    const questions = payload.data?.problemsetQuestionList?.questions;
    if (!Array.isArray(questions)) throw new Error("Malformed response");
    const normalized = questions.map((item) => ({ questionId: String(item.questionFrontendId ?? ""), title: String(item.title ?? ""), titleSlug: String(item.titleSlug ?? ""), difficulty: String(item.difficulty ?? "") })).filter((item) => item.questionId && item.title && item.titleSlug);
    return Response.json(normalized.sort(() => Math.random() - 0.5).slice(0, count));
  } catch { return Response.json({ error: "Failed to fetch problems" }, { status: 502 }); }
}
